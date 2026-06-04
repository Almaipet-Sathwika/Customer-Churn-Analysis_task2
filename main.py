import pandas as pd
import os
import data_generator
import cleaner
import validator
import analyzer

def run_churn_pipeline(
    raw_file="raw_data.csv", 
    cleaned_file="cleaned_data.csv", 
    error_file="validation_errors.csv",
    dashboard_file="dashboard.html"
):
    """Orchestrates the data pipeline for Customer Churn Leak Detection."""
    print("==================================================")
    print("CUSTOMER CHURN ANALYSIS - LEAK DETECTOR PIPELINE")
    print("==================================================")
    
    # 1. Generate Raw Messy Data
    data_generator.generate_messy_churn_data(raw_file)
    if not os.path.exists(raw_file):
        print(f"Error: Raw file '{raw_file}' could not be generated.")
        return
        
    # 2. Load Raw Data
    print(f"\n[Step 1] Loading raw data from '{raw_file}'...")
    df_raw = pd.read_csv(raw_file)
    print(f"Loaded {len(df_raw)} records.")
    
    # 3. Clean and Standardize Data
    print("\n[Step 2] Cleaning and pre-processing dataset...")
    df_cleaned = cleaner.clean_data(df_raw)
    print(f"Cleaned dataset: {len(df_cleaned)} records remaining.")
    
    # 4. Schema and Structural Validation using Pydantic
    print("\n[Step 3] Running structural validation (Pydantic schema check)...")
    df_validated, errors = validator.validate_df(df_cleaned)
    print(f"Validated dataset: {len(df_validated)} records conform to schema.")
    
    # Save validation errors if any
    if errors:
        error_df = pd.DataFrame(errors)
        error_df.to_csv(error_file, index=False)
        print(f"⚠️ Validation errors found. Saved details to '{error_file}'.")
    else:
        # Create empty error file or remove previous
        if os.path.exists(error_file):
            os.remove(error_file)
        print("✓ Zero structural validation errors found!")
        
    # Save the cleaned and validated data
    df_validated.to_csv(cleaned_file, index=False)
    print(f"✓ Cleaned and validated dataset saved to: '{cleaned_file}'")
    
    # 5. Leak Detection and Analysis + Interactive Dashboard Generation
    print("\n[Step 4] Launching Churn Leak Detector...")
    analyzer.analyze_churn(df_validated, dashboard_file)
    
    print("\n==================================================")
    print("PIPELINE COMPLETED SUCCESSFULLY!")
    print(f"Dashboard: {os.path.abspath(dashboard_file)}")
    print(f"Clean Data: {os.path.abspath(cleaned_file)}")
    print("==================================================")

if __name__ == "__main__":
    run_churn_pipeline()
