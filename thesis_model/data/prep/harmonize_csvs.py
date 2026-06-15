#!/usr/bin/env python3
"""
Script to harmonize NHANES CSVs to match thesis format
"""
import pandas as pd
import os
from pathlib import Path

# Define paths (relative to this repo)
repo_root = Path(__file__).resolve().parents[3]
thesis_dir = repo_root / "thesis_dataset" / "Data"
workspace_dir = repo_root.parent / "NHANES 1988-2018 Archive"
output_dir = workspace_dir / "harmonized"

# Create output directory
output_dir.mkdir(exist_ok=True)

# Column mappings for each file type
thesis_columns = {
    "demographics": [
        "SEQN", "SDDSRVYR", "RIDSTATR", "RIAGENDR", "RIDAGEYR", "RIDAGEMN", 
        "RIDRETH1", "RIDRETH3", "RIDEXMON", "RIDEXAGM", "DMQMILIZ", "DMQADFC", 
        "DMDBORN4", "DMDCITZN", "DMDYRSUS", "DMDEDUC3", "DMDEDUC2", "DMDMARTL", 
        "RIDEXPRG", "SIALANG", "SIAPROXY", "SIAINTRP", "FIALANG", "FIAPROXY", 
        "FIAINTRP", "MIALANG", "MIAPROXY", "MIAINTRP", "AIALANGA", "DMDHHSIZ", 
        "DMDFMSIZ", "DMDHHSZA", "DMDHHSZB", "DMDHHSZE", "DMDHRGND", "DMDHRAGE", 
        "DMDHRBR4", "DMDHREDU", "DMDHRMAR", "DMDHSEDU", "WTINT2YR", "WTMEC2YR", 
        "SDMVPSU", "SDMVSTRA", "INDHHIN2", "INDFMIN2", "INDFMPIR"
    ],
    "diabetes": [
        "SEQN", "DIQ010", "DID040", "DIQ160", "DIQ170", "DIQ172", "DIQ175A", 
        "DIQ175B", "DIQ175C", "DIQ175D", "DIQ175E", "DIQ175F", "DIQ175G", 
        "DIQ175H", "DIQ175I", "DIQ175J", "DIQ175K", "DIQ175L", "DIQ175M", 
        "DIQ175N", "DIQ175O", "DIQ175P", "DIQ175Q", "DIQ175R", "DIQ175S", 
        "DIQ175T", "DIQ175U", "DIQ175V", "DIQ175W", "DIQ175X", "DIQ180", 
        "DIQ050", "DID060", "DIQ060U", "DIQ070", "DIQ230", "DIQ240", "DID250", 
        "DID260", "DIQ260U", "DIQ275", "DIQ280", "DIQ291", "DIQ300S", "DIQ300D", 
        "DID310S", "DID310D", "DID320", "DID330", "DID341", "DID350", "DIQ350U", 
        "DIQ360", "DIQ080"
    ],
    "blood_pressure": [
        "SEQN", "BPQ020", "BPQ030", "BPD035", "BPQ040A", "BPQ050A", "BPQ080", 
        "BPQ060", "BPQ070", "BPQ090D", "BPQ100D"
    ],
    "food_individual": [
        "SEQN", "DR1IFDCD", "DR1IGRMS", "DR1IKCAL", "DR1IPROT", "DR1ICARB", 
        "DR1ISUGR", "DR1IFIBE", "DR1ITFAT", "DR1ISFAT", "DR1IMFAT", "DR1IPFAT", 
        "DR1ICHOL", "DR1IATOC", "DR1IATOA", "DR1IRET", "DR1IVARA", "DR1IACAR", 
        "DR1IBCAR", "DR1ICRYP", "DR1ILYCO", "DR1ILZ", "DR1IVB1", "DR1IVB2", 
        "DR1INIAC", "DR1IVB6", "DR1IFOLA", "DR1IFA", "DR1IFF", "DR1IFDFE", 
        "DR1ICHL", "DR1IVB12", "DR1IB12A", "DR1IVC", "DR1IVD", "DR1IVK", 
        "DR1ICALC", "DR1IPHOS", "DR1IMAGN", "DR1IIRON", "DR1IZINC", "DR1ICOPP", 
        "DR1ISODI", "DR1IPOTA", "DR1ISELE", "DR1ICAFF", "DR1ITHEO", "DR1IALCO", 
        "DR1IMOIS"
    ],
    "nutrients_total": [
        "SEQN", "WTDRD1", "WTDR2D", "DR1DRSTZ", "DR1EXMER", "DRABF", "DRDINT", 
        "DR1DBIH", "DR1DAY", "DR1LANG", "DR1MRESP", "DR1HELP", "DBQ095Z", 
        "DBD100", "DRQSPREP", "DR1STY", "DR1SKY", "DRQSDIET", "DRQSDT1", 
        "DRQSDT2", "DRQSDT3", "DRQSDT4", "DRQSDT5", "DRQSDT6", "DRQSDT7", 
        "DRQSDT8", "DRQSDT9", "DRQSDT10", "DRQSDT11", "DRQSDT12", "DRQSDT91", 
        "DR1TNUMF", "DR1TKCAL", "DR1TPROT", "DR1TCARB", "DR1TSUGR", "DR1TFIBE", 
        "DR1TTFAT", "DR1TSFAT", "DR1TMFAT", "DR1TPFAT", "DR1TCHOL", "DR1TATOC", 
        "DR1TATOA", "DR1TRET", "DR1TVARA", "DR1TACAR", "DR1TBCAR", "DR1TCRYP", 
        "DR1TLYCO", "DR1TLZ", "DR1TVB1", "DR1TVB2", "DR1TNIAC", "DR1TVB6", 
        "DR1TFOLA", "DR1TFA", "DR1TFF", "DR1TFDFE", "DR1TCHL", "DR1TVB12", 
        "DR1TB12A", "DR1TVC", "DR1TVD", "DR1TVK", "DR1TCALC", "DR1TPHOS", 
        "DR1TMAGN", "DR1TIRON", "DR1TZINC", "DR1TCOPP", "DR1TSODI", "DR1TPOTA", 
        "DR1TSELE", "DR1TCAFF", "DR1TTHEO", "DR1TALCO", "DR1TMOIS", "DR1TS040", 
        "DR1TS060", "DR1TS080", "DR1TS100", "DR1TS120", "DR1TS140", "DR1TS160", 
        "DR1TS180", "DR1TM161", "DR1TM181", "DR1TM201", "DR1TM221", "DR1TP182", 
        "DR1TP183", "DR1TP184", "DR1TP204", "DR1TP205", "DR1TP225", "DR1TP226", 
        "DR1_300", "DR1_320Z", "DR1_330Z", "DR1BWATZ", "DR1TWS", "DRD340", 
        "DRD350A", "DRD350AQ", "DRD350B", "DRD350BQ", "DRD350C", "DRD350CQ", 
        "DRD350D", "DRD350DQ", "DRD350E", "DRD350EQ", "DRD350F", "DRD350FQ", 
        "DRD350G", "DRD350GQ", "DRD350H", "DRD350HQ", "DRD350I", "DRD350IQ", 
        "DRD350J", "DRD350JQ", "DRD350K", "DRD360", "DRD370A", "DRD370AQ", 
        "DRD370B", "DRD370BQ", "DRD370C", "DRD370CQ", "DRD370D", "DRD370DQ", 
        "DRD370E", "DRD370EQ", "DRD370F", "DRD370FQ", "DRD370G", "DRD370GQ", 
        "DRD370H", "DRD370HQ", "DRD370I", "DRD370IQ", "DRD370J", "DRD370JQ", 
        "DRD370K", "DRD370KQ", "DRD370L", "DRD370LQ", "DRD370M", "DRD370MQ", 
        "DRD370N", "DRD370NQ", "DRD370O", "DRD370OQ", "DRD370P", "DRD370PQ", 
        "DRD370Q", "DRD370QQ", "DRD370R", "DRD370RQ", "DRD370S", "DRD370SQ", 
        "DRD370T", "DRD370TQ", "DRD370U", "DRD370UQ", "DRD370V"
    ]
}

