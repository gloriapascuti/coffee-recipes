# Coffee Recipe Website

A full-stack web application for discovering, creating, and sharing coffee recipes, with a built-in heart disease risk assessment tool based on caffeine consumption patterns.

## What it does

Users can create and browse coffee recipes, track their daily caffeine intake, and get a heart disease risk prediction based on their health profile and consumption habits. The prediction is powered by a logistic regression model trained on a synthetic dataset modeled after real-world distributions.

There's also a community section where users can post challenges, vote on recipes, and receive notifications.

## Tech stack

**Frontend** — React, React Router, Context API, Chart.js

**Backend** — Django, Django REST Framework, JWT authentication with 2FA support

**ML model** — Scikit-learn (Logistic Regression), trained on 5,000 synthetic samples

**Deployment** — Render (backend + frontend), PostgreSQL

## Running locally

**Backend**
```bash
cd backend/coffee_backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

**Frontend**
```bash
npm install
npm start
```

The API runs at `http://127.0.0.1:8000/api` and the frontend at `http://localhost:3000`.

## ML model

The heart disease risk model uses 24 features including age, sex, BMI, average daily caffeine, weekly caffeine total, systolic and diastolic blood pressure, cholesterol levels, hypertension, diabetes, family history of CHD, smoking status, and activity level. Best performing model: Gradient Boosting, trained on 59,057 samples.

| Metric | Value |
|--------|-------|
| ROC-AUC | 0.817 |
| MCC | 0.075 |
| Recall | 49.1% |
| Precision | 24.3% |
| Optimal threshold | 0.150 |

To retrain the model:
```bash
cd thesis_model
python trained_model.py --output_path ../backend/coffee_backend/ml_models
```

Risk predictions are for informational purposes only and are not a substitute for medical advice.

## Project structure

```
coffee-website/
├── backend/coffee_backend/   # Django API
│   ├── coffee/               # Recipes, predictions, challenges
│   ├── users/                # Auth, health profiles
│   └── ml_models/            # Trained model files (.pkl)
├── src/                      # React frontend
│   ├── Page1/                # Home, recipe cards
│   ├── Page2/                # Browse & filter recipes
│   ├── Page3/                # My recipes
│   ├── Page4/                # Health tracking & predictions
│   └── authentication/       # Login, register, 2FA
├── thesis_model/             # Model training script
└── thesis_dataset/           # Training data
```

---

Bachelor's thesis project — Babeș-Bolyai University
