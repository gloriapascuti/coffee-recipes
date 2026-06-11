import numpy as np
import pandas as pd
from scipy.stats import norm
from sklearn.linear_model import LogisticRegression


CLINICAL_POINTS = {
    "age_40_49":           1,
    "age_50_59":           2,
    "age_60_69":           3,
    "age_70_plus":         4,
    "hypertension":        3,
    "diabetes":            3,
    "smoker":              3,
    "high_cholesterol":    2,
    "family_history_chd":  2,
    "bmi_30_to_35":        1,
    "bmi_35_plus":         2,
    "bp_stage_1":          1,
    "bp_stage_2":          3,
    "bp_stage_3":          4,
}


def compute_clinical_score(features):
    score = 0

    age = float(features.get("age", 0))
    if   age >= 70: score += CLINICAL_POINTS["age_70_plus"]
    elif age >= 60: score += CLINICAL_POINTS["age_60_69"]
    elif age >= 50: score += CLINICAL_POINTS["age_50_59"]
    elif age >= 40: score += CLINICAL_POINTS["age_40_49"]

    if features.get("has_hypertension", 0):       score += CLINICAL_POINTS["hypertension"]
    if features.get("has_diabetes", 0):           score += CLINICAL_POINTS["diabetes"]
    if features.get("is_smoker", 0):              score += CLINICAL_POINTS["smoker"]
    if features.get("has_high_cholesterol", 0):   score += CLINICAL_POINTS["high_cholesterol"]
    if features.get("has_family_history_chd", 0): score += CLINICAL_POINTS["family_history_chd"]

    bmi = float(features.get("bmi", 25.0))
    if   bmi >= 35: score += CLINICAL_POINTS["bmi_35_plus"]
    elif bmi >= 30: score += CLINICAL_POINTS["bmi_30_to_35"]

    sbp = float(features.get("systolic_bp", 120.0))
    dbp = float(features.get("diastolic_bp", 80.0))
    if   sbp >= 160 or dbp >= 100: score += CLINICAL_POINTS["bp_stage_3"]
    elif sbp >= 140 or dbp >= 90:  score += CLINICAL_POINTS["bp_stage_2"]
    elif sbp >= 130 or dbp >= 85:  score += CLINICAL_POINTS["bp_stage_1"]

    return int(score)


def compute_clinical_scores_vectorized(X, feature_names):
    if not isinstance(X, pd.DataFrame):
        df = pd.DataFrame(X, columns=list(feature_names))
    else:
        df = X

    n = len(df)

    def col(name, default=0.0):
        return df[name].values if name in df.columns else np.full(n, default)

    score = np.zeros(n, dtype=int)

    age = col("age", 0.0)
    score += np.where(age >= 70, CLINICAL_POINTS["age_70_plus"],
             np.where(age >= 60, CLINICAL_POINTS["age_60_69"],
             np.where(age >= 50, CLINICAL_POINTS["age_50_59"],
             np.where(age >= 40, CLINICAL_POINTS["age_40_49"], 0))))

    score += CLINICAL_POINTS["hypertension"]      * col("has_hypertension").astype(int)
    score += CLINICAL_POINTS["diabetes"]          * col("has_diabetes").astype(int)
    score += CLINICAL_POINTS["smoker"]            * col("is_smoker").astype(int)
    score += CLINICAL_POINTS["high_cholesterol"]  * col("has_high_cholesterol").astype(int)
    score += CLINICAL_POINTS["family_history_chd"] * col("has_family_history_chd").astype(int)

    bmi = col("bmi", 25.0)
    score += np.where(bmi >= 35, CLINICAL_POINTS["bmi_35_plus"],
             np.where(bmi >= 30, CLINICAL_POINTS["bmi_30_to_35"], 0))

    sbp = col("systolic_bp", 120.0)
    dbp = col("diastolic_bp", 80.0)
    score += np.where((sbp >= 160) | (dbp >= 100), CLINICAL_POINTS["bp_stage_3"],
             np.where((sbp >= 140) | (dbp >= 90),  CLINICAL_POINTS["bp_stage_2"],
             np.where((sbp >= 130) | (dbp >= 85),  CLINICAL_POINTS["bp_stage_1"], 0)))

    return score


