import numpy as np
import pandas as pd
from sklearn.metrics import (
    confusion_matrix,
    f1_score,
    matthews_corrcoef,
    precision_score,
    recall_score,
    roc_auc_score,
)

from .postprocessing import (
    LearnedPostProcessor,
    apply_postprocessing,
    compute_caffeine_scores_vectorized,
    compute_clinical_scores_vectorized,
)


CONDITION_LABELS = (
    "A. Raw model",
    "B. + clinical scoring",
    "C. + clinical + caffeine scoring",
)


def _metrics_at_threshold(y_true, probs, threshold):
    y_pred = (probs >= threshold).astype(int)
    cm = confusion_matrix(y_true, y_pred)
    return {
        "roc_auc":   roc_auc_score(y_true, probs),
        "precision": precision_score(y_true, y_pred, zero_division=0),
        "recall":    recall_score(y_true, y_pred, zero_division=0),
        "f1":        f1_score(y_true, y_pred, zero_division=0),
        "mcc":       matthews_corrcoef(y_true, y_pred),
        "tn": int(cm[0, 0]),
        "fp": int(cm[0, 1]),
        "fn": int(cm[1, 0]),
        "tp": int(cm[1, 1]),
    }


def run_postprocessing_study(
    model,
    threshold,
    X_test_scaled,
    y_test,
    X_test_raw,
    feature_names,
    clinical_weight=0.01,
    caffeine_weight=0.01,
    caffeine_period_days=365,
):
    p_raw = model.predict_proba(X_test_scaled)[:, 1]

    clinical = compute_clinical_scores_vectorized(X_test_raw, feature_names)
    caffeine = compute_caffeine_scores_vectorized(
        X_test_raw, feature_names, period_days=caffeine_period_days,
    )

    conditions = {
        CONDITION_LABELS[0]: p_raw,
        CONDITION_LABELS[1]: apply_postprocessing(
            p_raw,
            clinical_scores=clinical,
            clinical_weight=clinical_weight,
        ),
        CONDITION_LABELS[2]: apply_postprocessing(
            p_raw,
            clinical_scores=clinical,
            caffeine_scores=caffeine,
            clinical_weight=clinical_weight,
            caffeine_weight=caffeine_weight,
        ),
    }

    print(f"\n{'Condition':<37} {'ROC-AUC':>8} {'F1':>8} "
          f"{'Recall':>8} {'Prec':>8} {'MCC':>8} {'TP':>6} {'FP':>6} "
          f"{'FN':>6} {'TN':>6}")
    print("-" * 110)

    rows = []
    for label, probs in conditions.items():
        m = _metrics_at_threshold(y_test, probs, threshold)
        rows.append({"condition": label, **m})
        print(f"{label:<37} {m['roc_auc']:>8.3f} {m['f1']:>8.3f} "
              f"{m['recall']:>8.3f} {m['precision']:>8.3f} {m['mcc']:>8.3f} "
              f"{m['tp']:>6d} {m['fp']:>6d} {m['fn']:>6d} {m['tn']:>6d}")

    for from_, to_ in [("A. Raw model", "B. + clinical scoring"),
                       ("A. Raw model", "C. + clinical + caffeine scoring"),
                       ("B. + clinical scoring", "C. + clinical + caffeine scoring")]:
        src = next(r for r in rows if r["condition"] == from_)
        dst = next(r for r in rows if r["condition"] == to_)
        print(f"  delta {from_!r:<40} -> {to_!r:<40}: "
              f"F1 {dst['f1']-src['f1']:+.3f}, "
              f"Recall {dst['recall']-src['recall']:+.3f}, "
              f"MCC {dst['mcc']-src['mcc']:+.3f}")

    return pd.DataFrame(rows)


LEARNED_CONDITION_LABELS = (
    "A. Raw model",
    "B. + clinical scoring",
    "C. + clinical + caffeine scoring",
)

DEFAULT_TAU_SWEEP = (0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50)


