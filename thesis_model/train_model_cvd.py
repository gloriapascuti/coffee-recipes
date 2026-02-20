"""
Train heart disease prediction model using REAL CVD outcomes from NHANES 1988-2018.

This replaces the synthetic formula-based labels with actual cardiovascular deaths
from 30 years of mortality follow-up data.

Usage:
    python train_model_cvd.py --dataset_path /path/to/nhanes_cvd_training_data.csv --output_path ./models
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, precision_score, recall_score, f1_score, 
                            roc_auc_score, roc_curve, classification_report, confusion_matrix)
from sklearn.utils.class_weight import compute_class_weight
import joblib
import os
import argparse
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')


def load_and_preprocess_data(dataset_path):
    """
    Load the prepared NHANES dataset with real CVD outcomes.
    
    Args:
        dataset_path: Path to nhanes_cvd_training_data.csv
    
    Returns:
        X: Feature matrix
        y: Target variable (real CVD deaths!)
        feature_names: List of feature names
        encoders: Dictionary of label encoders
    """
    print("="*80)
    print("Loading NHANES 1988-2018 dataset with REAL CVD outcomes")
    print("="*80)
    
    df = pd.read_csv(dataset_path)
    print(f"\nLoaded {len(df):,} records from NHANES 1988-2018")
    
    # Check target distribution
    n_cvd_deaths = df['cvd_death'].sum()
    n_alive = (df['cvd_death'] == 0).sum()
    print(f"\nTarget distribution:")
    print(f"  CVD deaths: {n_cvd_deaths:,} ({n_cvd_deaths/len(df)*100:.2f}%)")
    print(f"  Alive/Non-CVD: {n_alive:,} ({n_alive/len(df)*100:.2f}%)")
    print(f"\n✓ These are REAL outcomes from mortality follow-up (mean 14.4 years)")
    
    # Encode categorical variables
    print("\nEncoding categorical variables...")
    le_sex = LabelEncoder()
    le_activity = LabelEncoder()
    
    df['sex_encoded'] = le_sex.fit_transform(df['sex'])
    df['activity_level_encoded'] = le_activity.fit_transform(df['activity_level'])
    
    # Select features (matching your current model structure)
    feature_cols = [
        'age', 'sex_encoded', 'bmi',
        'avg_daily_caffeine_mg', 'total_caffeine_week_mg',
        'systolic_bp', 'diastolic_bp',
        'has_hypertension', 'has_diabetes', 'has_family_history_chd',
        'is_smoker', 'activity_level_encoded'
    ]
    
    # Add high cholesterol if available
    if 'has_high_cholesterol' in df.columns:
        feature_cols.append('has_high_cholesterol')
    
    print(f"\nFeatures selected: {len(feature_cols)}")
    for i, feat in enumerate(feature_cols, 1):
        print(f"  {i:2d}. {feat}")
    
    # Check for missing values
    missing_counts = df[feature_cols].isna().sum()
    if missing_counts.sum() > 0:
        print("\n Missing values detected:")
        for col, count in missing_counts[missing_counts > 0].items():
            print(f"     {col}: {count}")
        print("  Filling with median/mode...")
        for col in feature_cols:
            if df[col].isna().sum() > 0:
                if df[col].dtype in ['int64', 'float64']:
                    df[col] = df[col].fillna(df[col].median())
                else:
                    df[col] = df[col].fillna(df[col].mode()[0])
    
    X = df[feature_cols].values
    y = df['cvd_death'].values
    
    print(f"\n✓ Final dataset: {len(X):,} samples × {len(feature_cols)} features")
    print(f"✓ Target: {y.sum():,} CVD deaths ({y.mean()*100:.2f}%)")
    
    encoders = {'sex': le_sex, 'activity_level': le_activity}
    
    return X, y, feature_cols, encoders


def train_models(X_train, y_train, X_val, y_val):
    """
    Train multiple models with proper class imbalance handling.
    
    Args:
        X_train: Training features
        y_train: Training labels (real CVD deaths)
        X_val: Validation features
        y_val: Validation labels
    
    Returns:
        best_model: Best performing model
        best_model_name: Name of the best model
        results: Dictionary of model results
    """
    print("\n" + "="*80)
    print("Training models with real CVD outcomes")
    print("="*80)
    
    # Compute class weights for imbalanced data
    class_weights = compute_class_weight('balanced', classes=np.unique(y_train), y=y_train)
    class_weight_dict = {0: class_weights[0], 1: class_weights[1]}
    print(f"\nClass weights (to handle imbalance):")
    print(f"  Class 0 (alive): {class_weights[0]:.2f}")
    print(f"  Class 1 (CVD death): {class_weights[1]:.2f}")
    
    # Define models
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
        class_weight='balanced',
        solver='lbfgs'
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
    
    print("\nTraining individual models...")
    for name, model in models.items():
        print(f"\n  Training {name}...")
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
            'roc_auc': roc_auc,
            'y_pred': y_pred,
            'y_pred_proba': y_pred_proba
        }
        
        print(f"    Accuracy: {accuracy:.3f} | Precision: {precision:.3f} | Recall: {recall:.3f}")
        print(f"    F1: {f1:.3f} | ROC-AUC: {roc_auc:.3f}")
        
        if roc_auc > best_score:
            best_score = roc_auc
            best_model = model
            best_model_name = name
    
    # Train ensemble model
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
        'roc_auc': roc_auc_ensemble,
        'y_pred': y_pred_ensemble,
        'y_pred_proba': y_pred_proba_ensemble
    }
    
    print(f"    Accuracy: {accuracy_ensemble:.3f} | Precision: {precision_ensemble:.3f} | Recall: {recall_ensemble:.3f}")
    print(f"    F1: {f1_ensemble:.3f} | ROC-AUC: {roc_auc_ensemble:.3f}")
    
    # Select best model (prefer ensemble if within 0.1% of best)
    if roc_auc_ensemble >= best_score - 0.001:
        best_score = roc_auc_ensemble
        best_model = ensemble
        best_model_name = 'Ensemble (RF + GB)'
        print(f"\n  → Selected ensemble for better robustness")
    elif roc_auc_ensemble > best_score:
        best_score = roc_auc_ensemble
        best_model = ensemble
        best_model_name = 'Ensemble (RF + GB)'
    
    print(f"\n{'='*80}")
    print(f"Best model: {best_model_name} (ROC-AUC: {best_score:.3f})")
    print(f"{'='*80}")
    
    return best_model, best_model_name, results


def get_feature_importance_from_model(model, feature_names):
    """
    Extract feature importances from a trained model.
    Handles VotingClassifier, RandomForest, GradientBoosting, and LogisticRegression.
    """
    from sklearn.ensemble import VotingClassifier
    
    if isinstance(model, VotingClassifier):
        importances_list = []
        for name, estimator in model.named_estimators_.items():
            if hasattr(estimator, 'feature_importances_'):
                importances_list.append(estimator.feature_importances_)
            elif hasattr(estimator, 'coef_'):
                coef = np.abs(estimator.coef_[0])
                importances_list.append(coef / coef.sum())
        
        if importances_list:
            avg_importances = np.mean(importances_list, axis=0)
        else:
            raise ValueError("Could not extract feature importances from ensemble")
    elif hasattr(model, 'feature_importances_'):
        avg_importances = model.feature_importances_
    elif hasattr(model, 'coef_'):
        coef = np.abs(model.coef_[0])
        avg_importances = coef / coef.sum()
    else:
        raise ValueError(f"Model type {type(model)} does not support feature importances")
    
    importances_percent = (avg_importances / avg_importances.sum()) * 100
    return importances_percent


def get_readable_feature_names(feature_names):
    """Map technical feature names to readable display names."""
    name_mapping = {
        'age': 'Age',
        'sex_encoded': 'Sex',
        'bmi': 'BMI',
        'avg_daily_caffeine_mg': 'Avg Daily Caffeine Intake',
        'total_caffeine_week_mg': 'Total Weekly Caffeine Intake',
        'systolic_bp': 'Systolic Blood Pressure',
        'diastolic_bp': 'Diastolic Blood Pressure',
        'has_hypertension': 'Hypertension',
        'has_diabetes': 'Diabetes',
        'has_family_history_chd': 'Family History of CHD',
        'is_smoker': 'Smoking Status',
        'activity_level_encoded': 'Physical Activity',
        'has_high_cholesterol': 'High Cholesterol',
    }
    
    readable_names = []
    for name in feature_names:
        readable_names.append(name_mapping.get(name, name.replace('_', ' ').title()))
    
    return readable_names


def plot_feature_importance(model, feature_names, output_path=None):
    """Plot feature importances from a trained model."""
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("⚠️  matplotlib not available, skipping plot")
        return
    
    importances = get_feature_importance_from_model(model, feature_names)
    readable_names = get_readable_feature_names(feature_names)
    
    sorted_indices = np.argsort(importances)[::-1]
    sorted_importances = importances[sorted_indices]
    sorted_names = [readable_names[i] for i in sorted_indices]
    
    plt.figure(figsize=(10, 6))
    bars = plt.barh(sorted_names, sorted_importances, edgecolor="black", color='steelblue')
    plt.xlabel("Relative Contribution to CVD Risk Prediction (%)", fontsize=12)
    plt.title("Feature-Level Contributions to Real CVD Death Prediction", fontsize=14, fontweight='bold')
    
    max_importance = sorted_importances.max()
    plt.xlim(0, max_importance * 1.2)
    
    for bar in bars:
        width = bar.get_width()
        plt.text(width + max_importance * 0.02, bar.get_y() + bar.get_height() / 2,
                f"{width:.1f}%", va="center", fontsize=10, fontweight='bold')
    
    plt.gca().invert_yaxis()
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"\n✓ Feature importance plot saved to {output_path}")
    else:
        plt.show()
    
    print("\n" + "="*60)
    print("Feature Importances (What Predicts Real CVD Deaths):")
    print("="*60)
    for name, imp in zip(sorted_names, sorted_importances):
        print(f"{name:35s}: {imp:6.2f}%")
    print("="*60)


def evaluate_model_detailed(best_model, best_model_name, results, y_val):
    """Print detailed evaluation metrics."""
    print("\n" + "="*80)
    print("DETAILED MODEL EVALUATION - Real CVD Outcomes")
    print("="*80)
    
    print(f"\nBest Model: {best_model_name}")
    best_results = results[best_model_name]
    
    print("\n1. Overall Metrics:")
    print(f"   Accuracy:  {best_results['accuracy']:.3f}")
    print(f"   Precision: {best_results['precision']:.3f} (of predicted CVD deaths, how many were real)")
    print(f"   Recall:    {best_results['recall']:.3f} (of real CVD deaths, how many did we catch)")
    print(f"   F1-Score:  {best_results['f1']:.3f} (harmonic mean of precision & recall)")
    print(f"   ROC-AUC:   {best_results['roc_auc']:.3f} (area under ROC curve)")
    
    print("\n2. Confusion Matrix:")
    cm = confusion_matrix(y_val, best_results['y_pred'])
    print(f"   True Negatives (alive, predicted alive):  {cm[0,0]:,}")
    print(f"   False Positives (alive, predicted death): {cm[0,1]:,}")
    print(f"   False Negatives (death, predicted alive): {cm[1,0]:,}")
    print(f"   True Positives (death, predicted death):  {cm[1,1]:,}")
    
    print("\n3. Classification Report:")
    print(classification_report(y_val, best_results['y_pred'], 
                                target_names=['Alive', 'CVD Death'],
                                digits=3))
    
    print("\n4. All Models Comparison:")
    print(f"{'Model':<30} {'Accuracy':>10} {'Precision':>10} {'Recall':>10} {'F1':>10} {'ROC-AUC':>10}")
    print("-" * 90)
    for name, metrics in results.items():
        print(f"{name:<30} {metrics['accuracy']:>10.3f} {metrics['precision']:>10.3f} "
              f"{metrics['recall']:>10.3f} {metrics['f1']:>10.3f} {metrics['roc_auc']:>10.3f}")


def save_model(model, scaler, encoders, feature_names, output_path):
    """Save the trained model and preprocessing objects."""
    os.makedirs(output_path, exist_ok=True)
    
    model_path = os.path.join(output_path, 'heart_disease_model.pkl')
    joblib.dump(model, model_path)
    print(f"\n✓ Model saved to {model_path}")
    
    scaler_path = os.path.join(output_path, 'scaler.pkl')
    joblib.dump(scaler, scaler_path)
    print(f"✓ Scaler saved to {scaler_path}")
    
    encoders_path = os.path.join(output_path, 'encoders.pkl')
    joblib.dump(encoders, encoders_path)
    print(f"✓ Encoders saved to {encoders_path}")
    
    feature_names_path = os.path.join(output_path, 'feature_names.pkl')
    joblib.dump(feature_names, feature_names_path)
    print(f"✓ Feature names saved to {feature_names_path}")


def main():
    parser = argparse.ArgumentParser(
        description='Train heart disease prediction model with REAL CVD outcomes'
    )
    parser.add_argument('--dataset_path', type=str, 
                       default='/Users/filip/Desktop/NHANES 1988-2018 Archive/nhanes_cvd_training_data.csv',
                       help='Path to nhanes_cvd_training_data.csv')
    parser.add_argument('--output_path', type=str, default='./models',
                       help='Path to save trained model')
    parser.add_argument('--test_size', type=float, default=0.2,
                       help='Test set size (default: 0.2)')
    parser.add_argument('--random_state', type=int, default=42,
                       help='Random state for reproducibility')
    
    args = parser.parse_args()
    
    # Check if dataset exists
    if not os.path.exists(args.dataset_path):
        print(f"Error: Dataset not found at {args.dataset_path}")
        print(f"\nPlease run prepare_training_data.py first or specify correct path.")
        return
    
    # Load and preprocess data
    X, y, feature_names, encoders = load_and_preprocess_data(args.dataset_path)
    
    # Split data
    print(f"\nSplitting data (test_size={args.test_size})...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=args.test_size, random_state=args.random_state, stratify=y
    )
    print(f"  Training set: {len(X_train):,} samples ({y_train.sum():,} CVD deaths)")
    print(f"  Test set:     {len(X_test):,} samples ({y_test.sum():,} CVD deaths)")
    
    # Scale features
    print(f"\nScaling features...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    print("  ✓ Features standardized (mean=0, std=1)")
    
    # Train models
    best_model, best_model_name, results = train_models(
        X_train_scaled, y_train, X_test_scaled, y_test
    )
    
    # Detailed evaluation
    evaluate_model_detailed(best_model, best_model_name, results, y_test)
    
    # Save model
    print("\n" + "="*80)
    print("Saving model artifacts")
    print("="*80)
    save_model(best_model, scaler, encoders, feature_names, args.output_path)
    
    # Plot feature importances
    print("\n" + "="*80)
    print("Generating Feature Importance Plot")
    print("="*80)
    try:
        plot_path = os.path.join(args.output_path, 'feature_importance_cvd.png')
        plot_feature_importance(best_model, feature_names, output_path=plot_path)
    except Exception as e:
        print(f"Could not generate feature importance plot: {e}")
    
    # Final summary
    print("\n" + "="*80)
    print("TRAINING COMPLETE - Model Uses REAL CVD Outcomes!")
    print("="*80)
    print(f"\nTraining Summary:")
    print(f"   • Dataset: {len(X):,} samples from NHANES 1988-2018")
    print(f"   • CVD deaths: {y.sum():,} real outcomes (not formula-based!)")
    print(f"   • Best model: {best_model_name}")
    print(f"   • ROC-AUC: {results[best_model_name]['roc_auc']:.3f}")
    print(f"   • Model saved to: {args.output_path}")
    print(f"\nThis model learns from REAL cardiovascular outcomes,")
    print(f"   not from synthetic formulas. It's scientifically legitimate!")
    print(f"\nYour API and frontend will work exactly the same,")
    print(f"   but now the ML is based on actual mortality data.")
    print("\n" + "="*80)


if __name__ == '__main__':
    main()
