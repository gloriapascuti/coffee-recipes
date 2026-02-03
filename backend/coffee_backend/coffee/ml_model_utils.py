"""
Utility module for loading and using the trained ML model for heart disease risk prediction.
"""
import os
import joblib
from django.conf import settings
from datetime import date


# Cache for loaded model components
_model_cache = {
    'model': None,
    'scaler': None,
    'encoders': None,
    'feature_names': None
}


def get_model_path():
    """Get the path to the ML model directory."""
    # Try to get from settings, otherwise use default location
    model_dir = getattr(settings, 'ML_MODEL_DIR', None)
    if model_dir is None:
        # Default to ml_models directory in the coffee app
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        model_dir = os.path.join(base_dir, 'ml_models')
    return model_dir


def load_model_components():
    """
    Load the trained ML model and preprocessing components.
    Uses caching to avoid reloading on every request.
    """
    # Return cached components if already loaded
    if _model_cache['model'] is not None:
        return _model_cache
    
    model_dir = get_model_path()
    
    try:
        # Load model
        model_path = os.path.join(model_dir, 'heart_disease_model.pkl')
        _model_cache['model'] = joblib.load(model_path)
        
        # Load scaler
        scaler_path = os.path.join(model_dir, 'scaler.pkl')
        _model_cache['scaler'] = joblib.load(scaler_path)
        
        # Load encoders
        encoders_path = os.path.join(model_dir, 'encoders.pkl')
        _model_cache['encoders'] = joblib.load(encoders_path)
        
        # Load feature names
        feature_names_path = os.path.join(model_dir, 'feature_names.pkl')
        _model_cache['feature_names'] = joblib.load(feature_names_path)
        
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
    
    # Load model components to get encoders
    components = load_model_components()
    encoders = components['encoders']
    
    # Calculate age
    age = None
    if health_profile and health_profile.date_of_birth:
        today = date.today()
        age = today.year - health_profile.date_of_birth.year
        if (today.month, today.day) < (health_profile.date_of_birth.month, health_profile.date_of_birth.day):
            age -= 1
    
    # Default age if not available (use median age)
    if age is None:
        age = 45
    
    # Encode sex
    sex = health_profile.sex if health_profile and health_profile.sex else 'M'
    if sex not in ['M', 'F']:
        sex = 'M'  # Default to M if Other or None
    sex_encoded = encoders['sex'].transform([sex])[0]
    
    # Calculate BMI
    bmi = None
    if health_profile:
        bmi = health_profile.bmi
    if bmi is None:
        bmi = 25.0  # Default BMI
    
    # Blood pressure
    systolic_bp = bp_entry.get('systolic') if bp_entry else None
    diastolic_bp = bp_entry.get('diastolic') if bp_entry else None
    
    if systolic_bp is None:
        systolic_bp = 120.0  # Default normal BP
    if diastolic_bp is None:
        diastolic_bp = 80.0  # Default normal BP
    
    # Health conditions (binary)
    has_hypertension = 1 if (health_profile and health_profile.has_hypertension) else 0
    has_diabetes = 1 if (health_profile and health_profile.has_diabetes) else 0
    has_family_history_chd = 1 if (health_profile and health_profile.has_family_history_chd) else 0
    is_smoker = 1 if (health_profile and health_profile.is_smoker) else 0
    
    # Activity level
    activity_level = health_profile.activity_level if health_profile and health_profile.activity_level else 'sedentary'
    # Map activity levels to valid choices (encoder only has: 'active', 'light', 'moderate', 'sedentary')
    valid_activities = ['sedentary', 'light', 'moderate', 'active']
    if activity_level == 'very_active':
        activity_level = 'active'  # Map very_active to active
    elif activity_level not in valid_activities:
        activity_level = 'sedentary'  # Default to sedentary if unknown
    activity_level_encoded = encoders['activity_level'].transform([activity_level])[0]
    
    # Caffeine features
    # Use total_caffeine_week for the period, but calculate weekly average
    if period_days > 0:
        total_caffeine_week_mg = total_caffeine_week * (7 / period_days) if period_days != 7 else total_caffeine_week
    else:
        total_caffeine_week_mg = 0
    
    # Ensure avg_daily_caffeine is not negative
    avg_daily_caffeine_mg = max(0, avg_daily_caffeine)
    
    # Build feature vector in the exact order expected by the model
    # Based on feature_cols from train_model.py:
    # ['age', 'sex_encoded', 'bmi', 'avg_daily_caffeine_mg', 'total_caffeine_week_mg',
    #  'systolic_bp', 'diastolic_bp', 'has_hypertension', 'has_diabetes', 
    #  'has_family_history_chd', 'is_smoker', 'activity_level_encoded']
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
        # Load model components
        components = load_model_components()
        model = components['model']
        scaler = components['scaler']
        
        # Prepare features
        features = prepare_features(
            health_profile, bp_entry, avg_daily_caffeine, 
            total_caffeine_week, period_days
        )
        
        # Scale features
        features_scaled = scaler.transform(features)
        
        # Predict probability
        raw_probability = model.predict_proba(features_scaled)[0][1]  # Probability of class 1 (high risk)
        
        # Calibrate the probability to a more realistic risk percentage
        # The model outputs probability of being in "high risk" class, but we want a continuous risk score
        # Use a calibration function to map model probability to realistic risk percentage
        # This prevents over-prediction of risk
        
        # Calibration: scale and transform the probability
        # For low probabilities (<0.3), scale more conservatively
        # For higher probabilities, use more direct mapping
        if raw_probability < 0.1:
            # Very low risk - scale down further
            risk_probability = raw_probability * 0.3  # Scale down by 70%
        elif raw_probability < 0.3:
            # Low-moderate risk - scale down moderately
            risk_probability = 0.03 + (raw_probability - 0.1) * 0.35  # Map 0.1-0.3 to 0.03-0.10
        elif raw_probability < 0.6:
            # Moderate risk - use more direct mapping
            risk_probability = 0.10 + (raw_probability - 0.3) * 0.40  # Map 0.3-0.6 to 0.10-0.22
        else:
            # Higher risk - use direct mapping but cap at reasonable maximum
            risk_probability = 0.22 + (raw_probability - 0.6) * 0.45  # Map 0.6-1.0 to 0.22-0.40
        
        # Ensure risk is between 0 and 1
        risk_probability = max(0.0, min(1.0, risk_probability))
        
        # Convert to percentage
        risk_percentage = risk_probability * 100
        
        # Determine risk category based on calibrated probability
        if risk_probability < 0.15:
            risk_category = 'low'
        elif risk_probability < 0.30:
            risk_category = 'moderate'
        else:
            risk_category = 'high'
        
        return {
            'risk_probability': float(risk_probability),
            'risk_percentage': round(risk_percentage, 1),
            'risk_category': risk_category
        }
        
    except Exception as e:
        # Fallback to heuristic if model fails
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"ML model prediction failed: {str(e)}")
        
        # Return a default moderate risk
        return {
            'risk_probability': 0.3,
            'risk_percentage': 30.0,
            'risk_category': 'moderate'
        }
