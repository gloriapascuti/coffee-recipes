"""
Utility module for loading and using the trained ML model for heart disease risk prediction.
"""
import os
import joblib
from django.conf import settings
from datetime import date


_model_cache = {
    'model': None,
    'scaler': None,
    'encoders': None,
    'feature_names': None
}


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

        from sklearn.ensemble import VotingClassifier
        if isinstance(model, VotingClassifier):
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"Loaded ensemble model (VotingClassifier) with {len(model.estimators_)} estimators")
        
        return _model_cache
    except FileNotFoundError as e:
        raise FileNotFoundError(
            f"ML model files not found in {model_dir}. "
            "Please train the model first using thesis_model/train_model.py"
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
    sex_encoded = encoders['sex'].transform([sex])[0]
    
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
    valid_activities = ['sedentary', 'light', 'moderate', 'active']
    if activity_level == 'very_active':
        activity_level = 'active'
    elif activity_level not in valid_activities:
        activity_level = 'sedentary'
    activity_level_encoded = encoders['activity_level'].transform([activity_level])[0]
    
    if period_days > 0:
        total_caffeine_week_mg = total_caffeine_week * (7 / period_days) if period_days != 7 else total_caffeine_week
    else:
        total_caffeine_week_mg = 0
    
    avg_daily_caffeine_mg = max(0, avg_daily_caffeine)
    
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
        activity_level_encoded
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
        
        features = prepare_features(
            health_profile, bp_entry, avg_daily_caffeine, 
            total_caffeine_week, period_days
        )
        
        features_scaled = scaler.transform(features)
        
        raw_probability = float(model.predict_proba(features_scaled)[0][1])
        
        # ------------------------------------------------------------------
        # Evidence‑informed post‑processing
        #
        # Clinical literature and guidelines (Framingham/ASCVD style scores
        # and large coffee meta‑analyses) agree on two key points:
        #   1) Major clinical factors (age, hypertension, diabetes, smoking,
        #      high cholesterol, family history) dominate absolute risk.
        #   2) Caffeine/coffee has a U‑shaped relationship: moderate
        #      intake (~1–3 cups/day) is neutral/possibly protective,
        #      while chronically high intake (>400 mg/day) can increase
        #      risk, especially with other risk factors.
        #
        # To make the model both intuitive and more realistic, we combine
        # the ML probability with transparent rule‑based adjustments using
        # the actual profile, blood pressure and caffeine pattern.
        # ------------------------------------------------------------------
        
        avg_daily_caffeine_mg = max(0.0, float(avg_daily_caffeine or 0.0))
        period_days = max(1, int(period_days or 1))
        
        clinical_score = 0
        
        if health_profile:
            age = health_profile.age or 0
            bmi = health_profile.bmi or 0
            num_relatives = getattr(health_profile, "num_relatives_chd", 0) or 0
            
            if age >= 70:
                clinical_score += 4
            elif age >= 60:
                clinical_score += 3
            elif age >= 50:
                clinical_score += 2
            elif age >= 40:
                clinical_score += 1
            
            if getattr(health_profile, 'has_hypertension', False):
                clinical_score += 3
            if getattr(health_profile, 'has_diabetes', False):
                clinical_score += 3
            if getattr(health_profile, 'has_high_cholesterol', False):
                clinical_score += 2
            if getattr(health_profile, 'is_smoker', False):
                clinical_score += 3
            if getattr(health_profile, 'has_family_history_chd', False):
                # Base family‑history contribution
                clinical_score += 2
                # Additional weight for multiple affected relatives
                if num_relatives >= 2:
                    clinical_score += 1
            
            if bmi >= 35:
                clinical_score += 2
            elif bmi >= 30:
                clinical_score += 1
        
        systolic = None
        diastolic = None
        if bp_entry:
            systolic = bp_entry.get('systolic')
            diastolic = bp_entry.get('diastolic')
        elif health_profile and hasattr(health_profile, 'latest_bp'):
            latest = health_profile.latest_bp
            systolic = getattr(latest, 'systolic', None)
            diastolic = getattr(latest, 'diastolic', None)
        
        if systolic is not None and diastolic is not None:
            if systolic >= 160 or diastolic >= 100:
                clinical_score += 4
            elif systolic >= 140 or diastolic >= 90:
                clinical_score += 3
            elif systolic >= 130 or diastolic >= 85:
                clinical_score += 1
        
        caffeine_score = 0
        
        if avg_daily_caffeine_mg <= 100:
            caffeine_score += 0
        elif avg_daily_caffeine_mg <= 300:
            caffeine_score += 0
        elif avg_daily_caffeine_mg <= 400:
            caffeine_score += 1
        elif avg_daily_caffeine_mg <= 600:
            caffeine_score += 3
        else:
            caffeine_score += 4
        
        if period_days >= 180 and avg_daily_caffeine_mg > 400:
            caffeine_score += 1
        if period_days >= 365 and avg_daily_caffeine_mg > 400:
            caffeine_score += 1
        
        clinical_delta = clinical_score * 0.01
        period_factor = min(1.0, period_days / 365.0)
        caffeine_delta = caffeine_score * (0.01 + 0.02 * period_factor)
        
        adjusted_probability = raw_probability + clinical_delta + caffeine_delta
        
        adjusted_probability = max(0.01, min(0.95, adjusted_probability))
        
        # ------------------------------------------------------------------
        # Calibration: map probability to an interpretable range while
        # preserving *relative* differences between week/month/year.
        #
        # We now use a mostly linear mapping so that small changes in the
        # adjusted probability show up as different percentages, instead
        # of flattening everything at the top.
        # ------------------------------------------------------------------
        p = adjusted_probability
        risk_probability = 0.01 + 0.54 * p
        
        risk_probability = max(0.01, min(0.55, risk_probability))
        
        risk_percentage = risk_probability * 100
        
        if risk_probability < 0.15:
            risk_category = 'low'
        elif risk_probability < 0.30:
            risk_category = 'moderate'
        else:
            risk_category = 'high'
        
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
            'risk_probability': 0.3,
            'risk_percentage': 30.0,
            'risk_category': 'moderate'
        }
