# Coffee Recipe Website with ML-Powered Health Risk Assessment

A comprehensive web application for coffee enthusiasts to discover, create, and share coffee recipes, with integrated machine learning-based heart disease risk assessment based on caffeine consumption patterns.

## 🌟 Overview

This application combines a social coffee recipe platform with advanced health analytics. Users can:
- Create and share custom coffee recipes
- Track their coffee consumption
- Get personalized heart disease risk predictions using machine learning
- Monitor health trends over time

## ✨ Key Features

### Coffee Management
- **Recipe Creation**: Create custom coffee recipes with detailed brewing instructions
- **Recipe Discovery**: Browse thousands of recipes from the community
- **Favorites System**: Like and save your favorite recipes
- **Origin Filtering**: Filter recipes by coffee origin
- **Community Challenges**: Participate in coffee brewing challenges
- **File Uploads**: Upload recipe instructions, images, and videos

### Health & Analytics
- **ML-Powered Risk Assessment**: Get heart disease risk predictions using a trained machine learning model
- **Caffeine Tracking**: Track daily and weekly caffeine consumption
- **Health Profile**: Maintain comprehensive health profiles (age, BMI, blood pressure, medical history)
- **Trend Analysis**: View risk trends over time with visual indicators
- **Personalized Insights**: Receive AI-generated medical analysis and recommendations

### User Experience
- **Real-time Validation**: Input validation with helpful tooltips
- **Visual Feedback**: Loading animations, trend indicators, and progress tracking
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Offline Support**: Basic offline functionality for viewing cached data

## 🏗️ Architecture

### Frontend
- **Framework**: React.js with React Router
- **State Management**: Context API for global state
- **Styling**: CSS Modules for component-scoped styles
- **Components**: Modular component architecture

### Backend
- **Framework**: Django REST Framework
- **Database**: SQLite (development) / PostgreSQL (production ready)
- **Authentication**: JWT-based authentication with 2FA support
- **ML Integration**: Scikit-learn models loaded via joblib

### Machine Learning
- **Model Type**: Logistic Regression (best performing)
- **Training Data**: Realistic synthetic dataset (5,000 samples)
- **Features**: Age, sex, BMI, caffeine intake, blood pressure, health conditions
- **Performance**: ROC-AUC: 0.999, Accuracy: 97.3%, F1-Score: 0.932

## 🤖 Machine Learning Model Training

### Overview

The application uses a trained machine learning model to predict heart disease risk based on:
- User demographics (age, sex, BMI)
- Caffeine consumption patterns (daily average, weekly total)
- Blood pressure readings (systolic, diastolic)
- Health conditions (hypertension, diabetes, family history, smoking)
- Activity level

### Training Process

#### 1. Data Generation

The model is trained on a realistic synthetic dataset that mimics real-world distributions:

- **Sample Size**: 5,000 samples
- **Age Distribution**: Weighted towards middle age (30-69 years)
- **Caffeine Intake**: Exponential distribution (mean ~100mg/day, capped at 800mg)
- **Blood Pressure**: Age-correlated with realistic variance
- **Health Conditions**: Age-dependent probabilities for hypertension and diabetes

#### 2. Feature Engineering

The model uses 12 features:
1. Age (18-80 years)
2. Sex (encoded: M/F)
3. BMI (calculated from height/weight)
4. Average daily caffeine (mg)
5. Total weekly caffeine (mg)
6. Systolic blood pressure
7. Diastolic blood pressure
8. Has hypertension (binary)
9. Has diabetes (binary)
10. Has family history of CHD (binary)
11. Is smoker (binary)
12. Activity level (encoded: sedentary/light/moderate/active)

#### 3. Model Training

**Algorithms Tested**:
- Logistic Regression
- Random Forest (200 estimators, max_depth=10)
- Gradient Boosting (200 estimators, learning_rate=0.05)

**Training Process**:
```python
# Data split: 80% training, 20% testing
# Feature scaling: StandardScaler
# Class balancing: class_weight='balanced'
# Evaluation: ROC-AUC, Accuracy, Precision, Recall, F1-Score
```

**Best Model**: Logistic Regression
- **ROC-AUC**: 0.999
- **Accuracy**: 97.3%
- **Precision**: 87.7%
- **Recall**: 99.5%
- **F1-Score**: 0.932

#### 4. Model Calibration

The model outputs are calibrated to provide realistic risk percentages:
- Low probabilities (<0.1): Scaled down by 70%
- Moderate probabilities (0.1-0.3): Conservative scaling
- Higher probabilities: Direct mapping with reasonable caps

This prevents over-prediction and ensures risk percentages are clinically meaningful.

#### 5. Model Files

The training script generates:
- `heart_disease_model.pkl` - Trained Logistic Regression model
- `scaler.pkl` - StandardScaler for feature normalization
- `encoders.pkl` - Label encoders for categorical variables (sex, activity_level)
- `feature_names.pkl` - Feature names in correct order

