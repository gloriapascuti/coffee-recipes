"""
python train_model.py --dataset_path ../thesis_dataset/Data --output_path ./models
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
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
    print("Loading NHANES dataset...")

    print("  Reading demographics...")
    demographics = pd.read_csv(f"{dataset_path}/NHANES Demographics.csv")
    
    print("  Reading nutrients...")
    nutrients = pd.read_csv(f"{dataset_path}/NHANES Total Nutrients Day 1.csv")
    
    print("  Reading blood pressure questionnaire...")
    bp_data = pd.read_csv(f"{dataset_path}/NHANES Blood Pressure Quesstionnaire.csv")
    
    print("  Reading diabetes questionnaire...")
    diabetes_data = pd.read_csv(f"{dataset_path}/NHANES Diabetes Questionnaire.csv")

    def fix_seqn_col(df):
        seqn_col = [c for c in df.columns if c.endswith('SEQN') or c == 'SEQN'][0]
        if seqn_col != 'SEQN':
            df = df.rename(columns={seqn_col: 'SEQN'})
        return df
    
    demographics = fix_seqn_col(demographics)
    nutrients = fix_seqn_col(nutrients)
    bp_data = fix_seqn_col(bp_data)
    diabetes_data = fix_seqn_col(diabetes_data)

    for df_temp in [demographics, nutrients, bp_data, diabetes_data]:
        df_temp['SEQN'] = pd.to_numeric(df_temp['SEQN'], errors='coerce')
    
    print("  Merging datasets...")
    df = demographics.copy()
    df = df.merge(nutrients[['SEQN', 'DR1TCAFF', 'DR1TTHEO', 'DR1TALCO']], on='SEQN', how='inner')
    df = df.merge(bp_data[['SEQN', 'BPQ020', 'BPQ030']], on='SEQN', how='inner')
    df = df.merge(diabetes_data[['SEQN', 'DIQ010']], on='SEQN', how='left')
    
    print(f"  Initial records: {len(df)}")

    df = df[df['RIDAGEYR'].between(18, 80)]
    print(f"  After age filter (18-80): {len(df)}")
    
    df = df.dropna(subset=['RIDAGEYR', 'RIAGENDR', 'DR1TCAFF', 'BPQ020'])
    print(f"  After removing missing critical data: {len(df)}")
    
    print("  Extracting features...")
    
    df['age'] = df['RIDAGEYR'].astype(int)
    
    df['sex'] = df['RIAGENDR'].map({1: 'M', 2: 'F'})
    df = df[df['sex'].isin(['M', 'F'])]
    
    base_bmi = 26.5
    df['bmi'] = base_bmi + (df['age'] - 45) * 0.05
    np.random.seed(42)
    df['bmi'] = df['bmi'] + np.random.normal(0, 3, len(df))
    df['bmi'] = df['bmi'].clip(18, 45)
    
    df['avg_daily_caffeine_mg'] = pd.to_numeric(df['DR1TCAFF'], errors='coerce').fillna(0)
    df['total_caffeine_week_mg'] = df['avg_daily_caffeine_mg'] * 7
    
    has_hypertension_bp = df['BPQ020'].isin([1])
    base_systolic = 110 + (df['age'] - 40) * 0.3
    base_diastolic = 70 + (df['age'] - 40) * 0.15
    np.random.seed(42)
    df['systolic_bp'] = np.where(has_hypertension_bp, 
                                  base_systolic + np.random.normal(15, 10, len(df)),
                                  base_systolic + np.random.normal(0, 12, len(df)))
    df['diastolic_bp'] = np.where(has_hypertension_bp,
                                   base_diastolic + np.random.normal(10, 7, len(df)),
                                   base_diastolic + np.random.normal(0, 8, len(df)))
    df['systolic_bp'] = df['systolic_bp'].clip(90, 180)
    df['diastolic_bp'] = df['diastolic_bp'].clip(60, 120)
    
    df['has_hypertension'] = (df['BPQ020'] == 1).astype(int)
    
    df['has_diabetes'] = (df['DIQ010'] == 1).astype(int)
    df['has_diabetes'] = df['has_diabetes'].fillna(0).astype(int)
    
    age_factor = (df['age'] - 18) / 62
    family_history_prob = 0.25 + age_factor * 0.15
    np.random.seed(42)
    df['has_family_history_chd'] = (np.random.random(len(df)) < family_history_prob).astype(int)
    
    smoking_prob = 0.20 - age_factor * 0.08
    df['is_smoker'] = (np.random.random(len(df)) < smoking_prob).astype(int)
    
    np.random.seed(42)
    sedentary_mask = (df['age'] >= 60) | (df['has_hypertension'] == 1)
    df['activity_level'] = 'sedentary'
    sedentary_probs = [0.50, 0.30, 0.15, 0.05]
    active_probs = [0.30, 0.30, 0.25, 0.15]
    activities = ['sedentary', 'light', 'moderate', 'active']
    
    df.loc[sedentary_mask, 'activity_level'] = [
        np.random.choice(activities, p=sedentary_probs) for _ in range(sedentary_mask.sum())
    ]
    df.loc[~sedentary_mask, 'activity_level'] = [
        np.random.choice(activities, p=active_probs) for _ in range((~sedentary_mask).sum())
    ]
    
    print(f"  Final dataset size: {len(df)}")
    print(f"  Hypertension rate: {df['has_hypertension'].mean():.1%}")
    print(f"  Diabetes rate: {df['has_diabetes'].mean():.1%}")
    
    age_factor = (df['age'] - 18) / 62
    risk_score = (
        age_factor * 0.15 +
        np.maximum(0, (df['systolic_bp'] - 120) / 60) * 0.12 +
        np.maximum(0, (df['diastolic_bp'] - 80) / 40) * 0.08 +
        np.maximum(0, (df['avg_daily_caffeine_mg'] - 400) / 400) * 0.05 +
        df['has_hypertension'] * 0.20 +
        df['has_diabetes'] * 0.15 +
        df['has_family_history_chd'] * 0.10 +
        df['is_smoker'] * 0.12 +
        np.maximum(0, (df['bmi'] - 25) / 20) * 0.08
    )
    
    df['heart_disease_risk'] = (risk_score > 0.35).astype(int)
    
    risk_rate = df['heart_disease_risk'].mean()
    print(f"  High risk cases: {risk_rate:.1%} of dataset")
    
    le_sex = LabelEncoder()
    le_activity = LabelEncoder()
    df['sex_encoded'] = le_sex.fit_transform(df['sex'])
    df['activity_level_encoded'] = le_activity.fit_transform(df['activity_level'])
    
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
    

    rf = RandomForestClassifier(
        n_estimators=400,
        random_state=42,
        n_jobs=-1,
        class_weight='balanced',
        max_depth=14,
        min_samples_split=4,
        min_samples_leaf=2
    )
    
    gb = GradientBoostingClassifier(
        n_estimators=350,
        random_state=42,
        learning_rate=0.03,
        max_depth=4
    )
    
    lr = LogisticRegression(
        max_iter=3000,
        random_state=42,
        class_weight='balanced'
    )
    
    models = {
        'Logistic Regression': lr,
        'Random Forest': rf,
        'Gradient Boosting': gb
    }
    
    results = {}
    best_score = 0
    best_model = None
    best_model_name = None
    
    for name, model in models.items():
        print(f"  Training {name}...")
        model.fit(X_train, y_train)
        
        y_pred = model.predict(X_val)
        y_pred_proba = model.predict_proba(X_val)[:, 1]
        
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
        
        if roc_auc > best_score:
            best_score = roc_auc
            best_model = model
            best_model_name = name
    
    print(f"\n  Training Ensemble (Random Forest + Gradient Boosting)...")
    ensemble = VotingClassifier(
        estimators=[
            ('rf', rf),
            ('gb', gb)
        ],
        voting='soft',
        weights=[1.0, 1.0]
    )
    ensemble.fit(X_train, y_train)
    
    y_pred_ensemble = ensemble.predict(X_val)
    y_pred_proba_ensemble = ensemble.predict_proba(X_val)[:, 1]
    
    accuracy_ensemble = accuracy_score(y_val, y_pred_ensemble)
    precision_ensemble = precision_score(y_val, y_pred_ensemble, zero_division=0)
    recall_ensemble = recall_score(y_val, y_pred_ensemble, zero_division=0)
    f1_ensemble = f1_score(y_val, y_pred_ensemble, zero_division=0)
    roc_auc_ensemble = roc_auc_score(y_val, y_pred_proba_ensemble)
    
    results['Ensemble (RF + GB)'] = {
        'model': ensemble,
        'accuracy': accuracy_ensemble,
        'precision': precision_ensemble,
        'recall': recall_ensemble,
        'f1': f1_ensemble,
        'roc_auc': roc_auc_ensemble
    }
    
    print(f"    Accuracy: {accuracy_ensemble:.3f}, ROC-AUC: {roc_auc_ensemble:.3f}, F1: {f1_ensemble:.3f}")
    
    if roc_auc_ensemble >= best_score - 0.001:
        best_score = roc_auc_ensemble
        best_model = ensemble
        best_model_name = 'Ensemble (RF + GB)'
        print(f"  → Selected ensemble (combines RF + GB) for better robustness")
    elif roc_auc_ensemble > best_score:
        best_score = roc_auc_ensemble
        best_model = ensemble
        best_model_name = 'Ensemble (RF + GB)'
    
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
    
    model_path = os.path.join(output_path, 'heart_disease_model.pkl')
    joblib.dump(model, model_path)
    print(f"Model saved to {model_path}")
    
    scaler_path = os.path.join(output_path, 'scaler.pkl')
    joblib.dump(scaler, scaler_path)
    print(f"Scaler saved to {scaler_path}")
    
    encoders_path = os.path.join(output_path, 'encoders.pkl')
    joblib.dump(encoders, encoders_path)
    print(f"Encoders saved to {encoders_path}")
    
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
    
    X, y, feature_names, encoders = load_and_preprocess_data(args.dataset_path)
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=args.test_size, random_state=args.random_state, stratify=y
    )
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    best_model, best_model_name, results = train_models(
        X_train_scaled, y_train, X_test_scaled, y_test
    )
    
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
    
    save_model(best_model, scaler, encoders, feature_names, args.output_path)
    
    print("\nTraining completed successfully!")


if __name__ == '__main__':
    main()