CAFFEINE_THRESHOLDS = (300.0, 400.0, 600.0)
CAFFEINE_BASE_SCORES = (0, 1, 3, 4)

LONGITUDINAL_THRESHOLD_MG = 400.0
LONGITUDINAL_180D_BONUS   = 1
LONGITUDINAL_365D_BONUS   = 2


def compute_caffeine_score(daily_mg, period_days=365):
    daily = float(daily_mg)
    if   daily <= CAFFEINE_THRESHOLDS[0]: s = CAFFEINE_BASE_SCORES[0]
    elif daily <= CAFFEINE_THRESHOLDS[1]: s = CAFFEINE_BASE_SCORES[1]
    elif daily <= CAFFEINE_THRESHOLDS[2]: s = CAFFEINE_BASE_SCORES[2]
    else:                                  s = CAFFEINE_BASE_SCORES[3]

    if daily > LONGITUDINAL_THRESHOLD_MG:
        if   period_days >= 365: s += LONGITUDINAL_365D_BONUS
        elif period_days >= 180: s += LONGITUDINAL_180D_BONUS

    return int(s)


def compute_caffeine_scores_vectorized(X, feature_names, period_days=365):
    if not isinstance(X, pd.DataFrame):
        df = pd.DataFrame(X, columns=list(feature_names))
    else:
        df = X

    daily = df["avg_daily_caffeine_mg"].values.astype(float)

    s = np.where(daily <= CAFFEINE_THRESHOLDS[0], CAFFEINE_BASE_SCORES[0],
        np.where(daily <= CAFFEINE_THRESHOLDS[1], CAFFEINE_BASE_SCORES[1],
        np.where(daily <= CAFFEINE_THRESHOLDS[2], CAFFEINE_BASE_SCORES[2],
                                                   CAFFEINE_BASE_SCORES[3]))).astype(int)

    if daily.size:
        high = daily > LONGITUDINAL_THRESHOLD_MG
        if   period_days >= 365: s = s + LONGITUDINAL_365D_BONUS * high
        elif period_days >= 180: s = s + LONGITUDINAL_180D_BONUS * high

    return s.astype(int)


class PlattCalibrator:

    EPS = 1e-7

    def __init__(self):
        self.lr = LogisticRegression(solver="lbfgs")
        self._fitted = False

    @staticmethod
    def _logit(p):
        p = np.clip(p, PlattCalibrator.EPS, 1.0 - PlattCalibrator.EPS)
        return np.log(p / (1.0 - p))

    def fit(self, probs_val, y_val):
        logits = self._logit(np.asarray(probs_val, dtype=float)).reshape(-1, 1)
        self.lr.fit(logits, np.asarray(y_val).astype(int))
        self._fitted = True
        return self

    def transform(self, probs):
        if not self._fitted:
            raise RuntimeError("PlattCalibrator must be fit before transform.")
        logits = self._logit(np.asarray(probs, dtype=float)).reshape(-1, 1)
        return self.lr.predict_proba(logits)[:, 1]

    @property
    def params(self):
        if not self._fitted:
            raise RuntimeError("PlattCalibrator must be fit before reading params.")
        A = float(self.lr.coef_[0, 0])
        B = float(self.lr.intercept_[0])
        return {"A": A, "B": B}


def apply_postprocessing(
    probs_raw,
    clinical_scores=None,
    caffeine_scores=None,
    clinical_weight=0.01,
    caffeine_weight=0.01,
    clip_range=(0.001, 0.999),
):
    p = np.asarray(probs_raw, dtype=float).copy()
    if clinical_scores is not None:
        p = p + clinical_weight * np.asarray(clinical_scores, dtype=float)
    if caffeine_scores is not None:
        p = p + caffeine_weight * np.asarray(caffeine_scores, dtype=float)
    return np.clip(p, clip_range[0], clip_range[1])