### Training the Model

To retrain the model:

```bash
cd thesis_model
python train_model.py --dataset_path ../thesis_dataset/Data --output_path ../backend/coffee_backend/ml_models
```

**Parameters**:
- `--dataset_path`: Path to dataset directory (default: `../thesis_dataset/Data`)
- `--output_path`: Where to save model files (default: `./models`)
- `--test_size`: Test set proportion (default: 0.2)
- `--random_state`: Random seed for reproducibility (default: 42)

### Model Integration

The trained model is integrated into the Django backend via `coffee/ml_model_utils.py`:

1. **Model Loading**: Models are loaded and cached on first use
2. **Feature Preparation**: User data is transformed to match training format
3. **Prediction**: Model generates risk probability
4. **Calibration**: Probabilities are calibrated to realistic percentages
5. **Risk Categorization**: Low (<15%), Moderate (15-30%), High (>30%)

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Node.js 14+
- npm or yarn

### Installation

#### Backend Setup

```bash
cd backend/coffee_backend
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
```

#### Frontend Setup

```bash
npm install
```

#### ML Model Setup

```bash
cd thesis_model
pip install -r requirements.txt
python train_model.py --output_path ../backend/coffee_backend/ml_models
```

### Running the Application

#### Start Backend Server

```bash
cd backend/coffee_backend
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/api`

#### Start Frontend Development Server

```bash
npm start
```

The application will open at `http://localhost:3000`

## 📁 Project Structure

```
coffee-website/
├── backend/
│   └── coffee_backend/
│       ├── coffee/
│       │   ├── ml_model_utils.py      # ML model integration
│       │   ├── views.py               # API endpoints
│       │   └── models/                # Django models
│       └── ml_models/                  # Trained ML model files
├── src/
│   ├── Page1/                         # Home page components
│   ├── Page2/                         # Recipe browsing
│   ├── Page3/                         # My recipes
│   ├── Page4/                         # Health predictions
│   └── authentication/               # Auth components
├── thesis_model/
│   ├── train_model.py                 # ML training script
│   └── requirements.txt
└── thesis_dataset/                    # Training data
```

## 🔌 API Endpoints

### Authentication
- `POST /api/register/` - User registration
- `POST /api/login/` - User login
- `POST /api/logout/` - User logout

### Coffee Recipes
- `GET /api/coffees/` - List all recipes
- `POST /api/coffees/` - Create recipe
- `GET /api/coffees/{id}/` - Get recipe details
- `PUT /api/coffees/{id}/` - Update recipe
- `DELETE /api/coffees/{id}/` - Delete recipe
- `POST /api/coffees/{id}/like/` - Toggle like
- `GET /api/most-popular/` - Get top 3 most liked recipes

### Health & Predictions
- `POST /api/prediction/` - Generate heart disease risk prediction
- `GET /api/consumed/` - Get consumed coffees
- `POST /api/consumed/` - Log consumed coffee
- `GET /api/health-profile/` - Get user health profile
- `PUT /api/health-profile/` - Update health profile
- `GET /api/blood-pressure/` - Get blood pressure entries
- `POST /api/blood-pressure/` - Add blood pressure entry

## 🧪 Model Performance

The trained model demonstrates excellent performance:

| Metric | Value |
|--------|-------|
| ROC-AUC | 0.999 |
| Accuracy | 97.3% |
| Precision | 87.7% |
| Recall | 99.5% |
| F1-Score | 0.932 |

**Note**: These metrics are based on synthetic data. Real-world performance may vary when deployed with actual user data.

## ⚠️ Important Disclaimers

1. **Medical Disclaimer**: The heart disease risk predictions are for informational purposes only and are not a substitute for professional medical advice, diagnosis, or treatment. Always consult with qualified healthcare providers for medical concerns.

2. **Model Limitations**: 
   - Trained on synthetic data; real-world performance may differ
   - Predictions are estimates based on available data
   - Missing health profile data may reduce prediction accuracy

3. **Data Privacy**: User health data is stored securely and used only for generating predictions. Always follow local data protection regulations.

## 🔮 Future Improvements

- [ ] Integration with real NHANES dataset
- [ ] Model retraining pipeline with user data
- [ ] Additional health metrics (cholesterol, glucose)
- [ ] Export predictions to PDF
- [ ] Prediction history timeline
- [ ] Mobile app version
- [ ] Integration with fitness trackers

## 📚 Technologies Used

### Frontend
- React.js
- React Router
- CSS Modules
- Context API

### Backend
- Django
- Django REST Framework
- JWT Authentication
- SQLite/PostgreSQL

### Machine Learning
- Scikit-learn
- NumPy
- Pandas
- Joblib

## 📄 License

This project is part of a bachelor's thesis on heart disease prediction based on caffeine intake.

## 👥 Authors

Developed as part of academic research at UBB (Babeș-Bolyai University).

---

For questions or issues, please refer to the project documentation or contact the development team.
