#!/usr/bin/env python3
"""
Quick test to verify the model loads correctly and has the right number of features.
"""
import sys
import os

# Add the backend to Python path
backend_path = os.path.join(os.path.dirname(__file__), 'coffee_backend')
sys.path.insert(0, backend_path)

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'coffee_backend.settings')
import django
django.setup()

# Now test the model
from coffee.ml_model_utils import load_model_components, clear_model_cache

print("="*60)
print("Testing Model Feature Compatibility")
print("="*60)

# Clear cache to force fresh load
clear_model_cache()

# Load model
try:
    components = load_model_components()
    model = components['model']
    scaler = components['scaler']
    feature_names = components['feature_names']
    
    print(f"\n✓ Model loaded successfully!")
    print(f"✓ Model type: {type(model).__name__}")
    print(f"✓ Scaler type: {type(scaler).__name__}")
    print(f"\n✓ Model expects {len(feature_names)} features:")
    for i, feat in enumerate(feature_names, 1):
        print(f"  {i:2d}. {feat}")
    
    # Test with dummy data
    print(f"\n" + "="*60)
    print("Testing with dummy patient data")
    print("="*60)
    
    import numpy as np
    
    # Create dummy features (24 features)
    dummy_features = np.array([[
        45,      # age
        0,       # sex_encoded
        28.0,    # bmi
        250.0,   # avg_daily_caffeine_mg
        1750.0,  # total_caffeine_week_mg
        120.0,   # systolic_bp
        80.0,    # diastolic_bp
        0,       # has_hypertension
        0,       # has_diabetes
        0,       # has_family_history_chd
        0,       # is_smoker
        1,       # activity_level_encoded
        0,       # has_high_cholesterol
        200.0,   # total_cholesterol
        50.0,    # hdl_cholesterol
        120.0,   # ldl_cholesterol
        150.0,   # triglycerides
        95.0,    # glucose
        3.26,    # caffeine_per_kg
        8.93,    # caffeine_per_bmi
        2,       # caffeine_category
        11.25,   # caffeine_age_interaction
        0.0,     # caffeine_hypertension_interaction
        0        # is_high_caffeine
    ]])
    
    print(f"Dummy features shape: {dummy_features.shape}")
    
    if dummy_features.shape[1] != len(feature_names):
        print(f"\n❌ ERROR: Feature count mismatch!")
        print(f"   Model expects: {len(feature_names)}")
        print(f"   Provided: {dummy_features.shape[1]}")
        sys.exit(1)
    
    # Scale and predict
    features_scaled = scaler.transform(dummy_features)
    probability = model.predict_proba(features_scaled)[0][1]
    
    print(f"\n✓ Prediction successful!")
    print(f"  Raw probability: {probability:.4f} ({probability*100:.2f}%)")
    
    print(f"\n" + "="*60)
    print("✅ All tests passed! Model is working correctly.")
    print("="*60)
    
except Exception as e:
    import traceback
    print(f"\n❌ ERROR: {str(e)}")
    print(f"\nFull traceback:")
    traceback.print_exc()
    sys.exit(1)
