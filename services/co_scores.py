from collections import defaultdict

def calculate_co_scores(normalized_data):
    co_scores = defaultdict(float)

    for row in normalized_data:
        key = (row["Student_Name"], row["CO"])
        score = (row["Marks"] / row["Max_Marks"]) * row["Weight"]
        co_scores[key] += score

    return co_scores


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
