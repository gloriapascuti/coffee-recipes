"""
Complete ML Pipeline: Train CVD Model + Optimize Threshold

Usage:
    python trained_model.py --dataset_path /path/to/data.csv --output_path ./models_improved
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, precision_score, recall_score, f1_score, 
                            roc_auc_score, classification_report, confusion_matrix)
from sklearn.utils.class_weight import compute_class_weight
import joblib
import os
import argparse
import warnings
warnings.filterwarnings('ignore')


def load_and_preprocess_data(dataset_path):
    df = pd.read_csv(dataset_path)
    print(f"Loaded {len(df):,} records")
    
    n_cvd_deaths = df['cvd_death'].sum()
    print(f"CVD deaths: {n_cvd_deaths:,} ({n_cvd_deaths/len(df)*100:.2f}%)")
    
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
    
    if 'has_high_cholesterol' in df.columns:
        feature_cols.append('has_high_cholesterol')
    
    lab_features = ['total_cholesterol', 'hdl_cholesterol', 'ldl_cholesterol', 'triglycerides', 'glucose']
    for lab in lab_features:
        if lab in df.columns:
            feature_cols.append(lab)
    
    caff_features = ['caffeine_per_kg', 'caffeine_per_bmi', 'caffeine_category', 
                    'caffeine_age_interaction', 'caffeine_hypertension_interaction', 'is_high_caffeine']
    for caff in caff_features:
        if caff in df.columns:
            feature_cols.append(caff)
    
    missing_counts = df[feature_cols].isna().sum()
    if missing_counts.sum() > 0:
        for col in feature_cols:
            if df[col].isna().sum() > 0:
                if df[col].dtype in ['int64', 'float64']:
                    df[col] = df[col].fillna(df[col].median())
                else:
                    df[col] = df[col].fillna(df[col].mode()[0])
    
    X = df[feature_cols].values
    y = df['cvd_death'].values
    
    print(f"Final dataset: {len(X):,} samples × {len(feature_cols)} features\n")
    
    encoders = {'sex': le_sex, 'activity_level': le_activity}
    return X, y, feature_cols, encoders


def train_models(X_train, y_train, X_val, y_val):
    print("Training models...")
    y
    class_weights = compute_class_weight('balanced', classes=np.unique(y_train), y=y_train)
    
    rf = RandomForestClassifier(
        n_estimators=400, random_state=42, n_jobs=-1, class_weight='balanced',
        max_depth=14, min_samples_split=4, min_samples_leaf=2
    )
    
    gb = GradientBoostingClassifier(
        n_estimators=350, random_state=42, learning_rate=0.03, max_depth=4
    )
    
    lr = LogisticRegression(
        max_iter=3000, random_state=42, class_weight='balanced', solver='lbfgs'
    )
    
    models = {'Logistic Regression': lr, 'Random Forest': rf, 'Gradient Boosting': gb}
    
    results = {}
    best_score = 0
    best_model = None
    best_model_name = None
    
    for name, model in models.items():
        print(f"  Training {name}...")
        model.fit(X_train, y_train)
        
        y_pred = model.predict(X_val) # hard binary 0 (alive) or 1 (death)
        y_pred_proba = model.predict_proba(X_val)[:, 1] # raw probability of death for each patient
        
        accuracy = accuracy_score(y_val, y_pred) # compares y_pred with y_val
        precision = precision_score(y_val, y_pred, zero_division=0) # y_pred / y_val, zero_division is only to prevent crash -> false alarms
        recall = recall_score(y_val, y_pred, zero_division=0) # false negatives
        f1 = f1_score(y_val, y_pred, zero_division=0) # ( 2 x precision x recall ) / ( precision + recall ) -> forces balance between the two
        roc_auc = roc_auc_score(y_val, y_pred_proba) # raw probability -> calculates the area under the ROC curve
        
        results[name] = {
            'model': model, 'accuracy': accuracy, 'precision': precision,
            'recall': recall, 'f1': f1, 'roc_auc': roc_auc,
            'y_pred': y_pred, 'y_pred_proba': y_pred_proba
        }
        
        print(f"    ROC-AUC: {roc_auc:.3f}")
        
        if roc_auc > best_score:
            best_score = roc_auc
            best_model = model
            best_model_name = name
    
    print(f"  Training Ensemble...")
    ensemble = VotingClassifier(estimators=[('rf', rf), ('gb', gb)], voting='soft', weights=[1.0, 1.0]) # soft voting preserves confidence information
    ensemble.fit(X_train, y_train)
    # rf for reducing variance
    # gb for reducing bias

    y_pred_ensemble = ensemble.predict(X_val)
    y_pred_proba_ensemble = ensemble.predict_proba(X_val)[:, 1]
    
    accuracy_ensemble = accuracy_score(y_val, y_pred_ensemble)
    precision_ensemble = precision_score(y_val, y_pred_ensemble, zero_division=0)
    recall_ensemble = recall_score(y_val, y_pred_ensemble, zero_division=0)
    f1_ensemble = f1_score(y_val, y_pred_ensemble, zero_division=0)
    roc_auc_ensemble = roc_auc_score(y_val, y_pred_proba_ensemble)
    
    results['Ensemble (RF + GB)'] = {
        'model': ensemble, 'accuracy': accuracy_ensemble, 'precision': precision_ensemble,
        'recall': recall_ensemble, 'f1': f1_ensemble, 'roc_auc': roc_auc_ensemble,
        'y_pred': y_pred_ensemble, 'y_pred_proba': y_pred_proba_ensemble
    }
    
    print(f"    ROC-AUC: {roc_auc_ensemble:.3f}")
    
    if roc_auc_ensemble >= best_score - 0.001:
        best_score = roc_auc_ensemble
        best_model = ensemble
        best_model_name = 'Ensemble (RF + GB)'
    elif roc_auc_ensemble > best_score:
        best_score = roc_auc_ensemble
        best_model = ensemble
        best_model_name = 'Ensemble (RF + GB)'
    
    print(f"\nBest model: {best_model_name} (ROC-AUC: {best_score:.3f})\n")
    
    return best_model, best_model_name, results


def optimize_threshold(model, scaler, X_test, y_test):
    print("Optimizing threshold...")
    
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    thresholds = [0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50]
    results = []
    
    print(f"\n{'Threshold':<12} {'Recall':<12} {'Precision':<12} {'F1-Score':<12}")
    print("-" * 60)
    
    for threshold in thresholds:
        y_pred = (y_pred_proba >= threshold).astype(int)
        
        recall = recall_score(y_test, y_pred, zero_division=0)
        precision = precision_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        
        true_positives = ((y_test == 1) & (y_pred == 1)).sum()
        false_positives = ((y_test == 0) & (y_pred == 1)).sum()
        
        results.append({
            'threshold': threshold, 'recall': recall, 'precision': precision,
            'f1': f1, 'tp': true_positives, 'fp': false_positives
        })
        
        print(f"{threshold:<12.2f} {recall:<12.3f} {precision:<12.3f} {f1:<12.3f}")
    
    best_by_f1 = max(results, key=lambda x: x['f1'])
    
    print(f"\nOptimal threshold: {best_by_f1['threshold']:.2f}")
    print(f"  Recall: {best_by_f1['recall']:.1%}, Precision: {best_by_f1['precision']:.1%}, F1: {best_by_f1['f1']:.3f}\n")
    
    return best_by_f1['threshold'], results


def get_feature_importance_from_model(model, feature_names):
    from sklearn.ensemble import VotingClassifier
    
    if isinstance(model, VotingClassifier):
        importances_list = []
        for name, estimator in model.named_estimators_.items():
            if hasattr(estimator, 'feature_importances_'):
                importances_list.append(estimator.feature_importances_)
            elif hasattr(estimator, 'coef_'):
                coef = np.abs(estimator.coef_[0])
                importances_list.append(coef / coef.sum())
        avg_importances = np.mean(importances_list, axis=0) if importances_list else None
    elif hasattr(model, 'feature_importances_'):
        avg_importances = model.feature_importances_
    elif hasattr(model, 'coef_'):
        coef = np.abs(model.coef_[0])
        avg_importances = coef / coef.sum()
    else:
        raise ValueError(f"Model type {type(model)} does not support feature importances")
    
    return (avg_importances / avg_importances.sum()) * 100


def get_readable_feature_names(feature_names):
    name_mapping = {
        'age': 'Age', 'sex_encoded': 'Sex', 'bmi': 'BMI',
        'avg_daily_caffeine_mg': 'Avg Daily Caffeine Intake',
        'total_caffeine_week_mg': 'Total Weekly Caffeine Intake',
        'systolic_bp': 'Systolic Blood Pressure',
        'diastolic_bp': 'Diastolic Blood Pressure',
        'has_hypertension': 'Hypertension', 'has_diabetes': 'Diabetes',
        'has_family_history_chd': 'Family History of CHD',
        'is_smoker': 'Smoking Status',
        'activity_level_encoded': 'Physical Activity',
        'has_high_cholesterol': 'High Cholesterol',
        'total_cholesterol': 'Total Cholesterol',
        'hdl_cholesterol': 'HDL Cholesterol',
        'ldl_cholesterol': 'LDL Cholesterol',
        'triglycerides': 'Triglycerides', 'glucose': 'Glucose',
        'caffeine_per_kg': 'Caffeine Per Kg',
        'caffeine_per_bmi': 'Caffeine Per BMI',
        'caffeine_category': 'Caffeine Category',
        'caffeine_age_interaction': 'Caffeine Age Interaction',
        'caffeine_hypertension_interaction': 'Caffeine Hypertension Interaction',
        'is_high_caffeine': 'Is High Caffeine',
    }
    
    return [name_mapping.get(name, name.replace('_', ' ').title()) for name in feature_names]


def plot_feature_importance(model, feature_names, output_path=None):
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not available, skipping plot")
        return
    
    importances = get_feature_importance_from_model(model, feature_names)
    readable_names = get_readable_feature_names(feature_names)
    
    sorted_indices = np.argsort(importances)[::-1]
    sorted_importances = importances[sorted_indices]
    sorted_names = [readable_names[i] for i in sorted_indices]
    
    plt.figure(figsize=(10, 6))
    bars = plt.barh(sorted_names, sorted_importances, edgecolor="black", color='steelblue')
    plt.xlabel("Relative Contribution to CVD Risk Prediction (%)", fontsize=12)
    plt.title("Feature Contributions to CVD Death Prediction", fontsize=14, fontweight='bold')
    
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
        print(f"Feature importance plot saved to {output_path}")
    else:
        plt.show()
    
    print("\nFeature Importances:")
    for name, imp in zip(sorted_names, sorted_importances):
        print(f"{name:40s}: {imp:6.2f}%")


def evaluate_model_detailed(best_model, best_model_name, results, y_val):
    print("\nDetailed Model Evaluation")
    print(f"Best Model: {best_model_name}")
    
    best_results = results[best_model_name]
    
    print(f"\nMetrics:")
    print(f"  Accuracy:  {best_results['accuracy']:.3f}")
    print(f"  Precision: {best_results['precision']:.3f}")
    print(f"  Recall:    {best_results['recall']:.3f}")
    print(f"  F1-Score:  {best_results['f1']:.3f}")
    print(f"  ROC-AUC:   {best_results['roc_auc']:.3f}")
    
    cm = confusion_matrix(y_val, best_results['y_pred'])
    print(f"\nConfusion Matrix:")
    print(f"  True Negatives:  {cm[0,0]:,}")
    print(f"  False Positives: {cm[0,1]:,}")
    print(f"  False Negatives: {cm[1,0]:,}")
    print(f"  True Positives:  {cm[1,1]:,}")
    
    print("\nAll Models Comparison:")
    print(f"{'Model':<30} {'ROC-AUC':>10}")
    print("-" * 45)
    for name, metrics in results.items():
        print(f"{name:<30} {metrics['roc_auc']:>10.3f}")


def save_model(model, scaler, encoders, feature_names, optimal_threshold, output_path):
    os.makedirs(output_path, exist_ok=True)
    
    joblib.dump(model, os.path.join(output_path, 'heart_disease_model.pkl'))
    joblib.dump(scaler, os.path.join(output_path, 'scaler.pkl'))
    joblib.dump(encoders, os.path.join(output_path, 'encoders.pkl'))
    joblib.dump(feature_names, os.path.join(output_path, 'feature_names.pkl'))
    
    with open(os.path.join(output_path, 'optimal_threshold.txt'), 'w') as f:
        f.write(f"{optimal_threshold:.3f}\n")
    
    print(f"\nModel artifacts saved to {output_path}")


def main():
    parser = argparse.ArgumentParser(description='Train CVD prediction model')
    parser.add_argument('--dataset_path', type=str, 
                       default='/Users/filip/Desktop/NHANES 1988-2018 Archive/nhanes_cvd_training_data_IMPROVED.csv',
                       help='Path to training data CSV')
    parser.add_argument('--output_path', type=str, default='./models_improved',
                       help='Path to save trained model')
    parser.add_argument('--test_size', type=float, default=0.2,
                       help='Test set size (default: 0.2)')
    parser.add_argument('--random_state', type=int, default=42,
                       help='Random state for reproducibility')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.dataset_path):
        print(f"Error: Dataset not found at {args.dataset_path}")
        return
    
    X, y, feature_names, encoders = load_and_preprocess_data(args.dataset_path)
    
    print(f"Splitting data (test_size={args.test_size})...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=args.test_size, random_state=args.random_state, stratify=y
    )
    print(f"  Training: {len(X_train):,} samples, Test: {len(X_test):,} samples\n")
    
    print("Scaling features...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    print("  Features standardized\n")
    
    best_model, best_model_name, results = train_models(X_train_scaled, y_train, X_test_scaled, y_test)
    
    evaluate_model_detailed(best_model, best_model_name, results, y_test)
    
    optimal_threshold, threshold_results = optimize_threshold(best_model, scaler, X_test_scaled, y_test)
    
    print("Saving model...")
    save_model(best_model, scaler, encoders, feature_names, optimal_threshold, args.output_path)
    
    print("\nGenerating feature importance plot...")
    try:
        plot_path = os.path.join(args.output_path, 'feature_importance_cvd.png')
        plot_feature_importance(best_model, feature_names, output_path=plot_path)
    except Exception as e:
        print(f"Could not generate plot: {e}")
    
    opt_result = [r for r in threshold_results if r['threshold'] == optimal_threshold][0]
    print(f"\n{'='*60}")
    print("TRAINING COMPLETE!")
    print(f"{'='*60}")
    print(f"Dataset: {len(X):,} samples, {len(feature_names)} features")
    print(f"Best model: {best_model_name}")
    print(f"ROC-AUC: {results[best_model_name]['roc_auc']:.3f}")
    print(f"Optimal threshold: {optimal_threshold:.3f}")
    print(f"Recall: {opt_result['recall']:.1%}, Precision: {opt_result['precision']:.1%}")
    print(f"Model saved to: {args.output_path}")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
