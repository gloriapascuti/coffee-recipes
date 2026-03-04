"""
Generate evaluation figures for thesis Chapter 5.
Run this from the thesis_model/ directory.

Usage:
    python generate_eval_figures.py \
        --dataset /path/to/nhanes_cvd_training_data_IMPROVED.csv \
        --models_dir ./models_improved \
        --output_dir ./models_improved
"""

import argparse
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['font.family'] = 'DejaVu Sans'

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, confusion_matrix, roc_curve
)
import os
import warnings
warnings.filterwarnings('ignore')


def load_data(dataset_path, encoders):
    df = pd.read_csv(dataset_path)
    print(f"Loaded {len(df):,} records")
    print(f"CVD deaths: {df['cvd_death'].sum():,} ({df['cvd_death'].mean()*100:.2f}%)")

    df['sex_encoded'] = encoders['sex'].transform(df['sex'])
    df['activity_level_encoded'] = encoders['activity_level'].transform(df['activity_level'])

    feature_cols = [
        'age', 'sex_encoded', 'bmi',
        'avg_daily_caffeine_mg', 'total_caffeine_week_mg',
        'systolic_bp', 'diastolic_bp',
        'has_hypertension', 'has_diabetes', 'has_family_history_chd',
        'is_smoker', 'activity_level_encoded', 'has_high_cholesterol',
        'total_cholesterol', 'hdl_cholesterol', 'ldl_cholesterol',
        'triglycerides', 'glucose',
        'caffeine_per_kg', 'caffeine_per_bmi', 'caffeine_category',
        'caffeine_age_interaction', 'caffeine_hypertension_interaction',
        'is_high_caffeine',
    ]

    # Keep only columns that exist in this dataset
    feature_cols = [c for c in feature_cols if c in df.columns]

    X = df[feature_cols].values
    y = df['cvd_death'].values

    _, X_test, _, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    return X_test, y_test, feature_cols, df, y


