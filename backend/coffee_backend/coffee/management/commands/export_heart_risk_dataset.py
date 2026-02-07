from django.core.management.base import BaseCommand
from django.utils import timezone

from coffee.models.health import UserHealthProfile, BloodPressureEntry
from coffee.models.coffee import ConsumedCoffee
from coffee.ml_model_utils import prepare_features

import csv
from datetime import timedelta


class Command(BaseCommand):
    """
    Export an anonymised dataset of user features for future model training.
    
    This does NOT include real diagnosis labels (we don't have them), but it
    gives you a CSV of the same features the model uses plus consumption
    stats so you can annotate or combine with clinical data later.
    """

    help = "Export anonymised heart risk features for all users to CSV."

    def add_arguments(self, parser):
        parser.add_argument(
            "--output",
            type=str,
            default="heart_risk_features.csv",
            help="Path to output CSV file (default: heart_risk_features.csv)",
        )
        parser.add_argument(
            "--period",
            type=str,
            choices=["week", "month", "year"],
            default="year",
            help="Period over which to aggregate caffeine consumption.",
        )

    def handle(self, *args, **options):
        output_path = options["output"]
        period = options["period"]

        self.stdout.write(f"Exporting heart risk features for period: {period}")

        now = timezone.now()
        if period == "week":
            start = now - timedelta(days=7)
            period_days = 7
        elif period == "month":
            start = now - timedelta(days=30)
            period_days = 30
        else:
            start = now - timedelta(days=365)
            period_days = 365

        # Open CSV for writing
        with open(output_path, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)

            # Header: user_id kept, but no username/email to keep it simple
            header = [
                "user_id",
                "period",
                "period_days",
                "avg_daily_caffeine_mg",
                "total_caffeine_period_mg",
            ]
            # Feature columns the model uses (see prepare_features)
            feature_cols = [
                "age",
                "sex_encoded",
                "bmi",
                "avg_daily_caffeine_mg",
                "total_caffeine_week_mg",
                "systolic_bp",
                "diastolic_bp",
                "has_hypertension",
                "has_diabetes",
                "has_family_history_chd",
                "is_smoker",
                "activity_level_encoded",
                # Additional structured family‑history info for future models
                "num_relatives_chd",
            ]

            writer.writerow(header + feature_cols)

            for profile in UserHealthProfile.objects.select_related("user"):
                user = profile.user

                # Caffeine stats over period
                consumed = (
                    ConsumedCoffee.objects.filter(
                        user=user, consumed_at__gte=start, consumed_at__lte=now
                    )
                    .select_related("coffee")
                    .order_by("-consumed_at")
                )
                if not consumed.exists():
                    continue

                total_caffeine = sum(
                    cc.coffee.get_caffeine_mg() for cc in consumed
                )
                avg_daily_caffeine = total_caffeine / float(period_days)

                # Latest BP if available
                latest_bp = (
                    BloodPressureEntry.objects.filter(user=user)
                    .order_by("-measured_at")
                    .first()
                )
                bp_entry = None
                if latest_bp:
                    bp_entry = {
                        "systolic": latest_bp.systolic,
                        "diastolic": latest_bp.diastolic,
                    }

                # Build feature vector exactly as the model sees it
                features = prepare_features(
                    health_profile=profile,
                    bp_entry=bp_entry,
                    avg_daily_caffeine=avg_daily_caffeine,
                    total_caffeine_week=total_caffeine,
                    period_days=period_days,
                )

                # features is shape (1, n)
                feature_row = list(map(float, features[0]))
                num_relatives = getattr(profile, "num_relatives_chd", 0) or 0

                writer.writerow(
                    [
                        user.id,
                        period,
                        period_days,
                        round(avg_daily_caffeine, 2),
                        round(total_caffeine, 2),
                    ]
                    + feature_row
                    + [num_relatives]
                )

        self.stdout.write(self.style.SUCCESS(f"Exported dataset to {output_path}"))

