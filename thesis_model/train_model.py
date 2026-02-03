"""
Heart Disease Prediction Model Training Script

This script trains a machine learning model to predict heart disease risk
based on caffeine intake and health profile data.

Usage:
    python train_model.py --dataset_path ../thesis_dataset/Data --output_path ./models
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, roc_curve
import joblib
import os
import argparse
from pathlib import Path


def load_and_preprocess_data(dataset_path):
    """
    Load and preprocess the NHANES dataset for heart disease prediction.
    
    Args:
        dataset_path: Path to the dataset directory
        
    Returns:
        X: Feature matrix
        y: Target variable
        feature_names: List of feature names
    """
    print("Loading dataset...")
    
    # TODO: Load actual NHANES data files
    # For now, this is a placeholder structure
    
    # Example structure:
    # demographics = pd.read_csv(f"{dataset_path}/NHANES Demographics.csv")
    # bp_data = pd.read_csv(f"{dataset_path}/NHANES Blood Pressure Quesstionnaire.csv")
    # food_data = pd.read_csv(f"{dataset_path}/NHANES Individual Food Consumption Day 1 (Reduced).csv")
    # nutrients = pd.read_csv(f"{dataset_path}/NHANES Total Nutrients Day 1.csv")
    
    # Create more realistic synthetic data based on real-world distributions
    print("Creating realistic synthetic dataset...")
    n_samples = 5000  # Increased sample size for better model training
    
    # Age distribution (more realistic - weighted towards middle age)
    age_weights = np.concatenate([
        np.full(12, 0.5),  # 18-29: lower weight
        np.full(20, 1.0),  # 30-49: higher weight
        np.full(20, 1.2),  # 50-69: highest weight
        np.full(11, 0.8)   # 70-80: lower weight
    ])
    age_probs = age_weights / age_weights.sum()
    data = {
        'age': np.random.choice(np.arange(18, 81), n_samples, p=age_probs),
        'sex': np.random.choice(['M', 'F'], n_samples, p=[0.48, 0.52]),
        'bmi': np.clip(np.random.normal(26.5, 5.5, n_samples), 18, 45),  # Realistic BMI range
    }
    
    # Caffeine intake - more realistic distribution (most people consume 0-300mg)
    # Use exponential distribution for caffeine (most people have low intake)
    caffeine_base = np.random.exponential(100, n_samples)  # Mean ~100mg
    caffeine_base = np.clip(caffeine_base, 0, 800)  # Cap at 800mg
    data['avg_daily_caffeine_mg'] = caffeine_base
    data['total_caffeine_week_mg'] = caffeine_base * 7
    
    # Blood pressure - correlated with age and health conditions
    # Normal BP: ~120/80, but varies with age
    base_systolic = 110 + (data['age'] - 40) * 0.3  # Slight increase with age
    base_diastolic = 70 + (data['age'] - 40) * 0.15
    
    # Add noise
    data['systolic_bp'] = np.clip(base_systolic + np.random.normal(0, 12, n_samples), 90, 180)
    data['diastolic_bp'] = np.clip(base_diastolic + np.random.normal(0, 8, n_samples), 60, 120)
    
    # Health conditions - correlated with age
    age_factor = (data['age'] - 18) / 62  # Normalize age to 0-1
    
    # Hypertension probability increases with age
    hypertension_prob = 0.15 + age_factor * 0.25
    data['has_hypertension'] = (np.random.random(n_samples) < hypertension_prob).astype(int)
    
    # Diabetes probability
    diabetes_prob = 0.08 + age_factor * 0.12
    data['has_diabetes'] = (np.random.random(n_samples) < diabetes_prob).astype(int)
    
    # Family history (independent of age)
    data['has_family_history_chd'] = np.random.choice([0, 1], n_samples, p=[0.65, 0.35])
    
    # Smoking (slightly higher in younger adults)
    smoking_prob = 0.15 - age_factor * 0.05
    data['is_smoker'] = (np.random.random(n_samples) < smoking_prob).astype(int)
    
    # Activity level (weighted towards sedentary/light)
    data['activity_level'] = np.random.choice(
        ['sedentary', 'light', 'moderate', 'active'], 
        n_samples, 
        p=[0.35, 0.30, 0.25, 0.10]
    )
    
    df = pd.DataFrame(data)
    
    # Create more realistic target variable (heart disease risk)
    # Use a more conservative risk calculation that doesn't over-predict
    # Risk factors contribute additively but with realistic weights
    risk_score = (
        # Age contribution (0-0.15, not too high)
        age_factor * 0.15 +
        # Blood pressure contribution (only if elevated)
        np.maximum(0, (df['systolic_bp'] - 120) / 60) * 0.12 +
        np.maximum(0, (df['diastolic_bp'] - 80) / 40) * 0.08 +
        # Caffeine contribution (only significant at very high levels)
        np.maximum(0, (df['avg_daily_caffeine_mg'] - 400) / 400) * 0.05 +  # Only counts above 400mg
        # Health conditions (stronger predictors)
        df['has_hypertension'] * 0.20 +
        df['has_diabetes'] * 0.15 +
        df['has_family_history_chd'] * 0.10 +
        df['is_smoker'] * 0.12 +
        # BMI contribution (only if high)
        np.maximum(0, (df['bmi'] - 25) / 20) * 0.08
    )
    
    # Use a higher threshold for high risk (0.35 instead of 0.3)
    # This makes the model more conservative
    df['heart_disease_risk'] = (risk_score > 0.35).astype(int)
    
    # Ensure we have a reasonable class balance
    risk_rate = df['heart_disease_risk'].mean()
    print(f"  High risk cases: {risk_rate:.1%} of dataset")
    
    # Encode categorical variables
    le_sex = LabelEncoder()
    le_activity = LabelEncoder()
    df['sex_encoded'] = le_sex.fit_transform(df['sex'])
    df['activity_level_encoded'] = le_activity.fit_transform(df['activity_level'])
    
    # Select features
    feature_cols = [
        'age', 'sex_encoded', 'bmi',
        'avg_daily_caffeine_mg', 'total_caffeine_week_mg',
        'systolic_bp', 'diastolic_bp',
        'has_hypertension', 'has_diabetes', 'has_family_history_chd',
        'is_smoker', 'activity_level_encoded'
    ]
    
    X = df[feature_cols].values
    y = df['heart_disease_risk'].values
    
    feature_names = feature_cols
    
    # Save encoders
    return X, y, feature_names, {'sex': le_sex, 'activity_level': le_activity}


def train_models(X_train, y_train, X_val, y_val):
    """
    Train multiple models and return the best one.
    
    Args:
        X_train: Training features
        y_train: Training labels
        X_val: Validation features
        y_val: Validation labels
        
    Returns:
        best_model: Best performing model
        best_model_name: Name of the best model
        results: Dictionary of model results
    """
    print("Training models...")
    
    models = {
        'Logistic Regression': LogisticRegression(max_iter=2000, random_state=42, class_weight='balanced'),
        'Random Forest': RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1, 
                                                class_weight='balanced', max_depth=10),
        'Gradient Boosting': GradientBoostingClassifier(n_estimators=200, random_state=42, 
                                                        learning_rate=0.05, max_depth=5)
    }
    
    results = {}
    best_score = 0
    best_model = None
    best_model_name = None
    
    for name, model in models.items():
        print(f"  Training {name}...")
        model.fit(X_train, y_train)
        
        # Predictions
        y_pred = model.predict(X_val)
        y_pred_proba = model.predict_proba(X_val)[:, 1]
        
        # Metrics
        accuracy = accuracy_score(y_val, y_pred)
        precision = precision_score(y_val, y_pred, zero_division=0)
        recall = recall_score(y_val, y_pred, zero_division=0)
        f1 = f1_score(y_val, y_pred, zero_division=0)
        roc_auc = roc_auc_score(y_val, y_pred_proba)
        
        results[name] = {
            'model': model,
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'roc_auc': roc_auc
        }
        
        print(f"    Accuracy: {accuracy:.3f}, ROC-AUC: {roc_auc:.3f}, F1: {f1:.3f}")
        
        # Select best model based on ROC-AUC
        if roc_auc > best_score:
            best_score = roc_auc
            best_model = model
            best_model_name = name
    
    print(f"\nBest model: {best_model_name} (ROC-AUC: {best_score:.3f})")
    
    return best_model, best_model_name, results


def save_model(model, scaler, encoders, feature_names, output_path):
    """
    Save the trained model and preprocessing objects.
    
    Args:
        model: Trained model
        scaler: StandardScaler object
        encoders: Dictionary of label encoders
        feature_names: List of feature names
        output_path: Path to save the model
    """
    os.makedirs(output_path, exist_ok=True)
    
    # Save model
    model_path = os.path.join(output_path, 'heart_disease_model.pkl')
    joblib.dump(model, model_path)
    print(f"Model saved to {model_path}")
    
    # Save scaler
    scaler_path = os.path.join(output_path, 'scaler.pkl')
    joblib.dump(scaler, scaler_path)
    print(f"Scaler saved to {scaler_path}")
    
    # Save encoders
    encoders_path = os.path.join(output_path, 'encoders.pkl')
    joblib.dump(encoders, encoders_path)
    print(f"Encoders saved to {encoders_path}")
    
    # Save feature names
    feature_names_path = os.path.join(output_path, 'feature_names.pkl')
    joblib.dump(feature_names, feature_names_path)
    print(f"Feature names saved to {feature_names_path}")


def main():
    parser = argparse.ArgumentParser(description='Train heart disease prediction model')
    parser.add_argument('--dataset_path', type=str, default='../thesis_dataset/Data',
                        help='Path to dataset directory')
    parser.add_argument('--output_path', type=str, default='./models',
                        help='Path to save trained model')
    parser.add_argument('--test_size', type=float, default=0.2,
                        help='Test set size (default: 0.2)')
    parser.add_argument('--random_state', type=int, default=42,
                        help='Random state for reproducibility')
    
    args = parser.parse_args()
    
    # Load and preprocess data
    X, y, feature_names, encoders = load_and_preprocess_data(args.dataset_path)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=args.test_size, random_state=args.random_state, stratify=y
    )
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train models
    best_model, best_model_name, results = train_models(
        X_train_scaled, y_train, X_test_scaled, y_test
    )
    
    # Print final results
    print("\n" + "="*50)
    print("Final Model Performance:")
    print("="*50)
    for name, metrics in results.items():
        print(f"\n{name}:")
        print(f"  Accuracy:  {metrics['accuracy']:.3f}")
        print(f"  Precision: {metrics['precision']:.3f}")
        print(f"  Recall:    {metrics['recall']:.3f}")
        print(f"  F1-Score:  {metrics['f1']:.3f}")
        print(f"  ROC-AUC:   {metrics['roc_auc']:.3f}")
    
    # Save best model
    save_model(best_model, scaler, encoders, feature_names, args.output_path)
    
    print("\nTraining completed successfully!")


if __name__ == '__main__':
    main()
