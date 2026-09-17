import os
import sys
import json
import joblib

def predict_no_show(processed_df, models_dir="models"):
    """
    Predicts the No-show probability and risk category for a processed patient dataframe.
    
    Args:
        processed_df (pd.DataFrame): 103-feature preprocessed dataframe.
        models_dir (str): Path to the directory containing model artifacts.
        
    Returns:
        dict: A dictionary containing the prediction results.
    """
    # --------------------------------------------------------------------------
    # 1. LOAD ARTIFACTS WITH ERROR HANDLING
    # --------------------------------------------------------------------------
    model_path = os.path.join(models_dir, "medguard_xgboost_final.pkl")
    config_path = os.path.join(models_dir, "medguard_model_config.json")
    schema_path = os.path.join(models_dir, "medguard_feature_schema.json")
    
    if not os.path.exists(model_path):
        # Fallback for nested tests
        model_path = os.path.join("..", model_path)
        config_path = os.path.join("..", config_path)
        schema_path = os.path.join("..", schema_path)
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Missing model file at: {model_path}")
            
    try:
        model = joblib.load(model_path)
    except Exception as e:
        raise RuntimeError(f"Failed to load XGBoost model: {e}")
        
    try:
        with open(config_path, "r") as f:
            config = json.load(f)
    except Exception as e:
        raise RuntimeError(f"Failed to load model configuration: {e}")
        
    try:
        with open(schema_path, "r") as f:
            schema = json.load(f)
    except Exception as e:
        raise RuntimeError(f"Failed to load feature schema: {e}")
        
    # --------------------------------------------------------------------------
    # 2. VERIFY FEATURE SCHEMA
    # --------------------------------------------------------------------------
    expected_features = schema.get("features", [])
    expected_count = schema.get("feature_count", len(expected_features))
    
    if processed_df.shape[1] != expected_count:
        raise ValueError(f"Feature count mismatch. Expected {expected_count}, got {processed_df.shape[1]}.")
        
    if list(processed_df.columns) != expected_features:
        raise ValueError("Feature order mismatch. The processed features do not match the strict schema order.")
        
    # --------------------------------------------------------------------------
    # 3. GENERATE PREDICTION
    # --------------------------------------------------------------------------
    try:
        # predict_proba returns an array of shape (n_samples, n_classes)
        # Index [0][1] extracts the probability of the positive class (No-show = 1) for the single record
        prob = float(model.predict_proba(processed_df)[0][1])
    except Exception as e:
        raise RuntimeError(f"Model prediction failed: {e}")
        
    # Apply the locked operating threshold
    threshold = config.get("operating_threshold", 0.55)
    prediction = int(prob >= threshold)
    
    # --------------------------------------------------------------------------
    # 4. DETERMINE RISK CATEGORY
    # --------------------------------------------------------------------------
    if prob < 0.40:
        risk_category = "Low"
    elif prob < 0.55:
        risk_category = "Moderate"
    else:
        risk_category = "High"
        
    # --------------------------------------------------------------------------
    # 5. RETURN RESULTS
    # --------------------------------------------------------------------------
    return {
        "no_show_probability": prob,
        "no_show_prediction": prediction,
        "no_show_risk_category": risk_category
    }
