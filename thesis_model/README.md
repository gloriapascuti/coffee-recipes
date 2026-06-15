# Heart Disease Prediction Model Training

This directory contains scripts for training a Gradient Boosting model to predict cardiovascular disease risk from NHANES-derived health data and caffeine intake.

## Setup

```bash
pip install -r requirements.txt
```

## Data Pipeline

1. Raw NHANES data lives in `../thesis_dataset/Data/`
2. Prepare the training CSV:

```bash
python data/prep/prepare_training_data.py
```

Output: `data/nhanes_cvd_training_data.csv`

## Train the Model

```bash
python trained_model.py --output_path ./models
```

Copy artifacts to the Django backend for production inference:

```bash
python trained_model.py --output_path ../backend/coffee_backend/ml_models
```

## Model Output

The training script saves to the output directory:

- `heart_disease_model.pkl` — trained Gradient Boosting classifier
- `scaler.pkl` — StandardScaler for feature normalization
- `encoders.pkl` — label encoders for categorical variables
- `feature_names.pkl` — ordered feature list used at inference time
- `optimal_threshold.txt` — tuned decision threshold (τ = 0.15)
- `model_metrics.csv`, `threshold_metrics.csv` — evaluation metrics
- `feature_importance_cvd.png` — feature importance chart

## Experiments

Thesis experiment suite (model comparison, hyperparameter tuning, post-processing):

```bash
python experiments/run_experiments.py
```

Results are saved to `experiments/outputs/`. `CANONICAL_REFERENCE.json` is the authoritative source for thesis metrics.

## Integration with Django

Production model artifacts live in `backend/coffee_backend/ml_models/`. Inference is handled by `coffee/ml_model_utils.py` and exposed via the prediction API in `coffee/views.py`.