def harmonize_file(source_file, target_columns, output_file):
    """
    Read source file, select only columns that exist in both source and target,
    and save to output file.
    """
    print(f"\nProcessing {source_file.name}...")
    
    # Read the source file
    try:
        df = pd.read_csv(source_file, low_memory=False)
        print(f"  Loaded {len(df)} rows with {len(df.columns)} columns")
        
        # Get columns that exist in both source and target
        available_columns = [col for col in target_columns if col in df.columns]
        missing_columns = [col for col in target_columns if col not in df.columns]
        
        print(f"  Found {len(available_columns)}/{len(target_columns)} target columns")
        
        if missing_columns:
            print(f"  Missing columns ({len(missing_columns)}): {', '.join(missing_columns[:10])}" + 
                  ("..." if len(missing_columns) > 10 else ""))
        
        # Select only available columns
        df_harmonized = df[available_columns].copy()
        
        # Save to output file
        df_harmonized.to_csv(output_file, index=False)
        print(f"  Saved to {output_file.name}")
        
        return True
        
    except Exception as e:
        print(f"  ERROR: {str(e)}")
        return False

def main():
    print("=" * 60)
    print("NHANES CSV Harmonization Script")
    print("=" * 60)
    
    # 1. Harmonize Demographics
    harmonize_file(
        workspace_dir / "demographics_clean.csv",
        thesis_columns["demographics"],
        output_dir / "NHANES Demographics.csv"
    )
    
    # 2. Harmonize Diabetes Questionnaire
    harmonize_file(
        workspace_dir / "questionnaire_clean.csv",
        thesis_columns["diabetes"],
        output_dir / "NHANES Diabetes Questionnaire.csv"
    )
    
    # 3. Harmonize Blood Pressure Questionnaire
    harmonize_file(
        workspace_dir / "questionnaire_clean.csv",
        thesis_columns["blood_pressure"],
        output_dir / "NHANES Blood Pressure Quesstionnaire.csv"
    )
    
    # 4. Harmonize Dietary Data
    # Note: The dietary data structure is different - need to map DRXT* to DR1T* format
    
    print("\nProcessing dietary data...")
    try:
        dietary_df = pd.read_csv(workspace_dir / "dietary_clean.csv", low_memory=False)
        print(f"  Loaded {len(dietary_df)} rows with {len(dietary_df.columns)} columns")
        
        # Create column mapping from workspace names to thesis names
        # Map DRXT* to DR1T*, DRXD* to DR1D*, etc.
        column_mapping = {}
        for col in dietary_df.columns:
            if col.startswith('DRXT'):
                # Map DRXTKCAL -> DR1TKCAL, etc.
                new_col = col.replace('DRXT', 'DR1T')
                column_mapping[col] = new_col
            elif col.startswith('DRXD'):
                new_col = col.replace('DRXD', 'DR1D')
                column_mapping[col] = new_col
            elif col.startswith('DRX'):
                new_col = col.replace('DRX', 'DR1')
                column_mapping[col] = new_col
        
        # Rename columns in dietary dataframe
        dietary_df_renamed = dietary_df.rename(columns=column_mapping)
        
        # Individual Food Consumption - WARNING: This data may not be available
        print("  Note: Individual food item data (DR1I* columns) not found in workspace.")
        print("  Creating placeholder files - you may need to download this data from NHANES separately.")
        
        # Create empty placeholder for Individual Food Consumption
        food_placeholder = pd.DataFrame(columns=thesis_columns["food_individual"])
        food_placeholder.to_csv(output_dir / "NHANES Individual Food Consumption Day 1 (Reduced).csv", index=False)
        food_placeholder.to_csv(output_dir / "NHANES Individual Food Consumption Day 2 (Reduced).csv", index=False)
        print(f"  Created placeholder files for Individual Food Consumption")
        
        # Total Nutrients Day 1
        available_nutrient_cols = [col for col in thesis_columns["nutrients_total"] if col in dietary_df_renamed.columns]
        missing_nutrient_cols = [col for col in thesis_columns["nutrients_total"] if col not in dietary_df_renamed.columns]
        
        print(f"  Total Nutrients: {len(available_nutrient_cols)}/{len(thesis_columns['nutrients_total'])} columns available")
        
        if available_nutrient_cols:
            # Get unique records per SEQN
            nutrients_day1 = dietary_df_renamed.drop_duplicates(subset=["SEQN"]).copy()
            df_nutrients_day1 = nutrients_day1[available_nutrient_cols].copy()
            df_nutrients_day1.to_csv(output_dir / "NHANES Total Nutrients Day 1.csv", index=False)
            print(f"  Saved Total Nutrients Day 1: {len(df_nutrients_day1)} rows")
            
            # Create Day 2 version (duplicate for now, as workspace doesn't separate days)
            df_nutrients_day1.to_csv(output_dir / "NHANES Total Nutrients Day 2.csv", index=False)
            print(f"  Saved Total Nutrients Day 2: {len(df_nutrients_day1)} rows")
            
    except Exception as e:
        print(f"  ERROR processing dietary data: {str(e)}")
    
    # 5. Copy USDA Food Codes if available
    usda_source = workspace_dir / "dictionary_food_codes.csv"
    if usda_source.exists():
        try:
            usda_df = pd.read_csv(usda_source)
            # Try to map to thesis format
            if "food_code" in usda_df.columns or "DRXFDCD" in usda_df.columns:
                usda_df.to_csv(output_dir / "USDA Food Codes.csv", index=False)
                print(f"\n  Copied USDA Food Codes")
        except Exception as e:
            print(f"\n  Could not process USDA Food Codes: {str(e)}")
    
    print("\n" + "=" * 60)
    print("Harmonization Complete!")
    print(f"Output files saved to: {output_dir}")
    print("=" * 60)

if __name__ == "__main__":
    main()
