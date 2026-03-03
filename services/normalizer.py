"""
Marks Normalization Service
===========================

This module transforms raw marks sheets into a standardized dictionary format.
It handles:
1. Mapping questions to Course Outcomes (COs).
2. Validating marks are numeric.
3. Looking up weights for each assessment-CO pair.
4. Structuring data for downstream processing.
"""

import pandas as pd


def normalize_marks(marks_sheets, question_map, co_weights):
    """
    Converts multiple assessment sheets into a single list of normalized records.
    
    Args:
        marks_sheets (dict): {SheetName: DataFrame} involving student marks.
        question_map (pd.DataFrame): Configuration mapping Questions -> COs.
        co_weights (dict): {(Assessment, CO): Weight} dictionary.
        
    Returns:
        list: A list of dictionaries, one per valid mark entry.
              [
                  {
                      "Student_Name": "John Doe",
                      "Assessment": "CCE1",
                      "Question": "Q1",
                      "CO": "CO1",
                      "Marks": 8.5,
                      "Max_Marks": 10,
                      "Weight": 0.3
                  },
                  ...
              ]
              
    Raises:
        ValueError: If weights are missing for an assessment-CO pair.
    """
    normalized = []

    for assessment, df in marks_sheets.items():
        # Iterate over each student row
        for _, row in df.iterrows():
            student = row.get("Student_Name")

            # Skip invalid student rows (e.g. empty lines)
            if pd.isna(student):
                continue

            # Iterate over each question column
            for question in df.columns:
                if question == "Student_Name":
                    continue

                # Skip empty marks (absent students)
                marks = row.get(question)
                if pd.isna(marks):
                    continue

                # CO mapping lookup: Find which CO this Question belongs to
                q_map = question_map[
                    (question_map["Assessment"] == assessment) &
                    (question_map["Question"] == question)
                ]

                if q_map.empty:
                    # Question not mapped in config, skip it
                    continue

                # Ensure marks are numeric
                try:
                    # Parse as float first to handle "8.0", then round to nearest int
                    marks = int(round(float(marks)))
                except (ValueError, TypeError):
                     # Log warning or skip? For strictness, let's raise error or set to 0.
                     # Setting to 0 is safer for "Ab" (Absent) but "Ab" usually is NaN or string.
                     # Let's skip non-numeric to be safe unless it's a critical error.
                     continue

                co_id = q_map.iloc[0]["CO_ID"]
                
                # Check for CO-wise weight configuration
                if (assessment, co_id) not in co_weights:
                    raise ValueError(
                        f"Missing weight for Assessment '{assessment}' -> CO '{co_id}' in CO_Weightage sheet."
                    )

                normalized.append({
                    "Student_Name": student,
                    "Assessment": assessment,
                    "Question": question,
                    "CO": co_id,    
                    "Marks": marks,
                    "Max_Marks": q_map.iloc[0]["Max_Marks"],
                    "Weight": co_weights[(assessment, co_id)]
                })

    return normalized
