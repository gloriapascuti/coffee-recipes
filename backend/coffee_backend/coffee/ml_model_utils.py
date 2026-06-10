import os
import joblib
from django.conf import settings
from datetime import date


_model_cache = {
    'model': None,
    'scaler': None,
    'encoders': None,
    'feature_names': None,
    'optimal_threshold': None,
}


RISK_LOW_MAX = 0.05
RISK_MODERATE_MAX = 0.15
DEFAULT_OPTIMAL_THRESHOLD = 0.15


def clear_model_cache():
    """Clear the model cache to force reloading."""
    global _model_cache
    _model_cache = {
        'model': None,
        'scaler': None,
        'encoders': None,
        'feature_names': None,
        'optimal_threshold': None,
    }
    import logging
    logger = logging.getLogger(__name__)
    logger.info("Model cache cleared - will reload on next prediction")


def get_model_path():
    """Get the path to the ML model directory."""
    model_dir = getattr(settings, 'ML_MODEL_DIR', None)
    if model_dir is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        model_dir = os.path.join(base_dir, 'ml_models')
    return model_dir


def load_model_components():
    """
    Load the trained ML model and preprocessing components.
    Uses caching to avoid reloading on every request.
    """
    if _model_cache['model'] is not None:
        return _model_cache

    model_dir = get_model_path()

    try:
        model_path = os.path.join(model_dir, 'heart_disease_model.pkl')
        model = joblib.load(model_path)
        _model_cache['model'] = model

        scaler_path = os.path.join(model_dir, 'scaler.pkl')
        scaler = joblib.load(scaler_path)
        _model_cache['scaler'] = scaler

        encoders_path = os.path.join(model_dir, 'encoders.pkl')
        encoders = joblib.load(encoders_path)
        _model_cache['encoders'] = encoders

        feature_names_path = os.path.join(model_dir, 'feature_names.pkl')
        feature_names = joblib.load(feature_names_path)
        _model_cache['feature_names'] = feature_names

        threshold_path = os.path.join(model_dir, 'optimal_threshold.txt')
        if os.path.exists(threshold_path):
            with open(threshold_path) as f:
                _model_cache['optimal_threshold'] = float(f.read().strip())
        else:
            _model_cache['optimal_threshold'] = DEFAULT_OPTIMAL_THRESHOLD

        from sklearn.ensemble import VotingClassifier
        if isinstance(model, VotingClassifier):
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"Loaded ensemble model (VotingClassifier) with {len(model.estimators_)} estimators")

        return _model_cache
    except FileNotFoundError as e:
        raise FileNotFoundError(
            f"ML model files not found in {model_dir}. "
            "Please train the model first using thesis_model/trained_model.py"
        ) from e
    except Exception as e:
        raise RuntimeError(f"Error loading ML model: {str(e)}") from e


