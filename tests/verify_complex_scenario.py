
import sys
import os
import pandas as pd

# Add parent directory to path to import services
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.co_attainment import calculate_weighted_co_attainment
from services.normalizer import normalize_marks
from services.cleaning_normalized_data import clean_row
from services.validator import validate_co_weights

BASE_DIR = os.path.join(os.getcwd(), "Test_data", "New_Architecture", "Complex_Scenario")

def load_excel_data(path):
    print(f"Loading {path}...")
    xls = pd.ExcelFile(path)
    sheets = {sheet: xls.parse(sheet) for sheet in xls.sheet_names}
    return sheets

def run_verification():
    print("==========================================")
    print("   COMPLEX SCENARIO VERIFICATION TEST     ")
    print("==========================================")

    config_path = os.path.join(BASE_DIR, "Config.xlsx")
    marks_path = os.path.join(BASE_DIR, "Marks_Mixed.xlsx")
    
    if not os.path.exists(config_path) or not os.path.exists(marks_path):
        print(">> ERROR: Test data not found. Run 'tools/generate_test_data_new_arch.py' first.")
        return

    # 1. Load Data
    config_sheets = load_excel_data(config_path)
    marks_sheets = load_excel_data(marks_path)
    
    # 2. Validation (New Step)
    print("\n[Step 0] Validating Configuration...")
    try:
        validate_co_weights(config_sheets["CO_Weightage"])
        print(">> Success: CO Weights are valid (Direct=1.0, Indirect=1.0 split confirmed).")
    except Exception as e:
        print(f">> ERROR in Validation: {e}")
        return

    # 3. Prepare for Normalizer
    question_map = config_sheets["Question_CO_Map"]
    co_weights_df = config_sheets["CO_Weightage"]
    
    # Create co_weights dict
    co_weights = dict(zip(
        zip(co_weights_df["Assessment"], co_weights_df["CO_ID"]),
        co_weights_df["Weight"]
    ))
    
    # 3. Normalize
    print("\n[Step 1] Normalizing Marks...")
    try:
        normalized_rows = normalize_marks(marks_sheets, question_map, co_weights)
        cleaned_data = [clean_row(r) for r in normalized_rows]
        print(f">> Success: {len(cleaned_data)} rows processed.")
    except Exception as e:
        print(f">> ERROR in Normalization: {e}")
        return

    # 4. Calculate Attainment
    print("\n[Step 2] Calculating Weighted CO Attainment...")
    # This function internally handles Direct/Indirect splitting using "Mode" if available
    try:
        results = calculate_weighted_co_attainment(cleaned_data, config_sheets)
    except Exception as e:
         print(f">> ERROR in Attainment Calculation: {e}")
         return
         
    # 5. Review Results
    print("\n[Step 3] Reviewing Results:")
    print(f"{'CO':<5} | {'Direct %':<10} | {'Indir %':<10} | {'Final %':<10} | {'Level':<5}")
    print("-" * 55)
    
    for co, data in sorted(results.items()):
        direct = data['Direct']['Achieved_%']
        indirect = data['Indirect']['Achieved_%']
        final_pct = data['Final']['Achieved_%']
        level = data['Final']['Attainment_Level']
        
        print(f"{co:<5} | {direct:<10} | {indirect:<10} | {final_pct:<10} | {level:<5}")
        
    print("\n[Verification Check - Mixed Scenario]")
    
    # Check CO1-3 (High)
    high_cos = ["CO1", "CO2", "CO3"]
    high_pass = all(results[co]['Final']['Attainment_Level'] >= 2 for co in high_cos)
    
    # Check CO4-6 (Low)
    low_cos = ["CO4", "CO5", "CO6"]
    low_pass = all(results[co]['Final']['Attainment_Level'] < 2 for co in low_cos)
    
    if high_pass and low_pass:
        print(">> PASS: Mixed Scenario Verified (CO1-3 High, CO4-6 Low).")
    else:
        print(f">> FAIL: Mixed Scenario Mismatch.\n   High Group (Expected >=2): {high_pass}\n   Low Group (Expected <2): {low_pass}")

if __name__ == "__main__":
    run_verification()
