REQUIRED_CONFIG_SHEETS= [ "CO_List",
    "PO_List",
    "CO_PO_Mapping",
    "Assessment_Weightage",
    "Attainment_Targets",
    "Question_CO_Map",
    "Settings"
]

def validate_config_sheets(sheets):
    missing_sheets = [sheet for sheet in REQUIRED_CONFIG_SHEETS if sheet not in sheets] 
    
    if missing_sheets:
        raise ValueError(f'Missing required sheets in config file: {", ".join(missing_sheets)}')
    
    return True

def validate_marks_basic(marks_sheets):
    for sheet, df in marks_sheets.items():
        if "Student_Name" not in df.columns:
            raise ValueError(f"Student_Name missing in marks sheet: {sheet}")

        if df.empty:
            raise ValueError(f"No data in marks sheet: {sheet}")

def validate_assessment_weights(weights_df):
    """
    Validates that weights sum to 1.0 for each Mode (Direct/Indirect).
    Raises ValueError if weights are invalid.
    """
    # 1. Default Mode to 'Direct' if missing
    if "Mode" not in weights_df.columns:
        weights_df = weights_df.copy()
        weights_df["Mode"] = "Direct"
    else:
        weights_df["Mode"] = weights_df["Mode"].fillna("Direct")

    # 2. Group by Mode and calculate total raw weight
    mode_totals = weights_df.groupby("Mode")["Weight"].sum()

    errors = []
    
    for mode, total in mode_totals.items():
        # Check if total is approximately 1.0 (allow small float error)
        if not (0.99 <= total <= 1.01):
            errors.append(f"Total weight for '{mode}' assessments is {round(total, 2)}. It must be exactly 1.0.")

    if errors:
        raise ValueError("\n".join(errors))

    return True
