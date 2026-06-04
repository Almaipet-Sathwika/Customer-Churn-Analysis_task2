import pandas as pd
import numpy as np
import os

def generate_messy_churn_data(output_path="raw_data.csv"):
    """Generates a dataset with customer churn indicators, duplicates, missing values, and inconsistent formats."""
    
    # We want a mix of active and churned members with features showing:
    # 1. Specific feature breaks -> Canceled
    # 2. No login for 14 days -> Left & canceled
    # 3. Regular active customers and standard support contacts.
    
    data = {
        "id": [101, 102, 103, 103, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120], # 103 is a duplicate
        "name": [
            "John Doe", " Jane Smith ", "Alice Johnson", "Alice Johnson", "Bob Miller", 
            "Charlie Davis", "Emma Wilson", "Frank Thomas", np.nan, "Grace Taylor",
            "Henry Anderson", "Ivy Thomas", "Jack Martin", "Kelly White", "Leo Harris",
            "Mia Clark", "Noah Lewis", "Olivia Walker", "Paul Allen", "Ryan Young"
        ],
        "email": [
            "john.doe@example.com", "JANE.SMITH@EXAMPLE.COM", "alice@johnson.com", "alice@johnson.com", "bob@example.net",
            "charlie.d@example.org", "emma.w@example.com", "frank@example", "grace@example.com", "grace.t@example.com",
            "henry@example.com", "ivy.t@example.com", "jack.m@example.org", "kelly.w@example.com", "leo.h@example.com",
            "mia.c@example.com", "noah.l@example.com", "olivia.w@example.com", "paul.a@example", "ryan@example.com"
        ],
        "tenure_days": [
            "365", " 120 ", "450", "450", "30", "15", "600", "720", "180", "N/A",
            "90", "12", "500", "240", "80", "10", "400", "300", "50", "150"
        ], # String representation of numbers
        "login_frequency": [
            "30", "2", "25", "25", "1", "0", "28", "22", "15", "10",
            "5", "0", "26", "18", "4", "0", "20", "24", "2", "12"
        ], # Monthly logins
        "support_contacts": [
            "1", "8", "2", "2", "5", "12", "0", "1", "3", "4",
            "7", "10", "2", "3", "6", "14", "1", "2", "5", "4"
        ], # Number of support tickets
        "feature_breaks_encountered": [
            0, 4, 1, 1, 3, 5, 0, 0, 1, 2,
            5, 4, 1, 0, 3, 5, 0, 1, 4, 2
        ], # Specific feature breaks
        "days_since_last_login": [
            "2", "15", "4", "4", "20", "14", "1", "3", "7", "5",
            "16", "14", "3", "6", "18", "10", "5", "2", "17", "6"
        ], # Inactivity marker
        "status": [
            "Active", "Churned", "Active", "Active", "Churned", "Churned", "Active", "Active", "Active", "Active",
            "Churned", "Churned", "Active", "Active", "Churned", "Churned", "Active", "Active", "Churned", "Active"
        ]
    }
    
    df = pd.DataFrame(data)
    
    # Add a completely duplicate row
    df = pd.concat([df, df.iloc[[0]]], ignore_index=True)
    
    df.to_csv(output_path, index=False)
    print(f"Sample messy churn data generated at: {os.path.abspath(output_path)}")

if __name__ == "__main__":
    generate_messy_churn_data()
