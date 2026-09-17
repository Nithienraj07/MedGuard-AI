import os
import sys

# Ensure src can be imported
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from preprocessing import preprocess_patient
from predict import predict_no_show
from priority import calculate_priority

def run_pipeline(patient_data, models_dir="models"):
    """
    End-to-end wrapper for predicting MedGuard AI follow-up priority.
    
    Args:
        patient_data (dict): Raw input features of a single patient.
        models_dir (str): Path to the directory containing model artifacts.
        
    Returns:
        dict: A dictionary containing the final integrated prediction and priority results.
    """
    try:
        # 1. Preprocess the raw patient into a 103-feature DataFrame
        processed_df = preprocess_patient(patient_data)
        
        # 2. Predict no-show probability and risk category
        prediction_results = predict_no_show(processed_df, models_dir=models_dir)
        prob = prediction_results["no_show_probability"]
        
        # 3. Calculate Follow-up Priority Matrix based on vulnerability
        priority_results = calculate_priority(prob, patient_data)
        
        # 4. Assemble final results
        final_result = {
            "no_show_probability": prediction_results["no_show_probability"],
            "no_show_prediction": prediction_results["no_show_prediction"],
            "no_show_risk_category": prediction_results["no_show_risk_category"],
            "vulnerability_indicator_count": priority_results["vulnerability_indicator_count"],
            "vulnerability_category": priority_results["vulnerability_category"],
            "follow_up_priority": priority_results["follow_up_priority"]
        }
        
        return final_result
        
    except Exception as e:
        raise RuntimeError(f"Pipeline execution failed: {e}")
