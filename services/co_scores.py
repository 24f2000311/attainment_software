from collections import defaultdict

def calculate_co_scores(normalized_data):
    co_scores = defaultdict(float)
    co_total_weight = defaultdict(float)

    # 1. Calculate Score & Track Total Weight per CO
    # We need to find the unique "Assessment-Question" weight for each CO to normalize properly.
    # A set of (Assessment, Question, CO) guarantees we simply sum the weights of all questions belonging to a CO.
    
    unique_questions = set()

    for row in normalized_data:
        student = row["Student_Name"]
        co = row["CO"]
        assessment = row["Assessment"]
        question = row["Question"]
        weight = row["Weight"]
        
        # Add to student score
        key = (student, co)
        score = (row["Marks"] / row["Max_Marks"]) * weight
        co_scores[key] += score

        # Track total weight for this CO (globally for the course)
        # We assume every student takes the same assessments. 
        # If specific students miss assessments, they get 0, which is correct (they lost that weight).
        # We just need to know "What was the total possible weight for CO1?"
        # We use a set to avoid double counting if multiple students have the same row data structure (which they do).
        
        uniq_key = (assessment, question, co)
        if uniq_key not in unique_questions:
            co_total_weight[co] += weight
            unique_questions.add(uniq_key)

    # 2. Normalize Scores
    # Final Score = (Sum of Weighted Scores) / (Total Weight Allocated to CO)
    
    final_scores = {}
    for (student, co), raw_score in co_scores.items():
        total_possible = co_total_weight.get(co, 1.0) # Avoid div by 0, though shouldn't happen if data exists
        if total_possible == 0:
            final_scores[(student, co)] = 0.0
        else:
            final_scores[(student, co)] = raw_score / total_possible

    return final_scores


def convert_to_percentage(co_scores):
    return {
        key: round(value * 100, 2)
        for key, value in co_scores.items()
    }


# 🆕 NEW FUNCTION: CO NUMERIC SCORES (0–3 SCALE)
def calculate_co_numeric_scores(co_percentage_scores):
    """
    Input:
        {
          ('Student A', 'CO1'): 72.5,
          ('Student B', 'CO1'): 64.0,
          ...
        }

    Output:
        {
          'CO1': 2.66,
          'CO2': 2.12
        }
    """

    co_points = defaultdict(list)

    for (student, co), percent in co_percentage_scores.items():

        if percent >= 60:
            point = 3
        elif percent >= 50:
            point = 2
        elif percent >= 40:
            point = 1
        else:
            point = 0

        co_points[co].append(point)

    # Average per CO
    return {
        co: round(sum(points) / len(points), 3)
        for co, points in co_points.items()
    }
