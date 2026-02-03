# Dataset Summary for Bachelor's Thesis

**Topic:** Heart Disease Prediction based on Caffeine Intake  
**Student:** Gloriasa  
**Date:** November 26, 2025

---

## Dataset Overview

This project contains data from the National Health and Nutrition Examination Survey (NHANES) combined with USDA food composition data. The dataset includes approximately 9,500+ patients with comprehensive dietary intake, cardiovascular health indicators, and demographic information.

---

## Primary Data Files

### 1. Caffeine Intake Measurements

- **File:** `Data/NHANES Total Nutrients Day 1.csv`
  - Variable: `DR1TCAFF` (Total caffeine in mg/day)
  - ~9,500 patient records
- **File:** `Data/NHANES Total Nutrients Day 2.csv`
  - Second day measurements for validation/averaging

### 2. Cardiovascular Health Indicators

- **File:** `Data/NHANES Blood Pressure Quesstionnaire.csv`
  - ~6,400 patient records
  - Variables include: blood pressure status, hypertension diagnosis, medication use
  - Key fields: BPQ020, BPQ030, BPD035, BPQ040A, BPQ050A, BPQ080, etc.

### 3. Demographics & Control Variables

- **File:** `Data/NHANES Demographics.csv`
  - ~9,972 patient records
  - Age, gender, race/ethnicity, income, education level, etc.

### 4. Comorbidities (Optional)

- **File:** `Data/NHANES Diabetes Questionnaire.csv`
  - ~9,576 patient records
  - Diabetes status (relevant cardiovascular risk factor)

---

## Pre-Filtered Patient Samples

The dataset includes pre-filtered samples of **hypertension and prediabetic patients** (high cardiovascular risk group) located in `Samples/Hypertension and Prediabetic Patients/`:

### General Population:

- `all_1875_df.csv` - All patients (~1,875 total)
- `male_1875_df.csv` - Male patients (ages 18-75)
- `female_1875_df.csv` - Female patients (ages 18-75)

### Stratified by Age & Gender:

- `male_1825_df.csv` - Males, 18-25 years
- `male_2635_df.csv` - Males, 26-35 years
- `male_3645_df.csv` - Males, 36-45 years
- `male_4655_df.csv` - Males, 46-55 years
- `male_5665_df.csv` - Males, 56-65 years
- `female_1825_df.csv` - Females, 18-25 years
- `female_2635_df.csv` - Females, 26-35 years
- `female_3645_df.csv` - Females, 36-45 years
- `female_4655_df.csv` - Females, 46-55 years
- `female_5665_df.csv` - Females, 56-65 years

---

## Data Integration

All files can be merged using the **`SEQN`** variable (unique patient identifier) present in all NHANES datasets.

---

## Research Advantages

1. **Direct Relevance:** Contains both caffeine intake measurements AND cardiovascular outcomes
2. **Nationally Representative:** NHANES data is representative of the U.S. population
3. **High-Risk Population Available:** Pre-filtered hypertension patients for focused analysis
4. **Comprehensive Controls:** 75+ nutritional variables, demographics, and comorbidities available
5. **Multiple Time Points:** 2-day dietary records allow for intake averaging and validation

---

## Potential Research Questions

1. Association between caffeine intake levels and blood pressure status
2. Dose-response relationship (low/moderate/high caffeine consumption)
3. Stratified analysis by age, gender, or existing conditions
4. Interaction effects between caffeine and other dietary/lifestyle factors
5. Predictive modeling for heart disease risk based on caffeine consumption patterns

---

## Data Source Citation

**Dataset:** An Open-Source Dataset on Dietary Behaviors and DASH Eating Plan Optimization Constraints

**Authors:** Farzin Ahmadi, Fardin Ganjkhanloo, Kimia Ghobadi (2020)

**Paper:** [https://arxiv.org/pdf/2010.07531.pdf](https://arxiv.org/pdf/2010.07531.pdf)

**Original Data Source:** National Health and Nutrition Examination Survey (NHANES) Dietary Data  
[https://wwwn.cdc.gov/nchs/nhanes/Search/DataPage.aspx?Component=Dietary](https://wwwn.cdc.gov/nchs/nhanes/Search/DataPage.aspx?Component=Dietary)

---

## Next Steps

1. Load and explore the three core files (nutrients, blood pressure, demographics)
2. Merge datasets using patient ID (SEQN)
3. Perform exploratory data analysis on caffeine intake distribution
4. Analyze relationship between caffeine and cardiovascular outcomes
5. Build predictive models for heart disease risk
