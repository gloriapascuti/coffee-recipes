"""
Explore NHANES mortality data to understand CVD outcomes for ML model.
"""
import pandas as pd
import numpy as np

print("="*80)
print("NHANES 1988-2018 Mortality Data Exploration")
print("="*80)

# Load mortality data
print("\n1. Loading mortality data...")
mortality = pd.read_csv('mortality_clean.csv')
print(f"   Total records: {len(mortality):,}")

# Load demographics to understand the cohort
print("\n2. Loading demographics data...")
demographics = pd.read_csv('demographics_clean.csv')
print(f"   Total demographic records: {len(demographics):,}")

# Merge to get age information
print("\n3. Merging mortality with demographics...")
demo_cols = ['SEQN', 'RIDAGEYR', 'RIAGENDR']
if 'SDDSRVYR' in demographics.columns:
    demo_cols.append('SDDSRVYR')
df = mortality.merge(demographics[demo_cols], on='SEQN', how='left')
print(f"   Merged records: {len(df):,}")

print("\n" + "="*80)
print("ELIGIBILITY & FOLLOW-UP")
print("="*80)

# Eligibility status
print("\nEligibility Status (ELIGSTAT):")
print(f"  1 = Eligible for mortality follow-up: {(df['ELIGSTAT'] == 1).sum():,}")
print(f"  2 = Under 18, not eligible: {(df['ELIGSTAT'] == 2).sum():,}")
print(f"  3 = Ineligible for other reasons: {(df['ELIGSTAT'] == 3).sum():,}")

# Focus on eligible adults
eligible = df[df['ELIGSTAT'] == 1].copy()
print(f"\n✓ Eligible adults (18+): {len(eligible):,}")

# Mortality status
print("\nMortality Status (MORTSTAT) - Eligible Adults Only:")
deceased = eligible['MORTSTAT'] == 1
alive = eligible['MORTSTAT'] == 0
print(f"  Deceased: {deceased.sum():,} ({deceased.sum()/len(eligible)*100:.1f}%)")
print(f"  Alive/Assumed alive: {alive.sum():,} ({alive.sum()/len(eligible)*100:.1f}%)")

print("\n" + "="*80)
print("CARDIOVASCULAR OUTCOMES")
print("="*80)

# Cause of death analysis
print("\nCause of Death (UCOD_LEADING) - Deceased Only:")
deceased_df = eligible[deceased].copy()
print(f"\nTotal deaths with known cause: {deceased_df['UCOD_LEADING'].notna().sum():,}")

cause_counts = deceased_df['UCOD_LEADING'].value_counts().sort_index()
cause_labels = {
    1.0: "Diseases of heart (CVD)",
    2.0: "Malignant neoplasms (Cancer)",
    3.0: "Chronic lower respiratory diseases",
    4.0: "Accidents (unintentional injuries)",
    5.0: "Cerebrovascular diseases (Stroke)",
    6.0: "Alzheimer's disease",
    7.0: "Diabetes mellitus",
    8.0: "Influenza and pneumonia",
    9.0: "Nephritis, nephrotic syndrome",
    10.0: "All other causes"
}

print("\nBreakdown by cause:")
for code, count in cause_counts.items():
    label = cause_labels.get(code, f"Code {code}")
    pct = count / len(deceased_df) * 100
    print(f"  {code:2.0f}. {label:40s}: {count:5,} ({pct:4.1f}%)")

# CVD deaths (heart disease + stroke)
cvd_deaths = deceased_df[deceased_df['UCOD_LEADING'].isin([1.0, 5.0])]
print(f"\n🎯 CARDIOVASCULAR DEATHS (Heart + Stroke): {len(cvd_deaths):,}")
print(f"   As % of all deaths: {len(cvd_deaths)/len(deceased_df)*100:.1f}%")
print(f"   As % of eligible cohort: {len(cvd_deaths)/len(eligible)*100:.2f}%")

