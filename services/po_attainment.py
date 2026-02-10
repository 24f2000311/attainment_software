"""
PO Attainment Service
=====================

This module calculates Program Outcome (PO) attainment based on the already calculated
Course Outcome (CO) attainment levels and the CO-PO mapping matrix.

Formula:
    PO_Value = Sum(CO_Attainment_Level * Mapping_Strength) / Sum(Mapping_Strengths)
    
    Where:
    - CO_Attainment_Level is the final level (0-3) achieved by the CO.
    - Mapping_Strength is the correlation (1=Low, 2=Medium, 3=High) between the CO and PO.
"""

def calculate_po_attainment(co_attainment, co_po_df):
    """
    Calculates the attainment value for each Program Outcome (PO).
    
    Args:
        co_attainment (dict): Dictionary of CO results.
                              Format: {'CO1': {'Attainment_Level': 3}, ...}
                              (Can be nested, but must contain 'Attainment_Level' at top or 'Final')
                              
        co_po_df (pd.DataFrame): CO-PO Mapping Configuration. Columns: 'CO_ID', 'PO1', 'PO2', etc.
        
    Returns:
        dict: Attainment results for each PO.
              {
                  'PO1': {'PO_Value': 2.45, 'PO_Level': 2},
                  'PO2': ...
              }
    """
    po_results = {}

    # Extract PO columns (everything except CO_ID)
    po_columns = [col for col in co_po_df.columns if col != "CO_ID"]

    for po in po_columns:
        numerator = 0
        denominator = 0

        for _, row in co_po_df.iterrows():
            co = row["CO_ID"]
            strength = row[po]

            # Skip if no mapping exists
            if strength == 0:
                continue
            
            # Extract CO Level safely
            # Supports both {CO: {Level: 3}} and {CO: {Final: {Level: 3}}} structures
            co_data = co_attainment.get(co, {})
            if "Final" in co_data:
                 co_level = co_data["Final"].get("Attainment_Level", 0)
            else:
                 co_level = co_data.get("Attainment_Level", 0)

            numerator += co_level * strength
            denominator += strength

        # Avoid division by zero
        po_value = round(numerator / denominator, 2) if denominator != 0 else 0

        po_results[po] = {
            "PO_Value": po_value,
            "PO_Level": round(po_value) # Rounded to nearest integer level
        }

    return po_results
