from pydantic import BaseModel, EmailStr, Field, validator
from typing import Literal
import pandas as pd

class CustomerChurnRecord(BaseModel):
    """Pydantic model for validating customer churn records."""
    id: int = Field(..., gt=0)
    name: str = Field(..., min_length=2)
    email: EmailStr
    tenure_days: int = Field(..., ge=0)
    login_frequency: int = Field(..., ge=0)
    support_contacts: int = Field(..., ge=0)
    feature_breaks_encountered: int = Field(..., ge=0)
    days_since_last_login: int = Field(..., ge=0)
    status: Literal["Active", "Churned"]

def validate_df(df: pd.DataFrame):
    """Validates each row of the DataFrame against the CustomerChurnRecord model."""
    valid_records = []
    errors = []
    
    print("Starting validation process...")
    
    for index, row in df.iterrows():
        try:
            # Convert row to dict
            record_dict = row.to_dict()
            
            # Pydantic validation
            record = CustomerChurnRecord(**record_dict)
            valid_records.append(record.dict())
        except Exception as e:
            errors.append({"row_index": index, "error": str(e)})
            
    if errors:
        print(f"Validation: Found {len(errors)} records with validation/structural errors.")
    else:
        print("Validation: All records are valid and conform to schema.")
        
    return pd.DataFrame(valid_records), errors

if __name__ == "__main__":
    # Test validator
    test_data = [
        {
            "id": 101, "name": "John Doe", "email": "john@example.com", 
            "tenure_days": 365, "login_frequency": 30, "support_contacts": 1,
            "feature_breaks_encountered": 0, "days_since_last_login": 2, "status": "Active"
        },
        {
            "id": 102, "name": "J", "email": "invalid-email", 
            "tenure_days": -10, "login_frequency": 30, "support_contacts": 1,
            "feature_breaks_encountered": 0, "days_since_last_login": 2, "status": "InvalidStatus"
        }
    ]
    df_test = pd.DataFrame(test_data)
    valid_df, errs = validate_df(df_test)
    print("\nValid Records:")
    print(valid_df)
    print("\nErrors:")
    for err in errs:
        print(err)
