from collections import defaultdict


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