def plot_confusion_matrices(y_test, proba, output_dir):
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle('Confusion Matrices — Gradient Boosting Classifier',
                 fontsize=13, fontweight='bold', y=1.02)

    def draw_cm(ax, threshold, title):
        pred = (proba >= threshold).astype(int)
        cm = confusion_matrix(y_test, pred)
        tn, fp, fn, tp = cm.ravel()
        matrix = np.array([[tn, fp], [fn, tp]])
        rec = tp / (tp + fn) if (tp + fn) > 0 else 0
        pre = tp / (tp + fp) if (tp + fp) > 0 else 0
        im = ax.imshow(matrix, cmap='Blues')
        ax.set_title(f'{title}\nRecall: {rec:.1%}  Precision: {pre:.1%}',
                     fontsize=10, fontweight='bold', pad=10)
        ax.set_xticks([0, 1])
        ax.set_yticks([0, 1])
        ax.set_xticklabels(['Predicted\nNegative', 'Predicted\nPositive'], fontsize=9)
        ax.set_yticklabels(['Actual\nNegative', 'Actual\nPositive'], fontsize=9)
        ax.set_xlabel('Predicted label', fontsize=10)
        ax.set_ylabel('True label', fontsize=10)
        total = matrix.sum()
        for i in range(2):
            for j in range(2):
                val = matrix[i, j]
                color = 'white' if val > matrix.max() / 2 else 'black'
                ax.text(j, i, f'{val:,}\n({val/total*100:.1f}%)',
                        ha='center', va='center', fontsize=11,
                        fontweight='bold', color=color)
        plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

    draw_cm(axes[0], 0.50, 'Default threshold τ = 0.50')
    draw_cm(axes[1], 0.15, 'Optimised threshold τ = 0.15')

    plt.tight_layout()
    out = os.path.join(output_dir, 'confusion_matrices.png')
    plt.savefig(out, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Saved {out}")


def plot_roc_curves(y_test, all_probas, output_dir):
    fig, ax = plt.subplots(figsize=(8, 7))
    colors = {
        'Gradient Boosting':    ('#e74c3c', '-'),
        'Logistic Regression':  ('#2c7bb6', '--'),
        'Ensemble (RF + GB)':   ('#27ae60', '-.'),
        'Random Forest':        ('#f39c12', ':'),
    }
    for name, proba in all_probas.items():
        fpr, tpr, _ = roc_curve(y_test, proba)
        auc = roc_auc_score(y_test, proba)
        color, ls = colors[name]
        ax.plot(fpr, tpr, color=color, linestyle=ls, linewidth=2.2,
                label=f'{name} (AUC = {auc:.3f})')

    ax.plot([0, 1], [0, 1], 'k--', linewidth=1, alpha=0.5,
            label='Random classifier (AUC = 0.500)')
    ax.set_xlabel('False Positive Rate', fontsize=12)
    ax.set_ylabel('True Positive Rate', fontsize=12)
    ax.set_title('ROC Curves — All Models', fontsize=13, fontweight='bold')
    ax.legend(loc='lower right', fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_xlim([0, 1])
    ax.set_ylim([0, 1])

    plt.tight_layout()
    out = os.path.join(output_dir, 'roc_curves.png')
    plt.savefig(out, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Saved {out}")


def plot_threshold_optimization(y_test, proba, output_dir):
    thresholds = [0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50]
    recalls, precisions, f1s = [], [], []

    print(f"\n{'Threshold':<12} {'Recall':<10} {'Precision':<12} {'F1':<10} {'TP':<8} {'FP':<8}")
    print("-" * 60)
    for t in thresholds:
        pred = (proba >= t).astype(int)
        rec = recall_score(y_test, pred, zero_division=0)
        pre = precision_score(y_test, pred, zero_division=0)
        f1 = f1_score(y_test, pred, zero_division=0)
        tp = int(((y_test == 1) & (pred == 1)).sum())
        fp = int(((y_test == 0) & (pred == 1)).sum())
        recalls.append(rec)
        precisions.append(pre)
        f1s.append(f1)
        print(f"{t:<12.2f} {rec:<10.3f} {pre:<12.3f} {f1:<10.3f} {tp:<8d} {fp:<8d}")

    best_t = thresholds[np.argmax(f1s)]

    fig, ax = plt.subplots(figsize=(9, 6))
    ax.plot(thresholds, recalls,    'b-o', label='Recall',     linewidth=2, markersize=7)
    ax.plot(thresholds, precisions, 'r-s', label='Precision',  linewidth=2, markersize=7)
    ax.plot(thresholds, f1s,        'g-^', label='F1-Score',   linewidth=2, markersize=7)
    ax.axvline(x=best_t, color='purple', linestyle='--', linewidth=1.8,
               label=f'Optimal threshold τ = {best_t:.2f}')
    ax.set_xlabel('Classification Threshold', fontsize=12)
    ax.set_ylabel('Score', fontsize=12)
    ax.set_title('Threshold Optimisation — Precision / Recall / F1 Trade-off',
                 fontsize=13, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    ax.set_xlim([0.03, 0.52])
    ax.set_ylim([0, 1.0])

    plt.tight_layout()
    out = os.path.join(output_dir, 'threshold_optimization.png')
    plt.savefig(out, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Saved {out}")


def plot_feature_importance(gb_model, feature_cols, output_dir):
    importances = gb_model.feature_importances_
    indices = np.argsort(importances)[::-1]

    labels = {
        'age':                              'Age',
        'sex_encoded':                      'Sex',
        'bmi':                              'BMI',
        'avg_daily_caffeine_mg':            'Avg Daily Caffeine',
        'total_caffeine_week_mg':           'Total Weekly Caffeine',
        'systolic_bp':                      'Systolic BP',
        'diastolic_bp':                     'Diastolic BP',
        'has_hypertension':                 'Hypertension',
        'has_diabetes':                     'Diabetes',
        'has_family_history_chd':           'Family History CHD',
        'is_smoker':                        'Smoker',
        'activity_level_encoded':           'Activity Level',
        'has_high_cholesterol':             'High Cholesterol',
        'total_cholesterol':                'Total Cholesterol',
        'hdl_cholesterol':                  'HDL Cholesterol',
        'ldl_cholesterol':                  'LDL Cholesterol',
        'triglycerides':                    'Triglycerides',
        'glucose':                          'Glucose',
        'caffeine_per_kg':                  'Caffeine Per Kg',
        'caffeine_per_bmi':                 'Caffeine Per BMI',
        'caffeine_category':                'Caffeine Category',
        'caffeine_age_interaction':         'Caffeine–Age Interaction',
        'caffeine_hypertension_interaction':'Caffeine–Hypertension Interaction',
        'is_high_caffeine':                 'High Caffeine Flag',
    }

    caffeine_features = {
        'avg_daily_caffeine_mg', 'total_caffeine_week_mg',
        'caffeine_per_kg', 'caffeine_per_bmi', 'caffeine_category',
        'caffeine_age_interaction', 'caffeine_hypertension_interaction',
        'is_high_caffeine',
    }

    fig, ax = plt.subplots(figsize=(11, 8))
    colors = ['#c0392b' if feature_cols[i] in caffeine_features else '#2c7bb6'
              for i in indices]
    bars = ax.barh(
        [labels.get(feature_cols[i], feature_cols[i]) for i in indices],
        importances[indices] * 100,
        color=colors, edgecolor='white', linewidth=0.5
    )
    ax.set_xlabel('Feature Importance (%)', fontsize=12)
    ax.set_title('Feature Importance — Gradient Boosting Classifier',
                 fontsize=13, fontweight='bold')
    ax.invert_yaxis()
    for bar, val in zip(bars, importances[indices] * 100):
        ax.text(val + 0.2, bar.get_y() + bar.get_height() / 2,
                f'{val:.1f}%', va='center', fontsize=9)
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#2c7bb6', label='Clinical / demographic features'),
        Patch(facecolor='#c0392b', label='Caffeine features'),
    ]
    ax.legend(handles=legend_elements, loc='lower right', fontsize=10)
    ax.grid(axis='x', alpha=0.3)
    plt.tight_layout()
    out = os.path.join(output_dir, 'feature_importance_cvd.png')
    plt.savefig(out, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Saved {out}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset', required=True,
                        help='Path to nhanes_cvd_training_data_IMPROVED.csv')
    parser.add_argument('--models_dir', default='./models_improved',
                        help='Directory containing .pkl model files')
    parser.add_argument('--output_dir', default='./models_improved',
                        help='Directory to save generated figures')
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    print("Loading models...")
    gb      = joblib.load(os.path.join(args.models_dir, 'heart_disease_model.pkl'))
    scaler  = joblib.load(os.path.join(args.models_dir, 'scaler.pkl'))
    encoders = joblib.load(os.path.join(args.models_dir, 'encoders.pkl'))

    print("Preparing test data...")
    X_test, y_test, feature_cols, df, y_all = load_data(args.dataset, encoders)
    X_test_s = scaler.transform(X_test)

    gb_proba = gb.predict_proba(X_test_s)[:, 1]

    print("\nRetraining supporting models for ROC comparison...")
    X_all = df[feature_cols].values
    X_train, _, y_train, _ = train_test_split(
        X_all, y_all, test_size=0.2, random_state=42, stratify=y_all
    )
    X_train_s = scaler.transform(X_train)

    from sklearn.ensemble import RandomForestClassifier, VotingClassifier
    from sklearn.linear_model import LogisticRegression

    lr = LogisticRegression(max_iter=3000, random_state=42,
                             class_weight='balanced', solver='lbfgs')
    rf = RandomForestClassifier(n_estimators=400, random_state=42, n_jobs=-1,
                                 class_weight='balanced', max_depth=14,
                                 min_samples_split=4, min_samples_leaf=2)
    ensemble = VotingClassifier(estimators=[('rf', rf), ('gb', gb)], voting='soft')

    lr.fit(X_train_s, y_train)
    rf.fit(X_train_s, y_train)
    ensemble.fit(X_train_s, y_train)

    all_probas = {
        'Gradient Boosting':   gb_proba,
        'Logistic Regression': lr.predict_proba(X_test_s)[:, 1],
        'Random Forest':       rf.predict_proba(X_test_s)[:, 1],
        'Ensemble (RF + GB)':  ensemble.predict_proba(X_test_s)[:, 1],
    }

    print("\n=== FINAL METRICS AT τ=0.50 ===")
    for name, proba in all_probas.items():
        pred = (proba >= 0.50).astype(int)
        print(f"{name}: AUC={roc_auc_score(y_test, proba):.3f} "
              f"Acc={accuracy_score(y_test, pred):.3f} "
              f"Rec={recall_score(y_test, pred, zero_division=0):.3f} "
              f"Pre={precision_score(y_test, pred, zero_division=0):.3f} "
              f"F1={f1_score(y_test, pred, zero_division=0):.3f}")

    print("\n=== GENERATING FIGURES ===")
    plot_confusion_matrices(y_test, gb_proba, args.output_dir)
    plot_roc_curves(y_test, all_probas, args.output_dir)
    plot_threshold_optimization(y_test, gb_proba, args.output_dir)
    plot_feature_importance(gb, feature_cols, args.output_dir)

    print("\nAll figures saved to:", args.output_dir)


if __name__ == '__main__':
    main()
