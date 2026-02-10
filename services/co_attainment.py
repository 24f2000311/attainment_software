"""
CO Attainment Service
=====================

This module handles the core logic for calculating Course Outcome (CO) attainment levels.
It supports:
1. Normalizing raw marks into percentage scores.
2. Calculating "Achieved Percentage" of students meeting target thresholds.
3. Determining Attainment Levels (0-3) based on targets.
4. Handling Direct and Indirect assessment weights separately.
5. Aggregating final results.
"""

from collections import defaultdict
from services.co_scores import calculate_co_scores

# ------------------------------------------------------------------
#  HELPER FUNCTIONS
# ------------------------------------------------------------------

def convert_to_percentage(co_scores):
    """
    Converts raw normalized scores (0.0 to 1.0) into percentages (0 to 100).
    
    Args:
        co_scores (dict): {(Student, CO): Score_Fraction}
        
    Returns:
        dict: {(Student, CO): Percentage_Score}
    """
    return {k: v * 100 for k, v in co_scores.items()}

def calculate_achieved_percentage(co_percentages, targets_df):
    """
    Calculates the percentage of students who achieved the target minimum marks for each CO.
    
    Logic:
        1. Identify the 'Min_Marks_%' threshold from targets (usually 60%).
        2. Count how many students scored >= this threshold.
        3. Calculate (Count / Total Students) * 100.
    
    Args:
        co_percentages (dict): {(Student, CO): Percentage}
        targets_df (pd.DataFrame): Configuration sheet 'Attainment_Targets'
        
    Returns:
        dict: {CO_Name: Achieved_Percentage_of_Students}
    """
    achieved_results = {}
    
    # 1. Group scores by CO
    co_group = defaultdict(list)
    for (student, co), percent in co_percentages.items():
        co_group[co].append(percent)

    # 2. Process each CO
    for co, percents in co_group.items():
        total_students = len(percents)
        if total_students == 0:
            achieved_results[co] = 0.0
            continue
            
        # Get threshold from first row of targets (Standard Assumption)
        # TODO: Support variable thresholds per level if needed.
        reference_min_marks = targets_df.iloc[0]["Min_Marks_%"] 
        
        achieved_count = sum(p >= reference_min_marks for p in percents)
        achieved_percent = (achieved_count / total_students) * 100
        achieved_results[co] = achieved_percent

    return achieved_results


def determine_attainment_level(achieved_percent, targets_df):
    """
    Determines the Attainment Level (0-3) based on the percentage of students who achieved the target.
    
    Args:
        achieved_percent (float): Percentage of class meeting the threshold (e.g., 72.5%)
        targets_df (pd.DataFrame): Configuration sheet 'Attainment_Targets' containing:
                                   - Level (3, 2, 1)
                                   - Min_Students_% (e.g., 70, 60, 50)
                                   
    Returns:
        int: The highest level met (3, 2, 1, or 0).
    """
    # Sort targets high-to-low to find the highest match first
    for _, row in targets_df.sort_values("Level", ascending=False).iterrows():
        level = int(row["Level"])
        min_students = row["Min_Students_%"]

        if achieved_percent >= min_students:
            return level
            
    return 0


def calculate_co_attainment(co_percentages, targets_df):
    """
    Legacy wrapper function to calculate attainment for a single dataset without weighting split.
    Typically used for simple, non-weighted scenarios.
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
    Processes a subset of data (e.g., only Direct assessments) to calculate achievement percentage.
    
    IMPORTANT:
    This function normalizes scores against the TOTAL WEIGHT of the subset.
    If a student scores 100% in a subset that only had 0.8 weight, their raw score is 0.8.
    We normalize this back to 1.0 (100%) so that attainment thresholds work correctly.
    
    Args:
        data (list): List of row dicts (Student, CO, Marks, Weight, etc.)
        config_sheets (dict): Full configuration
        
    Returns:
        dict: {CO: Achieved_%}
    """
    if not data:
        return {}
        
    # 1. Calculate Raw Scores (Sum of Marks/Max * Weight)
    scores = calculate_co_scores(data)
    
    # 2. Calculate Total Weight per CO for this subset (Normalization Base)
    co_total_weights = defaultdict(float)
    processed_configs = set() # (Assessment, CO)
    
    for row in data:
        key = (row["Assessment"], row["CO"])
        if key not in processed_configs:
            co_total_weights[row["CO"]] += row["Weight"]
            processed_configs.add(key)
            
    # 3. Normalize Scores to 0-100% Scale
    percentages = {}
    for (student, co), raw_score in scores.items():
        max_weight = co_total_weights.get(co, 1.0)
        
        if max_weight > 0:
            final_percent = (raw_score / max_weight) * 100
        else:
            final_percent = 0.0
            
        percentages[(student, co)] = round(final_percent, 2)

    return calculate_achieved_percentage(percentages, config_sheets["Attainment_Targets"])

# ------------------------------------------------------------------
#  MAIN CALCULATION FUNCTION
# ------------------------------------------------------------------

def calculate_weighted_co_attainment(cleaned_normalized_data, config_sheets):
    """
    Calculates the Final CO Attainment considering Direct and Indirect Assessment weights.
    
    Process:
    1. Reads Global Weight settings (e.g., Direct=80%, Indirect=20%).
    2. Identifies Assessment Modes (Direct/Indirect) from Config.
    3. Splits data into Direct and Indirect subsets.
    4. Calculates "Achieved Student %" for each subset independently.
    5. Computes weighted average of Achieved %.
    6. Determines Final Attainment Level based on weighted average.
    
    Args:
        cleaned_normalized_data (list): Flattened list of student records.
        config_sheets (dict): Configuration DataFrames.
        
    Returns:
        dict: Structure containing Direct, Indirect, and Final results per CO.
              {
                  'CO1': {
                      'Direct': {'Achieved_%': 72.0, 'Attainment_Level': 3},
                      'Indirect': {'Achieved_%': 85.0, 'Attainment_Level': 3},
                      'Final': {'Achieved_%': 74.6, 'Attainment_Level': 3}
                  },
                  ...
              }
    """
    # 1. Get Settings (Global Weights)
    try:
        settings_df = config_sheets["Settings"]
        settings = dict(zip(settings_df["Property"], settings_df["Value"]))
        direct_weight = float(settings.get("Direct Weightage", 80)) / 100.0
        indirect_weight = float(settings.get("Indirect Weightage", 20)) / 100.0
        
        # Normalize if user entered >1.0
        if direct_weight > 1.0: direct_weight /= 100.0 
        
    except (KeyError, ValueError):
        direct_weight = 0.8
        indirect_weight = 0.2

    # 2. Get Assessment Modes
    # Checks 'Assessment_Weightage' first (Legacy). 
    # If missing, checks if 'CO_Weightage' has a 'Mode' column (New).
    # Defaults to "Direct" if neither finds a Mode.
    assessment_mode_map = {}
    
    if "Assessment_Weightage" in config_sheets:
        assessment_df = config_sheets["Assessment_Weightage"]
        if "Mode" in assessment_df.columns:
            assessment_mode_map = dict(zip(assessment_df["Assessment"], assessment_df["Mode"]))
            
    elif "CO_Weightage" in config_sheets:
        # Fallback: Check if CO_Weightage has a "Mode" column
        co_weight_df = config_sheets["CO_Weightage"]
        if "Mode" in co_weight_df.columns:
            # Drop duplicates in case multiple COs map to same assessment with same mode
            temp_df = co_weight_df[["Assessment", "Mode"]].drop_duplicates()
            assessment_mode_map = dict(zip(temp_df["Assessment"], temp_df["Mode"]))

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
