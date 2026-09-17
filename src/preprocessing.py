import pandas as pd
import json
import os

def preprocess_patient(patient_data):
    """
    Preprocesses a single raw patient record to reproduce the exact 103-feature
    schema used to train the final XGBoost model.
    
    Args:
        patient_data (dict): A dictionary containing the raw patient features.
        
    Returns:
        pd.DataFrame: A 1-row dataframe containing the exact 103 expected features.
    """
    # 1. Convert the single record to a pandas DataFrame
    df = pd.DataFrame([patient_data])
    
    # 2. Recreate Temporal Features from Dates
    # Parse the strings into datetime objects as done in original preprocessing
    df['ScheduledDay'] = pd.to_datetime(df['ScheduledDay'])
    df['AppointmentDay'] = pd.to_datetime(df['AppointmentDay'])
    
    # Extract weekday names
    df['Appointment_Weekday'] = df['AppointmentDay'].dt.day_name()
    df['Scheduled_Weekday'] = df['ScheduledDay'].dt.day_name()
    
    # Extract month name
    df['Appointment_Month'] = df['AppointmentDay'].dt.month_name()
    
    # 3. Categorize Age into Groups
    # Define exact bins and labels used in the original notebook
    bins = [-1, 12, 64, 150]
    labels = ['Child', 'Adult', 'Senior']
    # Use pd.cut to bucket the ages
    df['AgeGroup'] = pd.cut(df['Age'], bins=bins, labels=labels)
    
    # 4. Encode Categorical Variables
    # These are the exact categorical columns used during training
    categorical_cols = ['Gender', 'Appointment_Weekday', 'Scheduled_Weekday', 'Appointment_Month', 'AgeGroup', 'Neighbourhood']
    
    # Perform one-hot encoding
    df_encoded = pd.get_dummies(df, columns=categorical_cols, drop_first=True)
    
    # Convert booleans to integers
    for col in df_encoded.columns:
        if df_encoded[col].dtype == 'bool':
            df_encoded[col] = df_encoded[col].astype(int)
            
    # 5. Drop Unneeded Columns
    columns_to_drop = ['PatientID', 'AppointmentID', 'ScheduledDay', 'AppointmentDay']
    df_encoded.drop(columns=columns_to_drop, inplace=True, errors='ignore')
    
    # 6. Align with the Final Feature Schema
    schema_path = "models/medguard_feature_schema.json"
    if not os.path.exists(schema_path):
        # Allow fallback for tests running from different directories
        schema_path = "../models/medguard_feature_schema.json"
        
    with open(schema_path, "r") as f:
        schema_data = json.load(f)
        
    expected_features = schema_data["features"]
    
    # Detect if the patient has any unexpected dummy columns (unseen categories)
    # The original notebook does not have a strategy for handling unseen categories,
    # so we explicitly reject them as requested by the user.
    current_columns = set(df_encoded.columns)
    expected_set = set(expected_features)
    
    unexpected_features = current_columns - expected_set
    if unexpected_features:
        raise ValueError(f"Raw patient data contains unseen categories that were not present in the training schema: {unexpected_features}")
        
    # Reindex the dataframe to match the EXACT schema order.
    # Any missing dummy columns (e.g., categories not present in this single row) 
    # will be created and filled with 0.
    df_final = df_encoded.reindex(columns=expected_features, fill_value=0)
    
    return df_final
