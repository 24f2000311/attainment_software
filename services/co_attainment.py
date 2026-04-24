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
            
        reference_min_marks = targets_df.iloc[0]["Min_Marks_%"] 
        
        achieved_count = sum(p >= reference_min_marks for p in percents)
        achieved_percent = (achieved_count / total_students) * 100
        achieved_results[co] = achieved_percent

    return achieved_results


def determine_attainment_level(achieved_percent, targets_df):
    """
    Determines the Attainment Level (0.00-3.00) based on the percentage of students who achieved the target.
    Interpolates continuously between levels based on the configured thresholds in `Attainment_Targets`.
    
    Args:
        achieved_percent (float): Percentage of class meeting the threshold (e.g., 72.5%)
        targets_df (pd.DataFrame): Configuration sheet 'Attainment_Targets' containing:
                                   - Level (3, 2, 1)
                                   - Min_Students_% (e.g., 70, 60, 50)
                                   
    Returns:
        float: The interpolated attainment level (e.g. 2.51, 1.85, 0.40).
    """
    targets_df = targets_df.sort_values("Level", ascending=True)
    
    levels_data = []
    for _, row in targets_df.iterrows():
        levels_data.append((int(row["Level"]), float(row["Min_Students_%"])))
        
    if not levels_data:
        return 0.0
        
    max_level, max_threshold = levels_data[-1]
    
    if achieved_percent >= max_threshold:
        return float(max_level)
        
    # Add base level (0, 0.0) for interpolation below the first threshold
    levels_data.insert(0, (0, 0.0))
    
    for i in range(len(levels_data) - 1):
        curr_level, curr_threshold = levels_data[i]
        next_level, next_threshold = levels_data[i+1]
        
        if curr_threshold <= achieved_percent < next_threshold:
            diff_thresh = next_threshold - curr_threshold
            if diff_thresh == 0:
                return float(curr_level)
                
            if curr_level == 0:
                base_val = 0.01
            elif curr_level == 1:
                base_val = 1.01
            elif curr_level == 2:
                base_val = 2.01
            else:
                base_val = float(curr_level) + 0.01
                
            interpolated = base_val + 0.99 * (achieved_percent - curr_threshold) / diff_thresh
            return round(interpolated, 2)
                
    return 0.0


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
    
    This function calculates the percentage of students meeting the target threshold
    using a Question-wise approach:
    1. Calculate achievement percentage per Question.
    2. Average the question achievement percentages per (Assessment, CO).
    3. Compute the final weighted average for each CO using the configured assessment weights.
    
    Args:
        data (list): List of row dicts (Student, Assessment, Question, CO, Marks, Max_Marks, Weight)
        config_sheets (dict): Full configuration
        
    Returns:
        dict: {CO: {"Achieved_%": float, "Attainment_Level": float}}
    """
    if not data:
        return {}
        
    targets_df = config_sheets["Attainment_Targets"]
    # Usually targets_df contains 'Min_Marks_%'
    reference_min_marks = float(targets_df.iloc[0]["Min_Marks_%"])
    
    # 1. Group data by (Assessment, CO, Question)
    question_data = defaultdict(list)
    for row in data:
        key = (row["Assessment"], row["CO"], row["Question"])
        question_data[key].append(row)
        
    # 2. Calculate achieved percentage per question
    question_achieved = {}
    for key, rows in question_data.items():
        total_students = len(rows)
        if total_students == 0:
            question_achieved[key] = 0.0
            continue
            
        achieved_count = 0
        for r in rows:
            if r["Max_Marks"] > 0:
                pct = (r["Marks"] / r["Max_Marks"]) * 100.0
                if pct >= reference_min_marks:
                    achieved_count += 1
                    
        question_achieved[key] = (achieved_count / total_students) * 100.0

    # 3. Average achieved percentages for each (Assessment, CO)
    assessment_co_data = defaultdict(list)
    assessment_co_weights = {}
    
    for (assessment, co, question), achieved_pct in question_achieved.items():
        assessment_co_data[(assessment, co)].append(achieved_pct)
        
    for row in data:
        key = (row["Assessment"], row["CO"])
        # Ensure we capture the weight for this Assessment-CO pair
        if key not in assessment_co_weights:
            assessment_co_weights[key] = row["Weight"]

    assessment_co_achieved = {}
    for key, pcts in assessment_co_data.items():
        assessment_co_achieved[key] = sum(pcts) / len(pcts)
        
    # 4. Compute final weighted sum/average per CO
    co_achieved_pcts = defaultdict(float)
    co_achieved_levels = defaultdict(float)
    co_weight_sums = defaultdict(float)
    
    for (assessment, co), achieved_pct in assessment_co_achieved.items():
        weight = assessment_co_weights.get((assessment, co), 0.0)
        
        # Convert this specific assessment's percentage to a Level
        level = determine_attainment_level(achieved_pct, targets_df)
        
        co_achieved_pcts[co] += achieved_pct * weight
        co_achieved_levels[co] += level * weight
        co_weight_sums[co] += weight
        
    final_results = {}
    for co in co_weight_sums:
        total_weight = co_weight_sums[co]
        if total_weight > 0:
            final_pct = round(co_achieved_pcts[co] / total_weight, 2)
            final_level = round(co_achieved_levels[co] / total_weight, 2)
            final_results[co] = {
                "Achieved_%": final_pct,
                "Attainment_Level": final_level
            }
        else:
            final_results[co] = {
                "Achieved_%": 0.0,
                "Attainment_Level": 0.0
            }
            
    return final_results

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

    for co in all_cos:
        d_data = direct_achieved.get(co, {"Achieved_%": 0.0, "Attainment_Level": 0.0})
        i_data = indirect_achieved.get(co, {"Achieved_%": 0.0, "Attainment_Level": 0.0})

        d_im = d_data["Achieved_%"]
        d_level = d_data["Attainment_Level"]
        
        i_im = i_data["Achieved_%"]
        i_level = i_data["Attainment_Level"]

        # Weighted Average of the "Achieved Percentage"
        final_achieved_percent = (d_im * direct_weight) + (i_im * indirect_weight)
        
        # Final Level is the weighted average of the Direct and Indirect Levels
        final_level = (d_level * direct_weight) + (i_level * indirect_weight)

        final_results[co] = {
            "Direct": {
                "Achieved_%": round(d_im, 2),
                "Attainment_Level": round(d_level, 2)
            },
            "Indirect": {
                "Achieved_%": round(i_im, 2),
                "Attainment_Level": round(i_level, 2)
            },
            "Final": {
                "Achieved_%": round(final_achieved_percent, 2),
                "Attainment_Level": round(final_level, 2)
            }
        }
    return final_results