def prepare_features(health_profile, bp_entry, avg_daily_caffeine, total_caffeine_week, period_days):
    """
    Prepare feature vector from user data for model prediction.
    Args:
        health_profile: UserHealthProfile instance
        bp_entry: Dict with 'systolic' and 'diastolic' keys, or None
        avg_daily_caffeine: Average daily caffeine intake in mg
        total_caffeine_week: Total caffeine for the period in mg
        period_days: Number of days in the period
    Returns:
        numpy array of features ready for model prediction
    """
    import numpy as np

    components = load_model_components()
    encoders = components['encoders']

    age = None
    if health_profile and health_profile.date_of_birth:
        today = date.today()
        age = today.year - health_profile.date_of_birth.year
        if (today.month, today.day) < (health_profile.date_of_birth.month, health_profile.date_of_birth.day):
            age -= 1

    if age is None:
        age = 45

    sex = health_profile.sex if health_profile and health_profile.sex else 'M'
    if sex not in ['M', 'F']:
        sex = 'M'

    sex_encoded = 1 if sex == 'M' else 0

    bmi = None
    if health_profile:
        bmi = health_profile.bmi
    if bmi is None:
        bmi = 25.0

    systolic_bp = bp_entry.get('systolic') if bp_entry else None
    diastolic_bp = bp_entry.get('diastolic') if bp_entry else None

    if systolic_bp is None:
        systolic_bp = 120.0
    if diastolic_bp is None:
        diastolic_bp = 80.0

    has_hypertension = 1 if (health_profile and health_profile.has_hypertension) else 0
    has_diabetes = 1 if (health_profile and health_profile.has_diabetes) else 0
    has_family_history_chd = 1 if (health_profile and health_profile.has_family_history_chd) else 0
    is_smoker = 1 if (health_profile and health_profile.is_smoker) else 0

    activity_level = health_profile.activity_level if health_profile and health_profile.activity_level else 'sedentary'

    activity_level_encoded = 0

    if period_days > 0:
        total_caffeine_week_mg = total_caffeine_week * (7 / period_days) if period_days != 7 else total_caffeine_week
    else:
        total_caffeine_week_mg = 0

    avg_daily_caffeine_mg = max(0, avg_daily_caffeine)

    has_high_cholesterol = 1 if (health_profile and health_profile.has_high_cholesterol) else 0
    total_cholesterol = 200.0
    hdl_cholesterol = 50.0
    ldl_cholesterol = 120.0
    triglycerides = 150.0
    glucose = 95.0

    weight_kg = bmi * (1.70 ** 2)

    caffeine_per_kg = avg_daily_caffeine_mg / weight_kg
    caffeine_per_kg = min(caffeine_per_kg, 20.0)

    caffeine_per_bmi = avg_daily_caffeine_mg / bmi
    caffeine_per_bmi = min(caffeine_per_bmi, 100.0)

    if avg_daily_caffeine_mg <= 50:
        caffeine_category = 0
    elif avg_daily_caffeine_mg <= 200:
        caffeine_category = 1
    elif avg_daily_caffeine_mg <= 400:
        caffeine_category = 2
    elif avg_daily_caffeine_mg <= 600:
        caffeine_category = 3
    else:
        caffeine_category = 4

    caffeine_age_interaction = (avg_daily_caffeine_mg * age) / 1000.0
    caffeine_hypertension_interaction = avg_daily_caffeine_mg * has_hypertension
    is_high_caffeine = 1 if avg_daily_caffeine_mg > 400 else 0

    features = np.array([[
        age,
        sex_encoded,
        bmi,
        avg_daily_caffeine_mg,
        total_caffeine_week_mg,
        systolic_bp,
        diastolic_bp,
        has_hypertension,
        has_diabetes,
        has_family_history_chd,
        is_smoker,
        activity_level_encoded,
        has_high_cholesterol,
        total_cholesterol,
        hdl_cholesterol,
        ldl_cholesterol,
        triglycerides,
        glucose,
        caffeine_per_kg,
        caffeine_per_bmi,
        caffeine_category,
        caffeine_age_interaction,
        caffeine_hypertension_interaction,
        is_high_caffeine
    ]])

    return features


def predict_heart_disease_risk(health_profile, bp_entry, avg_daily_caffeine, total_caffeine_week, period_days):
    """
    Predict heart disease risk using the trained ML model.
    Args:
        health_profile: UserHealthProfile instance (can be None)
        bp_entry: Dict with 'systolic' and 'diastolic' keys, or None
        avg_daily_caffeine: Average daily caffeine intake in mg
        total_caffeine_week: Total caffeine for the period in mg
        period_days: Number of days in the period
    Returns:
        dict with:
            - risk_probability: float (0-1)
            - risk_percentage: float (0-100)
            - risk_category: str ('low', 'moderate', 'high')
    """
    try:
        components = load_model_components()
        model = components['model']
        scaler = components['scaler']
        feature_names = components['feature_names']

        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Model expects {len(feature_names)} features: {feature_names}")

        features = prepare_features(
            health_profile, bp_entry, avg_daily_caffeine,
            total_caffeine_week, period_days
        )

        logger.info(f"Prepared features shape: {features.shape}")

        if features.shape[1] != len(feature_names):
            error_msg = f"Feature mismatch! Model expects {len(feature_names)} features but got {features.shape[1]}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        features_scaled = scaler.transform(features)

        risk_probability = float(model.predict_proba(features_scaled)[0][1])
        risk_percentage = risk_probability * 100

        if risk_probability < RISK_LOW_MAX:
            risk_category = 'low'
        elif risk_probability < RISK_MODERATE_MAX:
            risk_category = 'moderate'
        else:
            risk_category = 'high'

        logger.info(f"risk={risk_probability:.4f}  category={risk_category}")

        return {
            'risk_probability': float(risk_probability),
            'risk_percentage': round(risk_percentage, 2),
            'risk_category': risk_category
        }

    except Exception as e:
        import logging
        import traceback
        logger = logging.getLogger(__name__)
        error_msg = f"ML model prediction failed: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_msg)
        print(f"ERROR in predict_heart_disease_risk: {error_msg}")

        return {
            'risk_probability': 0.07,
            'risk_percentage': 7.0,
            'risk_category': 'moderate'
        }