class LearnedPostProcessor:

    EPS = 1e-7

    def __init__(self, use_clinical=True, use_caffeine=True):
        self.use_clinical = bool(use_clinical)
        self.use_caffeine = bool(use_caffeine)
        self.lr = LogisticRegression(solver="lbfgs", C=1e6, max_iter=2000)
        self._fitted = False
        self._design = None
        self._y = None

    @staticmethod
    def _logit(p):
        p = np.clip(p, LearnedPostProcessor.EPS, 1.0 - LearnedPostProcessor.EPS)
        return np.log(p / (1.0 - p))

    @property
    def feature_names(self):
        names = ["logit(p_raw)"]
        if self.use_clinical:
            names.append("clinical_score")
        if self.use_caffeine:
            names.append("caffeine_score")
        return names

    def _design_matrix(self, p_raw, clinical_score, caffeine_score):
        cols = [self._logit(np.asarray(p_raw, dtype=float))]
        if self.use_clinical:
            if clinical_score is None:
                raise ValueError("clinical_score must be provided when use_clinical=True")
            cols.append(np.asarray(clinical_score, dtype=float))
        if self.use_caffeine:
            if caffeine_score is None:
                raise ValueError("caffeine_score must be provided when use_caffeine=True")
            cols.append(np.asarray(caffeine_score, dtype=float))
        return np.column_stack(cols)

    def fit(self, p_raw, clinical_score, caffeine_score, y):
        X = self._design_matrix(p_raw, clinical_score, caffeine_score)
        y = np.asarray(y).astype(int)
        self.lr.fit(X, y)
        self._design = X
        self._y = y
        self._fitted = True
        return self

    def transform(self, p_raw, clinical_score=None, caffeine_score=None):
        if not self._fitted:
            raise RuntimeError("LearnedPostProcessor must be fit before transform.")
        X = self._design_matrix(p_raw, clinical_score, caffeine_score)
        return self.lr.predict_proba(X)[:, 1]

    def _wald_stats(self):
        X = self._design
        n = X.shape[0]
        X_full = np.column_stack([np.ones(n), X])
        beta = np.concatenate([self.lr.intercept_, self.lr.coef_[0]])
        z = X_full @ beta
        p_hat = 1.0 / (1.0 + np.exp(-z))
        W = p_hat * (1.0 - p_hat)
        H = X_full.T @ (W[:, None] * X_full)
        try:
            cov = np.linalg.inv(H)
        except np.linalg.LinAlgError:
            cov = np.linalg.pinv(H)
        se = np.sqrt(np.maximum(np.diag(cov), 0.0))
        se_safe = np.where(se > 0, se, np.nan)
        z_score = beta / se_safe
        p_value = 2.0 * (1.0 - norm.cdf(np.abs(z_score)))
        return beta, se, z_score, p_value

    @property
    def coefficients(self):
        if not self._fitted:
            raise RuntimeError("LearnedPostProcessor must be fit before reading coefficients.")
        beta, se, z, p_value = self._wald_stats()
        names = ["intercept"] + self.feature_names
        return {
            name: {
                "beta":    float(beta[i]),
                "se":      float(se[i]),
                "z":       float(z[i])       if not np.isnan(z[i])       else None,
                "p_value": float(p_value[i]) if not np.isnan(p_value[i]) else None,
            }
            for i, name in enumerate(names)
        }

    def coefficients_dataframe(self):
        return pd.DataFrame([
            {"name": name, **stats}
            for name, stats in self.coefficients.items()
        ])

    def summary(self):
        coefs = self.coefficients
        lines = [
            f"  LearnedPostProcessor "
            f"(use_clinical={self.use_clinical}, use_caffeine={self.use_caffeine})",
            f"  {'name':<18} {'beta':>10} {'std err':>10} "
            f"{'z':>7} {'p-value':>10}",
            "  " + "-" * 60,
        ]
        for name, s in coefs.items():
            z_str = f"{s['z']:>7.2f}" if s["z"] is not None else "     --"
            p_str = (
                "  < 0.001" if (s["p_value"] is not None and s["p_value"] < 1e-3)
                else f"{s['p_value']:>10.4f}" if s["p_value"] is not None
                else "        --"
            )
            lines.append(
                f"  {name:<18} {s['beta']:>10.4f} {s['se']:>10.4f} {z_str} {p_str}"
            )
        return "\n".join(lines)
