"""
Configuration Validator Service
===============================

This module ensures that the uploaded configuration Excel file contains all necessary sheets
and that the data within them adheres to required formats and constraints.
"""

REQUIRED_CONFIG_SHEETS= [ 
    "CO_List",
    "PO_List",
    "CO_PO_Mapping",
    # "Assessment_Weightage", # REMOVED: Now using CO_Weightage
    "CO_Weightage",           # NEW: Per-CO Assessment Weighting
    "Attainment_Targets",
    "Question_CO_Map",
    "Settings"
]

def validate_config_sheets(sheets):
    """
    Checks if all required sheets are present in the uploaded configuration file.
    
    Args:
        sheets (list): List of sheet names available in the file.
        
    Returns:
        bool: True if validation passes.
        
    Raises:
        ValueError: If any required sheet is missing.
    """
    missing_sheets = [sheet for sheet in REQUIRED_CONFIG_SHEETS if sheet not in sheets] 
    
    if missing_sheets:
        raise ValueError(f'Missing required sheets in config file: {", ".join(missing_sheets)}')
        
    co_list_df = sheets.get("CO_List")
    if co_list_df is not None:
        if "Target" not in co_list_df.columns:
            raise ValueError("CO_List sheet missing required 'Target' column. Please set targets for all COs.")
        if co_list_df["Target"].isna().any():
            raise ValueError("Target values must be set for all COs in the CO_List sheet.")
            
    po_list_df = sheets.get("PO_List")
    if po_list_df is not None:
        if "Target" not in po_list_df.columns:
            raise ValueError("PO_List sheet missing required 'Target' column. Please set targets for all POs.")
        if po_list_df["Target"].isna().any():
            raise ValueError("Target values must be set for all POs in the PO_List sheet.")
    
    return True

def validate_marks_basic(marks_sheets):
    """
    Performs basic validation on marks sheets.
    Ensures 'Student_Name' column exists and sheets are not empty.
    
    Args:
        marks_sheets (dict): {SheetName: DataFrame}
        
    Raises:
        ValueError: If validation fails.
    """
    for sheet, df in marks_sheets.items():
        if "Student_Name" not in df.columns:
            raise ValueError(f"Student_Name missing in marks sheet: {sheet}")

        if df.empty:
            raise ValueError(f"No data in marks sheet: {sheet}")

def validate_co_weights(co_weights_df):
    """
    Validates that for each Course Outcome (CO), the sum of assessment weights equals 1.0.
    
    New Rule:
    If 'Mode' column exists, weights must sum to 1.0 per (CO, Mode) pair.
    e.g. CO1 Direct = 1.0, CO1 Indirect = 1.0.
    
    Args:
        co_weights_df (pd.DataFrame): Data from 'CO_Weightage' sheet.
                                      Must contain 'CO_ID' and 'Weight' columns.
                                      Optional: 'Mode' column.
                                      
    Returns:
        bool: True if validation passes.
        
    Raises:
        ValueError: If 'CO_ID'/'Weight' columns missing or if weights do not sum to 1.0 (+/- 0.01).
    """
    # 1. Validation Columns existence
    if "CO_ID" not in co_weights_df.columns or "Weight" not in co_weights_df.columns:
        raise ValueError("CO_Weightage sheet must contain 'CO_ID' and 'Weight' columns.")

    errors = []

    # 2. Check if Mode validation is applicable
    if "Mode" in co_weights_df.columns:
        # Group by CO and Mode
        # We also need to handle cases where Mode might be empty/NaN? 
        # Ideally Mode should be mandatory if present.
        # Let's fillna with "Direct" to be safe or just group.
        
        # Standardize Mode
        df_clean = co_weights_df.copy()
        df_clean["Mode"] = df_clean["Mode"].fillna("Direct").astype(str).str.strip().str.title()
        
        co_mode_totals = df_clean.groupby(["CO_ID", "Mode"])["Weight"].sum()
        
        for (co, mode), total in co_mode_totals.items():
            if not (0.99 <= total <= 1.01):
                errors.append(f"Total weight for '{co}' ({mode}) is {round(total, 2)}. It must be exactly 1.0.")
    
    else:
        # Legacy Validation (Global Sum per CO = 1.0)
        co_totals = co_weights_df.groupby("CO_ID")["Weight"].sum()
        for co, total in co_totals.items():
            if not (0.99 <= total <= 1.01):
                 errors.append(f"Total weight for '{co}' is {round(total, 2)}. It must be exactly 1.0.")
             
    if errors:
        raise ValueError("\n".join(errors))

    return True