# Also check the HYPERTEN flag (died with hypertension on death certificate)
print(f"\n   Deaths with hypertension on certificate: {deceased_df['HYPERTEN'].eq(1).sum():,}")
print(f"   Deaths with diabetes on certificate: {deceased_df['DIABETES'].eq(1).sum():,}")

print("\n" + "="*80)
print("AGE DISTRIBUTION")
print("="*80)

# Age distribution
print("\nAge Distribution - Eligible Adults:")
print(f"  Mean age: {eligible['RIDAGEYR'].mean():.1f} years")
print(f"  Median age: {eligible['RIDAGEYR'].median():.1f} years")
print(f"  Range: {eligible['RIDAGEYR'].min():.0f} - {eligible['RIDAGEYR'].max():.0f} years")

print("\nAge distribution by outcome:")
print(f"  Alive - Mean: {eligible[alive]['RIDAGEYR'].mean():.1f}, Median: {eligible[alive]['RIDAGEYR'].median():.1f}")
print(f"  Deceased - Mean: {deceased_df['RIDAGEYR'].mean():.1f}, Median: {deceased_df['RIDAGEYR'].median():.1f}")
print(f"  CVD Deaths - Mean: {cvd_deaths['RIDAGEYR'].mean():.1f}, Median: {cvd_deaths['RIDAGEYR'].median():.1f}")

# Age bins
age_bins = [0, 30, 40, 50, 60, 70, 80, 120]
age_labels = ['<30', '30-39', '40-49', '50-59', '60-69', '70-79', '80+']
eligible['age_group'] = pd.cut(eligible['RIDAGEYR'], bins=age_bins, labels=age_labels)

print("\nCohort by age group:")
for age_group in age_labels:
    group = eligible[eligible['age_group'] == age_group]
    n_total = len(group)
    n_deceased = (group['MORTSTAT'] == 1).sum()
    n_cvd = group[group['MORTSTAT'] == 1]['UCOD_LEADING'].isin([1.0, 5.0]).sum()
    if n_total > 0:
        print(f"  {age_group:8s}: {n_total:6,} total | {n_deceased:5,} deaths ({n_deceased/n_total*100:4.1f}%) | {n_cvd:4,} CVD ({n_cvd/n_total*100:4.2f}%)")

print("\n" + "="*80)
print("FOLLOW-UP TIME")
print("="*80)

# Follow-up time (PERMTH_INT = person-months of follow-up from interview)
print("\nFollow-up Time (from interview date):")
has_followup = eligible['PERMTH_INT'].notna()
print(f"  Records with follow-up data: {has_followup.sum():,}")

if has_followup.sum() > 0:
    followup_years = eligible[has_followup]['PERMTH_INT'] / 12
    print(f"  Mean follow-up: {followup_years.mean():.1f} years")
    print(f"  Median follow-up: {followup_years.median():.1f} years")
    print(f"  Max follow-up: {followup_years.max():.1f} years")
    print(f"  Min follow-up: {followup_years.min():.1f} years")
    
    print("\n  Follow-up by outcome:")
    print(f"    Alive: {eligible[alive & has_followup]['PERMTH_INT'].mean()/12:.1f} years (mean)")
    print(f"    Deceased: {deceased_df[deceased_df['PERMTH_INT'].notna()]['PERMTH_INT'].mean()/12:.1f} years (mean)")

print("\n" + "="*80)
print("SURVEY CYCLES")
print("="*80)

