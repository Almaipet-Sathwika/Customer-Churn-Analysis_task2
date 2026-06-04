import pandas as pd
import numpy as np

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Applies a series of cleaning steps to the churn DataFrame."""
    print("Starting cleaning process...")
    
    # 1. Deduplication
    df = deduplicate(df)
    
    # 2. String Standardization
    df = standardize_strings(df, ['name', 'email'])
    
    # 3. Numeric Standardization
    df = standardize_numeric(df, ['tenure_days', 'login_frequency', 'support_contacts', 'feature_breaks_encountered', 'days_since_last_login'])
    
    # 4. Handle Missing Values
    df = handle_missing_values(df)
    
    print("Cleaning process completed.")
    return df

def deduplicate(df: pd.DataFrame) -> pd.DataFrame:
    """Removes exact duplicate rows and duplicate customer IDs."""
    initial_count = len(df)
    # Remove exact duplicate rows
    df = df.drop_duplicates().reset_index(drop=True)
    # Remove duplicate IDs (keeping first occurrence)
    df = df.drop_duplicates(subset=['id'], keep='first').reset_index(drop=True)
    print(f"Deduplication: Removed {initial_count - len(df)} duplicate entries.")
    return df

def standardize_strings(df: pd.DataFrame, columns: list) -> pd.DataFrame:
    """Trims whitespace and normalizes casing for string columns."""
    for col in columns:
        if col in df.columns:
            # Convert to string and trim
            df[col] = df[col].astype(str).str.strip()
            # Normalize casing
            if col == 'name':
                df[col] = df[col].str.title()
            if col == 'email':
                df[col] = df[col].str.lower()
    print(f"String Standardization: Cleaned string columns {columns}.")
    return df

def standardize_numeric(df: pd.DataFrame, columns: list) -> pd.DataFrame:
    """Converts numeric columns stored as strings/objects to integers."""
    for col in columns:
        if col in df.columns:
            # Strip whitespace if object/string
            if df[col].dtype == object:
                df[col] = df[col].astype(str).str.strip()
            # Replace placeholder markers
            df[col] = df[col].replace(['NaN', 'N/A', 'nan', 'none', 'None', '', np.nan], np.nan)
            # Convert to numeric
            df[col] = pd.to_numeric(df[col], errors='coerce')
    print(f"Numeric Standardization: Converted columns {columns} to numeric values.")
    return df

def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """Imputes missing numeric values and drops rows with critical missing info."""
    # Convert placeholder strings in entire dataframe to actual NaN
    df = df.replace(['NaN', 'N/A', 'nan', 'none', 'None', ''], np.nan)
    
    # Impute tenure_days with median tenure of the dataset
    if 'tenure_days' in df.columns:
        median_tenure = df['tenure_days'].median()
        if pd.isna(median_tenure):
            median_tenure = 180.0
        df['tenure_days'] = df['tenure_days'].fillna(median_tenure).astype(int)
        
    # Impute logins, support, feature breaks and last login
    for numeric_col in ['login_frequency', 'support_contacts', 'feature_breaks_encountered', 'days_since_last_login']:
        if numeric_col in df.columns:
            median_val = df[numeric_col].median()
            if pd.isna(median_val):
                median_val = 0
            df[numeric_col] = df[numeric_col].fillna(median_val).astype(int)
            
    # Drop rows where critical info like name, email, or status is missing
    df = df.dropna(subset=['id', 'name', 'email', 'status'])
    df['id'] = df['id'].astype(int)
    
    print("Missing Values: Imputed numerical fields and removed records with critical missing values.")
    return df

if __name__ == "__main__":
    # Quick test
    import os
    if os.path.exists("raw_data.csv"):
        raw_df = pd.read_csv("raw_data.csv")
        cleaned_df = clean_data(raw_df)
        print(cleaned_df.head())
