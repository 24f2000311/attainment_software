import json
import pandas as pd
from services.co_attainment import calculate_weighted_co_attainment, determine_attainment_level
from services.normalizer import normalize_marks
from services.cleaning_normalized_data import clean_row

def load_excel_data(path):
    print(f"Loading {path}...")
    xls = pd.ExcelFile(path)
    sheets = {sheet: xls.parse(sheet) for sheet in xls.sheet_names}
    return sheets

def debug():
    config_file = r"c:\Users\madha\Desktop\attainment_software\Test_data\New_Architecture\Complex_Scenario\Config_Styled_Final.xlsx"
    marks_file = r"c:\Users\madha\Desktop\attainment_software\Test_data\New_Architecture\Complex_Scenario\Marks_Randomized_Interpolation.xlsx"
    
    config_sheets = load_excel_data(config_file)
    marks_sheets = load_excel_data(marks_file)
    
    question_map = config_sheets["Question_CO_Map"]
    co_weights_df = config_sheets["CO_Weightage"]
    
    co_weights = dict(zip(
        zip(co_weights_df["Assessment"], co_weights_df["CO_ID"]),
        co_weights_df["Weight"]
    ))
    
    # DEBUG
    print("Sheets in marks:", list(marks_sheets.keys()))
    print("Assessments in map:", question_map['Assessment'].unique() if 'Assessment' in question_map.columns else "No Assessment Column")
    df = next(iter(marks_sheets.values()))
    print(df.head())
    
    normalized_rows = normalize_marks(marks_sheets, question_map, co_weights)
    cleaned_data = [clean_row(r) for r in normalized_rows]
    
    try:
        settings_df = config_sheets["Settings"]
        settings = dict(zip(settings_df["Property"], settings_df["Value"]))
        direct_weight = float(settings.get("Direct Weightage", 80)) / 100.0
        indirect_weight = float(settings.get("Indirect Weightage", 20)) / 100.0
        if direct_weight > 1.0: direct_weight /= 100.0 
    except (KeyError, ValueError):
        direct_weight = 0.8
        indirect_weight = 0.2

    print(f"\nWeights => Direct: {direct_weight}, Indirect: {indirect_weight}")

    results = calculate_weighted_co_attainment(cleaned_data, config_sheets)
    print("\nResults:")
    for co, data in sorted(results.items()):
        print(f"{co}:")
        print(f"  Direct: Achieved {data['Direct']['Achieved_%']}% -> Level {data['Direct']['Attainment_Level']}")
        print(f"  Indirect: Achieved {data['Indirect']['Achieved_%']}% -> Level {data['Indirect']['Attainment_Level']}")
        print(f"  Final: Achieved {data['Final']['Achieved_%']}% -> Level {data['Final']['Attainment_Level']}")
        
    print(f"\nTotal rows in cleaned data: {len(cleaned_data)}")
        

if __name__ == "__main__":
    debug()
