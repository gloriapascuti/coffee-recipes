# Heart Disease Prediction Model Training

This directory contains scripts for training a machine learning model to predict heart disease risk based on caffeine intake and health profile data.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Train the model with default settings:
```bash
python train_model.py
```

Train with custom dataset path and output directory:
```bash
python train_model.py --dataset_path ../thesis_dataset/Data --output_path ./models
```

## Model Output

The training script will save:
- `heart_disease_model.pkl` - The trained model
- `scaler.pkl` - StandardScaler for feature normalization
- `encoders.pkl` - Label encoders for categorical variables
- `feature_names.pkl` - List of feature names in order

## Integration with Django

To use the trained model in the Django backend:

1. Copy the model files to `backend/coffee_backend/coffee/models/ml/`
2. Update `coffee/views.py` `generate_prediction` function to load and use the model
3. Ensure feature engineering matches the training pipeline

## Notes

- Currently uses synthetic data for demonstration
- Replace `load_and_preprocess_data()` with actual NHANES dataset loading
- Feature engineering should match what's collected in the app (caffeine stats, health profile, BP)
