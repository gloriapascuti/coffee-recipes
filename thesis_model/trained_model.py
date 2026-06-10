"""
Usage:
    python trained_model.py
    python trained_model.py --dataset_path /path/to/data.csv --output_path ./models
    python trained_model.py --final_model "Gradient Boosting"
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, precision_score, recall_score, f1_score,
                            roc_auc_score, confusion_matrix, matthews_corrcoef)
import joblib
import os
import argparse
import warnings
from datetime import datetime
warnings.filterwarnings('ignore')


def load_and_preprocess_data(dataset_path):
    df = pd.read_csv(dataset_path)
    print(f"Loaded {len(df):,} records")

    n_cvd_deaths = int(df['cvd_death'].sum())
    print(f"CVD deaths: {n_cvd_deaths:,} ({n_cvd_deaths / len(df) * 100:.2f}%)")

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

    for col in feature_cols:
        if df[col].isna().sum() > 0:
            if df[col].dtype in ['int64', 'float64']:
                df[col] = df[col].fillna(df[col].median())
            else:
                df[col] = df[col].fillna(df[col].mode()[0])

    X = df[feature_cols].values
    y = df['cvd_death'].values

    print(f"Final dataset: {len(X):,} samples x {len(feature_cols)} features\n")

    encoders = {'sex': le_sex, 'activity_level': le_activity}
    return X, y, feature_cols, encoders


def split_data_3way(X, y, test_size=0.20, val_size=0.20, random_state=42):
    X_trainval, X_test, y_trainval, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )

    val_relative = val_size / (1.0 - test_size)
    X_train, X_val, y_train, y_val = train_test_split(
        X_trainval, y_trainval, test_size=val_relative,
        random_state=random_state, stratify=y_trainval
    )

    n = len(y)
    print("Stratified 3-way split:")
    print(f"  Train:      {len(y_train):>7,} ({len(y_train) / n * 100:5.1f}%) - {int(y_train.sum()):>5,} CVD deaths ({y_train.mean() * 100:.2f}%)")
    print(f"  Validation: {len(y_val):>7,} ({len(y_val) / n * 100:5.1f}%) - {int(y_val.sum()):>5,} CVD deaths ({y_val.mean() * 100:.2f}%)")
    print(f"  Test:       {len(y_test):>7,} ({len(y_test) / n * 100:5.1f}%) - {int(y_test.sum()):>5,} CVD deaths ({y_test.mean() * 100:.2f}%)\n")

    return X_train, X_val, X_test, y_train, y_val, y_test


def _evaluate_on(model, X, y, threshold=0.5):
    y_pred_proba = model.predict_proba(X)[:, 1]
    y_pred = (y_pred_proba >= threshold).astype(int)
    return {
        'y_pred': y_pred,
        'y_pred_proba': y_pred_proba,
        'accuracy': accuracy_score(y, y_pred),
        'precision': precision_score(y, y_pred, zero_division=0),
        'recall': recall_score(y, y_pred, zero_division=0),
        'f1': f1_score(y, y_pred, zero_division=0),
        'roc_auc': roc_auc_score(y, y_pred_proba),
        'mcc': matthews_corrcoef(y, y_pred),
    }


def train_all_models(X_train, y_train, X_val, y_val):
    print("Training models on the train split...")

    rf = RandomForestClassifier(
        n_estimators=400, max_depth=10, min_samples_leaf=4, min_samples_split=4,
        random_state=42, n_jobs=-1, class_weight='balanced'
    )
    gb = GradientBoostingClassifier(
        n_estimators=350, max_depth=3, learning_rate=0.05, random_state=42
    )
    lr = LogisticRegression(
        C=1.0, max_iter=3000, random_state=42, class_weight='balanced', solver='lbfgs'
    )

    models = {'Logistic Regression': lr, 'Random Forest': rf, 'Gradient Boosting': gb}

    results = {}
    for name, model in models.items():
        print(f"  Training {name}...")
        model.fit(X_train, y_train)

        y_pred = model.predict(X_val)
        y_pred_proba = model.predict_proba(X_val)[:, 1]

        results[name] = {
            'model': model,
            'accuracy': accuracy_score(y_val, y_pred),
            'precision': precision_score(y_val, y_pred, zero_division=0),
            'recall': recall_score(y_val, y_pred, zero_division=0),
            'f1': f1_score(y_val, y_pred, zero_division=0),
            'roc_auc': roc_auc_score(y_val, y_pred_proba),
            'mcc': matthews_corrcoef(y_val, y_pred),
        }
        print(f"    [val] ROC-AUC = {results[name]['roc_auc']:.3f}, F1 = {results[name]['f1']:.3f}, Recall = {results[name]['recall']:.3f}")

    print("  Training Ensemble (RF + GB, soft voting)...")
    ensemble = VotingClassifier(estimators=[('rf', rf), ('gb', gb)], voting='soft', weights=[1.0, 1.0])
    ensemble.fit(X_train, y_train)

    y_pred = ensemble.predict(X_val)
    y_pred_proba = ensemble.predict_proba(X_val)[:, 1]

    results['Ensemble (RF + GB)'] = {
        'model': ensemble,
        'accuracy': accuracy_score(y_val, y_pred),
        'precision': precision_score(y_val, y_pred, zero_division=0),
        'recall': recall_score(y_val, y_pred, zero_division=0),
        'f1': f1_score(y_val, y_pred, zero_division=0),
        'roc_auc': roc_auc_score(y_val, y_pred_proba),
        'mcc': matthews_corrcoef(y_val, y_pred),
    }
    print(f"    [val] ROC-AUC = {results['Ensemble (RF + GB)']['roc_auc']:.3f}, F1 = {results['Ensemble (RF + GB)']['f1']:.3f}, Recall = {results['Ensemble (RF + GB)']['recall']:.3f}")

    return results


def select_threshold_on_validation(model, X_val, y_val):
    print("Selecting classification threshold on validation set...")

    y_pred_proba = model.predict_proba(X_val)[:, 1]
    thresholds = [0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50]
    rows = []

    print(f"\n  {'tau':<6} {'Recall':<8} {'Prec':<8} {'F1':<8} {'MCC':<8} {'TP':<6} {'FP':<6}")
    print("  " + "-" * 56)
    for tau in thresholds:
        y_pred = (y_pred_proba >= tau).astype(int)

        recall = recall_score(y_val, y_pred, zero_division=0)
        precision = precision_score(y_val, y_pred, zero_division=0)
        f1 = f1_score(y_val, y_pred, zero_division=0)
        mcc = matthews_corrcoef(y_val, y_pred)

        true_positives = ((y_val == 1) & (y_pred == 1)).sum()
        false_positives = ((y_val == 0) & (y_pred == 1)).sum()

        rows.append({
            'threshold': tau, 'recall': recall, 'precision': precision,
            'f1': f1, 'mcc': mcc, 'tp': int(true_positives), 'fp': int(false_positives)
        })
        print(f"  {tau:<6.2f} {recall:<8.3f} {precision:<8.3f} {f1:<8.3f} {mcc:<8.3f} {int(true_positives):<6d} {int(false_positives):<6d}")

    best = max(rows, key=lambda x: x['f1'])
    print(f"\n  Optimal threshold (max F1): tau = {best['threshold']:.2f}")
    print(f"  Recall = {best['recall']:.1%}, Precision = {best['precision']:.1%}, F1 = {best['f1']:.3f}\n")

    return best['threshold'], rows


def final_test_evaluation(model, threshold, X_test, y_test, model_name):
    print("=" * 60)
    print(f"FINAL TEST-SET EVALUATION - {model_name} @ tau = {threshold:.2f}")
    print("=" * 60)

    y_pred_proba = model.predict_proba(X_test)[:, 1]
    y_pred = (y_pred_proba >= threshold).astype(int)

    metrics = {
        'accuracy': accuracy_score(y_test, y_pred),
        'precision': precision_score(y_test, y_pred, zero_division=0),
        'recall': recall_score(y_test, y_pred, zero_division=0),
        'f1': f1_score(y_test, y_pred, zero_division=0),
        'roc_auc': roc_auc_score(y_test, y_pred_proba),
        'mcc': matthews_corrcoef(y_test, y_pred),
    }
    cm = confusion_matrix(y_test, y_pred)

    print(f"  Accuracy:  {metrics['accuracy']:.3f}")
    print(f"  Precision: {metrics['precision']:.3f}")
    print(f"  Recall:    {metrics['recall']:.3f}")
    print(f"  F1-Score:  {metrics['f1']:.3f}")
    print(f"  ROC-AUC:   {metrics['roc_auc']:.3f}")
    print(f"  MCC:       {metrics['mcc']:.3f}")
    print(f"\n  Confusion Matrix [test set]:")
    print(f"    TN = {cm[0, 0]:>5,}   FP = {cm[0, 1]:>5,}")
    print(f"    FN = {cm[1, 0]:>5,}   TP = {cm[1, 1]:>5,}\n")

    return metrics, cm


def get_feature_importance_from_model(model, feature_names):
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
    bars = plt.barh(sorted_names, sorted_importances, edgecolor='black', color='steelblue')
    plt.xlabel("Relative Contribution to CVD Risk Prediction (%)", fontsize=12)
    plt.title("Feature Contributions to CVD Death Prediction", fontsize=14, fontweight='bold')

    max_importance = sorted_importances.max()
    plt.xlim(0, max_importance * 1.2)

    for bar in bars:
        width = bar.get_width()
        plt.text(width + max_importance * 0.02, bar.get_y() + bar.get_height() / 2,
                 f"{width:.1f}%", va='center', fontsize=10, fontweight='bold')

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


def save_model(model, scaler, encoders, feature_names, optimal_threshold, output_path):
    os.makedirs(output_path, exist_ok=True)

    joblib.dump(model, os.path.join(output_path, 'heart_disease_model.pkl'))
    joblib.dump(scaler, os.path.join(output_path, 'scaler.pkl'))
    joblib.dump(encoders, os.path.join(output_path, 'encoders.pkl'))
    joblib.dump(feature_names, os.path.join(output_path, 'feature_names.pkl'))

    with open(os.path.join(output_path, 'optimal_threshold.txt'), 'w') as f:
        f.write(f"{optimal_threshold:.3f}\n")

    print(f"\nModel artifacts saved to {output_path}")


def save_run_metrics(results, final_model_name, test_metrics, threshold_results, optimal_threshold,
                     output_path, dataset_path, n_samples, n_features, split_config, random_state):
    os.makedirs(output_path, exist_ok=True)
    timestamp = datetime.utcnow().isoformat()

    model_rows = []
    for name, metrics in results.items():
        model_rows.append({
            'timestamp': timestamp,
            'dataset_path': dataset_path,
            'n_samples': n_samples,
            'n_features': n_features,
            'split_config': split_config,
            'random_state': random_state,
            'split': 'validation',
            'model_name': name,
            'accuracy': metrics['accuracy'],
            'precision': metrics['precision'],
            'recall': metrics['recall'],
            'f1': metrics['f1'],
            'roc_auc': metrics['roc_auc'],
            'mcc': metrics['mcc'],
            'is_final_model': int(name == final_model_name),
        })

    model_rows.append({
        'timestamp': timestamp,
        'dataset_path': dataset_path,
        'n_samples': n_samples,
        'n_features': n_features,
        'split_config': split_config,
        'random_state': random_state,
        'split': 'test',
        'model_name': final_model_name,
        'accuracy': test_metrics['accuracy'],
        'precision': test_metrics['precision'],
        'recall': test_metrics['recall'],
        'f1': test_metrics['f1'],
        'roc_auc': test_metrics['roc_auc'],
        'mcc': test_metrics['mcc'],
        'is_final_model': 1,
    })

    model_metrics_path = os.path.join(output_path, 'model_metrics.csv')
    pd.DataFrame(model_rows).to_csv(
        model_metrics_path, mode='a',
        header=not os.path.exists(model_metrics_path), index=False
    )

    threshold_rows = []
    for r in threshold_results:
        threshold_rows.append({
            'timestamp': timestamp,
            'dataset_path': dataset_path,
            'n_samples': n_samples,
            'n_features': n_features,
            'split_config': split_config,
            'random_state': random_state,
            'final_model_name': final_model_name,
            'best_threshold': optimal_threshold,
            'threshold': r['threshold'],
            'recall': r['recall'],
            'precision': r['precision'],
            'f1': r['f1'],
            'mcc': r['mcc'],
            'true_positives': r['tp'],
            'false_positives': r['fp'],
        })

    thresholds_path = os.path.join(output_path, 'threshold_metrics.csv')
    pd.DataFrame(threshold_rows).to_csv(
        thresholds_path, mode='a',
        header=not os.path.exists(thresholds_path), index=False
    )

    print(f"\nRun metrics appended to:")
    print(f"  - {model_metrics_path}")
    print(f"  - {thresholds_path}")


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    default_data = os.path.join(here, 'data', 'nhanes_cvd_training_data.csv')
    default_out = os.path.join(here, 'models')

    parser = argparse.ArgumentParser(description='Train CVD prediction model')
    parser.add_argument('--dataset_path', type=str, default=default_data)
    parser.add_argument('--output_path', type=str, default=default_out)
    parser.add_argument('--test_size', type=float, default=0.20)
    parser.add_argument('--val_size', type=float, default=0.20)
    parser.add_argument('--random_state', type=int, default=42)
    parser.add_argument('--final_model', type=str, default='Gradient Boosting',
                        choices=['Logistic Regression', 'Random Forest',
                                 'Gradient Boosting', 'Ensemble (RF + GB)'])
    args = parser.parse_args()

    if not os.path.exists(args.dataset_path):
        print(f"Error: Dataset not found at {args.dataset_path}")
        return

    X, y, feature_names, encoders = load_and_preprocess_data(args.dataset_path)

    print(f"Splitting data (train/val/test)...")
    X_train, X_val, X_test, y_train, y_val, y_test = split_data_3way(
        X, y, test_size=args.test_size, val_size=args.val_size, random_state=args.random_state
    )

    print("Scaling features...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_val_scaled = scaler.transform(X_val)
    X_test_scaled = scaler.transform(X_test)
    print("  Features standardized\n")

    results = train_all_models(X_train_scaled, y_train, X_val_scaled, y_val)

    print("\nValidation-set comparison:")
    print(f"  {'Model':<25} {'ROC-AUC':>8} {'F1':>8} {'Recall':>8}")
    for name, r in results.items():
        print(f"  {name:<25} {r['roc_auc']:>8.3f} {r['f1']:>8.3f} {r['recall']:>8.3f}")

    final_model = results[args.final_model]['model']
    print(f"\nFinal model: {args.final_model}")

    optimal_threshold, threshold_results = select_threshold_on_validation(final_model, X_val_scaled, y_val)

    test_metrics, _ = final_test_evaluation(final_model, optimal_threshold, X_test_scaled, y_test, args.final_model)

    save_model(final_model, scaler, encoders, feature_names, optimal_threshold, args.output_path)

    split_config = f"{1 - args.test_size - args.val_size:.0%}/{args.val_size:.0%}/{args.test_size:.0%}"
    save_run_metrics(results, args.final_model, test_metrics, threshold_results, optimal_threshold,
                     args.output_path, args.dataset_path, len(X), len(feature_names),
                     split_config, args.random_state)

    print("\nGenerating feature importance plot...")
    try:
        plot_path = os.path.join(args.output_path, 'feature_importance_cvd.png')
        plot_feature_importance(final_model, feature_names, output_path=plot_path)
    except Exception as e:
        print(f"Could not generate plot: {e}")

    print(f"\n{'='*60}")
    print("TRAINING COMPLETE!")
    print(f"{'='*60}")
    print(f"Dataset: {len(X):,} samples, {len(feature_names)} features")
    print(f"Best model: {args.final_model}")
    print(f"ROC-AUC: {test_metrics['roc_auc']:.3f}")
    print(f"MCC: {test_metrics['mcc']:.3f}")
    print(f"Optimal threshold: {optimal_threshold:.3f}")
    print(f"Model saved to: {args.output_path}")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
