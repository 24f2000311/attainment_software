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
    
    Formula:
        Score += (Marks_Obtained / Max_Marks) * Weightage
        
    Args:
        normalized_data (list): List of dictionaries containing:
                                - Student_Name
                                - CO
                                - Marks
                                - Max_Marks
                                - Weight
                                
    Returns:
        dict: A dictionary mapping (Student, CO) tuples to their aggregated weighted score (float).
              {(Student_Name, CO_ID): Score}
    """
    co_scores = defaultdict(float)

    for row in normalized_data:
        # Create a unique key for each student-CO pair
        key = (row["Student_Name"], row["CO"])
        
        # Calculate weighted contribution of this assessment question
        # If a question is worth 30% of the CO (Weight=0.3), and student gets 10/10,
        # they get 0.3 points added to their CO score.
        contribution = (row["Marks"] / row["Max_Marks"]) * row["Weight"]
        
        co_scores[key] += contribution

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


