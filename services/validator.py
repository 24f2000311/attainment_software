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
