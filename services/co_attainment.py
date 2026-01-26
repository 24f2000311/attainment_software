from collections import defaultdict
from services.co_scores import calculate_co_scores, convert_to_percentage

def calculate_achieved_percentage(co_percentages, targets_df):
    """
    Calculates the percentage of students achieving >= target min marks for each CO.
    Returns: {CO: Achieved_%}
    """
    achieved_results = {}
    
    # Group by CO
    co_group = defaultdict(list)
    for (student, co), percent in co_percentages.items():
        co_group[co].append(percent)

    # Note: Target lookup is needed to know "Min_Marks". 
    # Usually Min_Marks is same for all levels or we take a base.
    # NBA Standard: Usually we check against a Set Target (e.g. 60% marks).
    # Since targets_df defines Levels based on % of students, we need to know WHICH Min_Marks to use.
    # We will assume the target definition implies a consistent "Min Marks" across levels 
    # OR we use the lowest level's min marks as the baseline for "Attainment".
    # However, common NBA practice: "Percentage of students scoring > X% marks". The X is fixed usually.
    # Let's extract the target Min_Marks from the highest level (3) as standard, or iterate.
    
    # To keep fully flexible: We will use the target definition for Level 1 (Entry level) 
    # to count "Students who Attempted/Passed" or use the row logic provided in targets.
    
    # But wait, the previous code iterated through levels. 
    # The NEW requirement says: "Compute Final CO Score using (Direct*0.8 + Indirect*0.2) -> Then Level."
    # This implies we are averaging the "Achieved Percentage" (e.g. 70% students passed Direct, 80% Indirect -> Final 72%).
    
    for co, percents in co_group.items():
        total_students = len(percents)
        if total_students == 0:
            achieved_results[co] = 0.0
            continue
            
        # We need a reference "Min_Marks" to define "Success".
        # Assuming all levels share the same "Min_Marks" requirement but differ in "Min_Students_%".
        # Let's peek at the first row of targets to get the mark threshold.
        # If targets vary in Min_Marks per level, this split logic is ambiguous.
        # Standard Assumption: Min marks is constant (e.g. 60%), levels depend on student count (e.g. 60%, 70%, 80% of class).
        
        reference_min_marks = targets_df.iloc[0]["Min_Marks_%"] 
        # Check if any row has different Min_Marks - if so, this logic is complex.
        # For this implementation, we take the MAX min_marks to be safe or average? 
        # Let's trust the first row as the definition of "Target Marks".
        
        achieved_count = sum(p >= reference_min_marks for p in percents)
        achieved_percent = (achieved_count / total_students) * 100
        achieved_results[co] = achieved_percent

    return achieved_results


def determine_attainment_level(achieved_percent, targets_df):
    """
    Look up the Attainment Level based on the Achieved Percentage of Students.
    """
    for _, row in targets_df.sort_values("Level", ascending=False).iterrows():
        level = int(row["Level"])
        # min_marks = row["Min_Marks_%"] # Already used in step 1
        min_students = row["Min_Students_%"]

        if achieved_percent >= min_students:
            return level
    return 0


def calculate_co_attainment(co_percentages, targets_df):
    """
    Legacy/Wrapper function if needed, or new logic can call the parts.
    Current usage expects a dict of {CO: {Attainment_Level: X, Achieved_%: Y}}
    """
    achieved_map = calculate_achieved_percentage(co_percentages, targets_df)
    results = {}
    
    for co, achieved_percent in achieved_map.items():
        level = determine_attainment_level(achieved_percent, targets_df)
        results[co] = {
            "Attainment_Level": level,
            "Achieved_%": round(achieved_percent, 2)
        }
    return results

def process_attainment_subset_percentage(data, config_sheets):
    """
    Helper: Returns {CO: Achieved_%} for a subset of data
    """
    if not data:
        return {}
    scores = calculate_co_scores(data)
    percentages = convert_to_percentage(scores)
    return calculate_achieved_percentage(percentages, config_sheets["Attainment_Targets"])

def calculate_weighted_co_attainment(cleaned_normalized_data, config_sheets):
    """
    Calculates CO attainment with separate Direct/Indirect weightings.
    """
    # 1. Get Settings (Global Weights)
    try:
        settings_df = config_sheets["Settings"]
        settings = dict(zip(settings_df["Property"], settings_df["Value"]))
        direct_weight = float(settings.get("Direct Weightage", 80)) / 100.0
        indirect_weight = float(settings.get("Indirect Weightage", 20)) / 100.0
        
        if direct_weight > 1.0: direct_weight /= 100.0 
        
    except (KeyError, ValueError):
        direct_weight = 0.8
        indirect_weight = 0.2

    # 2. Get Assessment Modes
    assessment_df = config_sheets["Assessment_Weightage"]
    if "Mode" in assessment_df.columns:
        assessment_mode_map = dict(zip(assessment_df["Assessment"], assessment_df["Mode"]))
    else:
        assessment_mode_map = {}

    # 3. Split Data
    direct_data = []
    indirect_data = []

    for record in cleaned_normalized_data:
        mode = assessment_mode_map.get(record["Assessment"], "Direct") 
        if str(mode).strip().lower() == "indirect":
            indirect_data.append(record)
        else:
            direct_data.append(record)

    # 4. Calculate Achieved % for subsets (Metric Calculation Step)
    direct_achieved = process_attainment_subset_percentage(direct_data, config_sheets)
    indirect_achieved = process_attainment_subset_percentage(indirect_data, config_sheets)

    # 5. Merge and Calculate Final Attainment Level
    final_results = {}
    all_cos = set(direct_achieved.keys()) | set(indirect_achieved.keys())
    
    targets_df = config_sheets["Attainment_Targets"]

    for co in all_cos:
        d_im = direct_achieved.get(co, 0.0)
        i_im = indirect_achieved.get(co, 0.0)

        # Weighted Average of the "Achieved Percentage" (e.g. 60% of students passed Direct)
        final_achieved_percent = (d_im * direct_weight) + (i_im * indirect_weight)
        
        # Determine Level based on this weighted percentage
        final_level = determine_attainment_level(final_achieved_percent, targets_df)

        final_results[co] = {
            "Direct": {
                "Achieved_%": round(d_im, 2),
                # Optional: Look up level just for display? 
                "Attainment_Level": determine_attainment_level(d_im, targets_df)
            },
            "Indirect": {
                "Achieved_%": round(i_im, 2),
                "Attainment_Level": determine_attainment_level(i_im, targets_df)
            },
            "Final": {
                "Achieved_%": round(final_achieved_percent, 2),
                "Attainment_Level": final_level
            }
        }
    return final_results