def _pick_threshold(y_val, probs_val, thresholds=DEFAULT_TAU_SWEEP):
    best = None
    for tau in thresholds:
        y_pred = (probs_val >= tau).astype(int)
        f1 = f1_score(y_val, y_pred, zero_division=0)
        mcc = matthews_corrcoef(y_val, y_pred)
        key = (f1, mcc)
        if best is None or key > best[0]:
            best = (key, tau)
    return float(best[1])


def run_learned_postprocessing_study(
    model,
    X_val_scaled, y_val, X_val_raw,
    X_test_scaled, y_test, X_test_raw,
    feature_names,
    caffeine_period_days=365,
    thresholds=DEFAULT_TAU_SWEEP,
):
    p_val_raw = model.predict_proba(X_val_scaled)[:, 1]
    p_test_raw = model.predict_proba(X_test_scaled)[:, 1]

    clin_val  = compute_clinical_scores_vectorized(X_val_raw,  feature_names)
    clin_test = compute_clinical_scores_vectorized(X_test_raw, feature_names)
    caff_val  = compute_caffeine_scores_vectorized(X_val_raw,  feature_names,
                                                   period_days=caffeine_period_days)
    caff_test = compute_caffeine_scores_vectorized(X_test_raw, feature_names,
                                                   period_days=caffeine_period_days)

    configs = [
        (LEARNED_CONDITION_LABELS[0], None),
        (LEARNED_CONDITION_LABELS[1], LearnedPostProcessor(use_clinical=True,  use_caffeine=False)),
        (LEARNED_CONDITION_LABELS[2], LearnedPostProcessor(use_clinical=True,  use_caffeine=True )),
    ]

    print(f"\n{'Condition':<40} {'tau*':>6} {'ROC-AUC':>8} {'F1':>8} "
          f"{'Recall':>8} {'Prec':>8} {'MCC':>8} "
          f"{'TP':>6} {'FP':>6} {'FN':>6} {'TN':>6}")
    print("-" * 120)

    metric_rows = []
    coef_rows = []
    for label, pp in configs:
        if pp is None:
            probs_val = p_val_raw
            probs_test = p_test_raw
        else:
            pp.fit(p_val_raw, clin_val, caff_val, y_val)
            probs_val  = pp.transform(p_val_raw,  clin_val,  caff_val)
            probs_test = pp.transform(p_test_raw, clin_test, caff_test)

        tau = _pick_threshold(y_val, probs_val, thresholds=thresholds)
        metrics = _metrics_at_threshold(y_test, probs_test, tau)
        row = {"condition": label, "tau_opt": tau, **metrics}
        metric_rows.append(row)
        print(f"{label:<40} {tau:>6.2f} "
              f"{metrics['roc_auc']:>8.3f} {metrics['f1']:>8.3f} "
              f"{metrics['recall']:>8.3f} {metrics['precision']:>8.3f} "
              f"{metrics['mcc']:>8.3f} "
              f"{metrics['tp']:>6d} {metrics['fp']:>6d} "
              f"{metrics['fn']:>6d} {metrics['tn']:>6d}")

        if pp is not None:
            print(pp.summary())
            for name, stats in pp.coefficients.items():
                coef_rows.append({"condition": label, "name": name, **stats})

    print("\nPairwise deltas vs. raw baseline:")
    src = metric_rows[0]
    for dst in metric_rows[1:]:
        print(f"  {dst['condition']:<40} "
              f"F1 {dst['f1']-src['f1']:+.3f}, "
              f"Recall {dst['recall']-src['recall']:+.3f}, "
              f"Prec {dst['precision']-src['precision']:+.3f}, "
              f"MCC {dst['mcc']-src['mcc']:+.3f}, "
              f"ROC-AUC {dst['roc_auc']-src['roc_auc']:+.3f}")

    return pd.DataFrame(metric_rows), pd.DataFrame(coef_rows)