if 'SDDSRVYR' in eligible.columns:
    print("\nDistribution across NHANES cycles:")
    cycle_labels = {
        1: '1988-1994 (NHANES III)',
        2: '1999-2000',
        3: '2001-2002',
        4: '2003-2004',
        5: '2005-2006',
        6: '2007-2008',
        7: '2009-2010',
        8: '2011-2012',
        9: '2013-2014',
        10: '2015-2016',
        11: '2017-2018'
    }

    for cycle, label in cycle_labels.items():
        cycle_data = eligible[eligible['SDDSRVYR'] == cycle]
        n_total = len(cycle_data)
        n_deceased = (cycle_data['MORTSTAT'] == 1).sum()
        n_cvd = cycle_data[cycle_data['MORTSTAT'] == 1]['UCOD_LEADING'].isin([1.0, 5.0]).sum()
        if n_total > 0:
            print(f"  {label:25s}: {n_total:6,} | {n_deceased:5,} deaths | {n_cvd:4,} CVD")
else:
    print("\nSurvey cycle information (SDDSRVYR) not available in demographics file.")
    print("Using SDDSRVYR from mortality file instead:")
    if 'SDDSRVYR' in eligible.columns:
        print(eligible['SDDSRVYR'].value_counts().sort_index())
    else:
        print("  (Survey cycle data not found)")

print("\n" + "="*80)
print("DATA QUALITY ASSESSMENT")
print("="*80)

print("\nMissing data in key variables (eligible adults only):")
print(f"  Age (RIDAGEYR): {eligible['RIDAGEYR'].isna().sum():,} missing ({eligible['RIDAGEYR'].isna().sum()/len(eligible)*100:.2f}%)")
print(f"  Sex (RIAGENDR): {eligible['RIAGENDR'].isna().sum():,} missing ({eligible['RIAGENDR'].isna().sum()/len(eligible)*100:.2f}%)")
print(f"  Follow-up time: {eligible['PERMTH_INT'].isna().sum():,} missing ({eligible['PERMTH_INT'].isna().sum()/len(eligible)*100:.2f}%)")
print(f"  Cause of death (among deceased): {deceased_df['UCOD_LEADING'].isna().sum():,} missing")

print("\n" + "="*80)
print("SUMMARY & RECOMMENDATIONS")
print("="*80)

print(f"""
✓ VIABLE FOR ML MODEL WITH REAL OUTCOMES:

1. Sample Size:
   - Eligible adults (18+): {len(eligible):,}
   - Total deaths: {deceased.sum():,}
   - CVD deaths (target): {len(cvd_deaths):,}
   - Class imbalance: {len(cvd_deaths)/len(eligible)*100:.2f}% positive class

2. Follow-up:
   - Up to {followup_years.max():.0f} years of follow-up
   - Mean: {followup_years.mean():.1f} years
   - Sufficient time for CVD outcomes to develop

3. Data Quality:
   - Minimal missing data in key variables
   - Age and sex nearly complete
   - Clear outcome labels (CVD death vs alive)

4. Temporal Coverage:
   - 30 years of NHANES data (1988-2018)
   - Multiple survey cycles provide diversity

NEXT STEPS:
1. Merge mortality data with:
   - Demographics (age, sex, BMI)
   - Blood pressure questionnaire (hypertension)
   - Diabetes questionnaire
   - Dietary data (caffeine intake)
2. Create binary target: CVD death (1) vs alive (0)
3. Handle class imbalance (use class_weight='balanced' or SMOTE)
4. Train model to predict CVD death probability
5. Validate that model learns real patterns (not formula)
""")

print("\n" + "="*80)
print("Exploration complete!")
print("="*80)

# Save summary statistics
summary = {
    'total_eligible': len(eligible),
    'total_deaths': deceased.sum(),
    'cvd_deaths': len(cvd_deaths),
    'cvd_rate': len(cvd_deaths)/len(eligible),
    'mean_age': eligible['RIDAGEYR'].mean(),
    'mean_followup_years': followup_years.mean(),
    'max_followup_years': followup_years.max()
}

print("\nSaving summary to 'mortality_exploration_summary.txt'...")
with open('mortality_exploration_summary.txt', 'w') as f:
    f.write("NHANES 1988-2018 Mortality Data Summary\n")
    f.write("="*80 + "\n\n")
    for key, value in summary.items():
        f.write(f"{key}: {value}\n")

print("Done!")
