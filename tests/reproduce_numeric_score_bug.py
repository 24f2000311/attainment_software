
import sys
import os
import pandas as pd

# Add parent directory to path to import services
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.co_scores import calculate_co_numeric_scores

def test_numeric_score_discrepancy():
    print("Testing CO Numeric Score Logic...")

    # Scenario:
    # 5 students.
    # Target: 60% students must score > 60% marks for Level 3.
    
    # Case: All 5 students score 100%. 
    # - Attainment Calculation: 100% of students > 60% marks -> Level 3.
    # - Numeric Score Calculation (Current): 
    
    co_percentage_scores = {
        ("S1", "CO1"): 100.0,
        ("S2", "CO1"): 100.0,
        ("S3", "CO1"): 100.0,
        ("S4", "CO1"): 100.0,
        ("S5", "CO1"): 100.0,
    }

    numeric_scores = calculate_co_numeric_scores(co_percentage_scores)
    print(f"Scenario 1 (All 100%): Numeric Score = {numeric_scores['CO1']}")
    
    # Case: User Report. Indirect 0%, Direct 100%. CO Attained 100% -> Level 3.
    # But dashboard shows 2.
    
    # Let's inspect the logic in calculate_co_numeric_scores:
    # if percent >= 60: point = 3
    # ...
    # Average per CO.
    
    # If all score 100%, point is 3 for all. Average is 3. 
    # So why did the user see 2?
    
    # Maybe the user implies that *Attainment Level* was 3, but *Numeric Score* was 2.
    # Discrepancy implies they are different calculations.
    
    # Let's try a case where Attainment is Level 3, but Numeric Score is lower.
    # Level 3 requirement: > 70% of students cross threshold.
    # Suppose we have 10 students.
    # 8 students score 60% (Just pass). -> 80% pass -> Level 3.
    # 2 students score 0%.
    
    co_percentage_scores_2 = {}
    for i in range(8):
        co_percentage_scores_2[(f"S{i}", "CO2")] = 60.0 # Points: 3 (>=60 is 3 in current logic)
    for i in range(8, 10):
        co_percentage_scores_2[(f"S{i}", "CO2")] = 0.0  # Points: 0
        
    # Attainment Level Logic (Mental Check):
    # 8/10 passed (80%). If Target Level 3 is > 70%, then Attainment is Level 3.
    
    # Numeric Score Logic:
    # 8 students * 3 points = 24
    # 2 students * 0 points = 0
    # Average = 24 / 10 = 2.4
    
    numeric_scores_2 = calculate_co_numeric_scores(co_percentage_scores_2)
    print(f"Scenario 2 (80% pass with just 60 marks): Numeric Score = {numeric_scores_2['CO2']}")
    
    if numeric_scores_2['CO2'] < 3.0:
        print(">> Discrepancy found! Attainment is Level 3, but Numeric Score is < 3.")
    
    # CHECKING THE BUG REPORT DETAIL:
    # "even if the indirect assement setting is to be set 0 and direct to be 100"
    # "and co has attained 100 and level 3 still the co numeric on dashbaord was 2"
    
    # "co has attained 100" -> This likely means Attainment % (Percentage of students passing) is 100%.
    # If 100% students passed, they all have > target marks.
    # If all have > target marks (say 60%), then calculate_co_numeric_scores gives them 3 points?
    
    # Let's look at the code for calculate_co_numeric_scores again:
    # if percent >= 60: point = 3
    # elif percent >= 50: point = 2
    # elif percent >= 40: point = 1
    # else: point = 0
    
    # If the threshold for Attainment "Pass" was lower than 60? 
    # e.g. If "Attainment Target" Min Marks was 40%?
    # Then a student getting 45% would "Pass" (contribute to Attainment Level), 
    # but in Numeric Score they would get only 1 point.
    
    # BUT, standard is usually 60%.
    
    # Possibility 2: The "Numeric Score" on the dashboard is actually pulling "Attainment Level" from somewhere else?
    # Or is it calculated purely from Direct scores and ignoring weights?
    # The user mentioned "indirect setting 0, direct 100".
    # This suggests the Numeric Score function might NOT be using the weighted data correctly, 
    # or it is unaware of the Direct/Indirect split and simply taking raw averages?
    
    # Wait, calculate_co_numeric_scores takes `co_percentage_scores`.
    # These are RAW scores from `calculate_co_scores`.
    # They are NOT weighted by Direct/Indirect config if that config is applied *after* this step.
    
    # In `co_attainment.py`, `calculate_weighted_co_attainment` logic:
    # 1. Splits Direct/Indirect data.
    # 2. Calculates Achieved % for each (Attainment Metric).
    # 3. Merges them.
    
    # BUT where is `calculate_co_numeric_scores` called?
    # Need to check `cqi_routes.py` or `dashboard` logic to see WHAT is fed into it.
    
if __name__ == "__main__":
    test_numeric_score_discrepancy()
