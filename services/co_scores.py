"""
CO Scoring Service
==================

This module handles the normalization of student marks based on their weightage.
It converts raw marks into a normalized score (0.0 to 1.0) relative to the total possible weight.
"""

from collections import defaultdict


def calculate_co_scores(normalized_data):
    """
    Aggregates student scores for each CO based on weighted assessments.
    
    Groups marks by the same Assessment & CO for a given student so that
    the defined configuration weight is only applied once to the sum of 
    those marks, not excessively multiplied per individual question.
        
    Args:
        normalized_data (list): List of dictionaries containing:
                                - Student_Name
                                - Assessment
                                - CO
                                - Marks
                                - Max_Marks
                                - Weight
                                
    Returns:
        dict: A dictionary mapping (Student, CO) tuples to their aggregated weighted score (float).
              {(Student_Name, CO_ID): Score}
    """
    # 1. Aggregate Marks and Max_Marks per Student, Assessment, and CO
    agg_data = defaultdict(lambda: {"Marks": 0.0, "Max_Marks": 0.0, "Weight": 0.0})
    for row in normalized_data:
        key = (row["Student_Name"], row["Assessment"], row["CO"])
        agg_data[key]["Marks"] += row["Marks"]
        agg_data[key]["Max_Marks"] += row["Max_Marks"]
        agg_data[key]["Weight"] = row["Weight"]  # Same weight applies to the whole Assessment-CO group
        
    # 2. Calculate final CO score using the aggregated fractions
    co_scores = defaultdict(float)
    for (student, assessment, co), data in agg_data.items():
        if data["Max_Marks"] > 0:
            contribution = (data["Marks"] / data["Max_Marks"]) * data["Weight"]
        else:
            contribution = 0.0
            
        co_scores[(student, co)] += contribution

    return co_scores


def convert_to_percentage(co_scores):
    """
    Converts raw weighted scores (typically 0.0-1.0) into percentages (0-100).
    
    Args:
        co_scores (dict): {(Student, CO): Score}
        
    Returns:
        dict: {(Student, CO): Percentage}
    """
    return {
        key: round(value * 100, 2)
        for key, value in co_scores.items()
    }


