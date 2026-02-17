"""
Script to plot feature importances from the trained heart disease prediction model.
Can be run standalone to generate the plot from an existing trained model.
"""
import matplotlib.pyplot as plt
import joblib
import numpy as np
import os
import argparse
from sklearn.ensemble import VotingClassifier


def get_feature_importance_from_model(model, feature_names):
    """
    Extract feature importances from a trained model.
    Handles VotingClassifier, RandomForest, GradientBoosting, and LogisticRegression.
    
    Args:
        model: Trained model (can be VotingClassifier, RandomForest, etc.)
        feature_names: List of feature names
    
    Returns:
        numpy array of feature importances (normalized to sum to 100)
    """
    if isinstance(model, VotingClassifier):
        # For ensemble, average the importances from constituent models
        importances_list = []
        
        for name, estimator in model.named_estimators_.items():
            if hasattr(estimator, 'feature_importances_'):
                importances_list.append(estimator.feature_importances_)
            elif hasattr(estimator, 'coef_'):
                # For LogisticRegression, use absolute coefficients
                coef = np.abs(estimator.coef_[0])
                importances_list.append(coef / coef.sum())
        
        if importances_list:
            # Average the importances
            avg_importances = np.mean(importances_list, axis=0)
        else:
            raise ValueError("Could not extract feature importances from ensemble")
    elif hasattr(model, 'feature_importances_'):
        # RandomForest, GradientBoosting, etc.
        avg_importances = model.feature_importances_
    elif hasattr(model, 'coef_'):
        # LogisticRegression
        coef = np.abs(model.coef_[0])
        avg_importances = coef / coef.sum()
    else:
        raise ValueError(f"Model type {type(model)} does not support feature importances")
    
    # Normalize to percentages (sum to 100)
    importances_percent = (avg_importances / avg_importances.sum()) * 100
    
    return importances_percent


def get_readable_feature_names(feature_names):
    """
    Map technical feature names to readable display names.
    
    Args:
        feature_names: List of technical feature names
    
    Returns:
        List of readable feature names
    """
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
    }
    
    readable_names = []
    for name in feature_names:
        readable_names.append(name_mapping.get(name, name.replace('_', ' ').title()))
    
    return readable_names


def plot_feature_importance(model_path, feature_names_path, output_path=None):
    """
    Load model and feature names, then plot feature importances.
    
    Args:
        model_path: Path to saved model (.pkl file)
        feature_names_path: Path to saved feature names (.pkl file)
        output_path: Optional path to save the figure (if None, displays it)
    """
    print(f"Loading model from {model_path}...")
    model = joblib.load(model_path)
    
    print(f"Loading feature names from {feature_names_path}...")
    feature_names = joblib.load(feature_names_path)
    
    print("Extracting feature importances...")
    importances = get_feature_importance_from_model(model, feature_names)
    
    readable_names = get_readable_feature_names(feature_names)
    
    # Sort by importance (descending)
    sorted_indices = np.argsort(importances)[::-1]
    sorted_importances = importances[sorted_indices]
    sorted_names = [readable_names[i] for i in sorted_indices]
    
    # Create the plot
    plt.figure(figsize=(10, 6))
    
    bars = plt.barh(
        sorted_names,
        sorted_importances,
        edgecolor="black",
        color='steelblue'
    )
    
    plt.xlabel("Relative Contribution to Risk Prediction (%)", fontsize=12)
    plt.title("Feature-Level Contributions to Heart Disease Risk Prediction", fontsize=14, fontweight='bold')
    
    # Set x-axis limit to accommodate the highest value
    max_importance = sorted_importances.max()
    plt.xlim(0, max_importance * 1.2)
    
    # Annotate bars with percentages
    for bar in bars:
        width = bar.get_width()
        plt.text(
            width + max_importance * 0.02,
            bar.get_y() + bar.get_height() / 2,
            f"{width:.1f}%",
            va="center",
            fontsize=10,
            fontweight='bold'
        )
    
    plt.gca().invert_yaxis()  # Most important features on top
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Figure saved to {output_path}")
    else:
        plt.show()
    
    # Print summary
    print("\n" + "="*60)
    print("Feature Importances Summary:")
    print("="*60)
    for name, imp in zip(sorted_names, sorted_importances):
        print(f"{name:35s}: {imp:6.2f}%")
    print("="*60)


def main():
    parser = argparse.ArgumentParser(description='Plot feature importances from trained model')
    parser.add_argument('--model_path', type=str, default='./models/heart_disease_model.pkl',
                        help='Path to trained model file')
    parser.add_argument('--feature_names_path', type=str, default='./models/feature_names.pkl',
                        help='Path to feature names file')
    parser.add_argument('--output', type=str, default=None,
                        help='Path to save figure (if not provided, displays it)')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.model_path):
        print(f"Error: Model file not found at {args.model_path}")
        print("Please train the model first using train_model.py")
        return
    
    if not os.path.exists(args.feature_names_path):
        print(f"Error: Feature names file not found at {args.feature_names_path}")
        return
    
    plot_feature_importance(args.model_path, args.feature_names_path, args.output)


if __name__ == '__main__':
    main()
