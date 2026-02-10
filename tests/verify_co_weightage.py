
import sys
import os
import pandas as pd

# Standardize path to import services from parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.validator import validate_co_weights
from services.normalizer import normalize_marks
from services.co_scores import calculate_co_scores, convert_to_percentage
from services.cleaning_normalized_data import clean_row

def run_verification():
    print("==========================================")
    print("   CO-WISE WEIGHTING VERIFICATION TEST    ")
    print("==========================================")

    # ---------------------------------------------------------
    # 1. SETUP MOCK CONFIGURATION (CO_Weightage)
    # ---------------------------------------------------------
    # Scenario:
    # - CO1 is assessed in CCE1 (50%) and ET (50%)
    # - CO2 is assessed in CCE1 (30%) and ET (70%)
    # - CO3 is assessed ONLY in ET (100%)
    
    print("\n[Step 1] Loading Mock Configuration...")
    co_weights_data = {
        "Assessment": ["CCE1", "ET",   "CCE1", "ET",   "ET"],
        "CO_ID":      ["CO1",  "CO1",  "CO2",  "CO2",  "CO3"],
        "Weight":     [0.5,    0.5,    0.3,    0.7,    1.0]
    }
    co_weights_df = pd.DataFrame(co_weights_data)
    print(co_weights_df)

    # ---------------------------------------------------------
    # 2. VALIDATION
    # ---------------------------------------------------------
    print("\n[Step 2] Validating Weights (Must sum to 1.0 per CO)...")
    try:
        validate_co_weights(co_weights_df)
        print(">> SUCCESS: Validation passed.")
    except Exception as e:
        print(f">> FAILURE: Validation error: {e}")
        return

    # Transform to dictionary map: (Assessment, CO) -> Weight
    co_weights_map = dict(zip(
        zip(co_weights_df["Assessment"], co_weights_df["CO_ID"]),
        co_weights_df["Weight"]
    ))

    # ---------------------------------------------------------
    # 3. SETUP MOCK STUDENT MARKS (FULL MARKS)
    # ---------------------------------------------------------
    print("\n[Step 3] Loading Mock Student Data (Full Marks)...")
    
    # Student A gets 10/10 in CCE1 and 50/50 in ET
    cce1_data = pd.DataFrame({
        "Student_Name": ["Student A"],
        "Q1": [10], # Mapped to CO1
        "Q2": [10], # Mapped to CO2
    })
    
    et_data = pd.DataFrame({
        "Student_Name": ["Student A"],
        "Q1": [50], # Mapped to CO1
        "Q2": [50], # Mapped to CO2
        "Q3": [100] # Mapped to CO3
    })

    marks_sheets = {
        "CCE1": cce1_data,
        "ET":   et_data
    }

    # ---------------------------------------------------------
    # 4. SETUP QUESTION MAPPING
    # ---------------------------------------------------------
    q_map_data = {
        "Assessment": ["CCE1", "CCE1", "ET",  "ET",  "ET"],
        "Question":   ["Q1",   "Q2",   "Q1",  "Q2",  "Q3"],
        "CO_ID":      ["CO1",  "CO2",  "CO1", "CO2", "CO3"],
        "Max_Marks":  [10,     10,     50,    50,    100]
    }
    q_map = pd.DataFrame(q_map_data)

    # ---------------------------------------------------------
    # 5. EXECUTE NORMALIZATION & CALCULATION
    # ---------------------------------------------------------
    print("\n[Step 4] Running Normalization & Calculation...")
    
    try:
        # Normalize
        normalized_rows = normalize_marks(marks_sheets, q_map, co_weights_map)
        cleaned_data = [clean_row(r) for r in normalized_rows]
        
        # Calculate Scores
        raw_scores = calculate_co_scores(cleaned_data)
        percentages = convert_to_percentage(raw_scores)
        
    except Exception as e:
        print(f">> FAILURE: Calculation crashed: {e}")
        return

    # ---------------------------------------------------------
    # 6. VERIFY RESULTS
    # ---------------------------------------------------------
    print("\n[Step 5] Verifying Results (Expect 100% for all)...")
    
    expected_results = {
        ("Student A", "CO1"): 100.0,
        ("Student A", "CO2"): 100.0,
        ("Student A", "CO3"): 100.0
    }
    
    all_passed = True
    for key, expected in expected_results.items():
        actual = percentages.get(key, 0.0)
        print(f"  {key[1]}: Expected {expected}%, Got {actual}%")
        
        if actual != expected:
            print(f"  >> ERROR: {key[1]} calculation is incorrect!")
            all_passed = False
    
    if all_passed:
        print("\n>> TEST PASSED: All CO attainment calculations are correct.")
    else:
        print("\n>> TEST FAILED: Some calculations were incorrect.")

if __name__ == "__main__":
    run_verification()
