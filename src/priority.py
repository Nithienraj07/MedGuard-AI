def calculate_priority(no_show_probability, patient_data):
    """
    Calculates the Follow-up Priority based on a 2-dimensional matrix of 
    No-show Risk and Documented Patient Vulnerability.
    
    This is an operational decision-support score, not a clinical severity score.
    
    Args:
        no_show_probability (float): The probability (0.0 to 1.0) of a no-show.
        patient_data (dict): Raw patient information containing:
            - 'Age'
            - 'Hypertension'
            - 'Diabetes'
            - 'Alcoholism'
            - 'Handicap'
            
    Returns:
        dict: A structured dictionary containing the priority results.
    """
    
    # --------------------------------------------------------------------------
    # 1. NO-SHOW RISK CATEGORY
    # --------------------------------------------------------------------------
    if no_show_probability < 0.40:
        no_show_risk_category = "Low"
    elif no_show_probability < 0.55:
        no_show_risk_category = "Moderate"
    else:
        no_show_risk_category = "High"
        
    # --------------------------------------------------------------------------
    # 2. VULNERABILITY INDICATORS
    # --------------------------------------------------------------------------
    indicator_count = 0
    
    # Age indicator
    # Age = -1 is treated as unknown (0 indicators)
    age = patient_data.get('Age', 0)
    if age >= 65:
        indicator_count += 1
        
    # Chronic conditions
    if patient_data.get('Hypertension', 0) == 1:
        indicator_count += 1
        
    if patient_data.get('Diabetes', 0) == 1:
        indicator_count += 1
        
    if patient_data.get('Alcoholism', 0) == 1:
        indicator_count += 1
        
    # Handicap indicator
    # Handicap > 0 counts as exactly 1 indicator, regardless of severity (1-4)
    if patient_data.get('Handicap', 0) > 0:
        indicator_count += 1
        
    # --------------------------------------------------------------------------
    # 3. VULNERABILITY CATEGORY
    # --------------------------------------------------------------------------
    if indicator_count == 0:
        vulnerability_category = "Low Vulnerability"
    else:
        vulnerability_category = "Higher Vulnerability"
        
    # --------------------------------------------------------------------------
    # 4. FINAL FOLLOW-UP PRIORITY MATRIX
    # --------------------------------------------------------------------------
    if no_show_risk_category == "Low":
        if vulnerability_category == "Low Vulnerability":
            follow_up_priority = "Low"
        else: # Higher Vulnerability
            follow_up_priority = "Moderate"
            
    elif no_show_risk_category == "Moderate":
        if vulnerability_category == "Low Vulnerability":
            follow_up_priority = "Moderate"
        else: # Higher Vulnerability
            follow_up_priority = "High"
            
    elif no_show_risk_category == "High":
        if vulnerability_category == "Low Vulnerability":
            follow_up_priority = "High"
        else: # Higher Vulnerability
            follow_up_priority = "Highest"
            
    # --------------------------------------------------------------------------
    # 5. RETURN RESULTS
    # --------------------------------------------------------------------------
    return {
        "no_show_probability": no_show_probability,
        "no_show_risk_category": no_show_risk_category,
        "vulnerability_indicator_count": indicator_count,
        "vulnerability_category": vulnerability_category,
        "follow_up_priority": follow_up_priority
    }
