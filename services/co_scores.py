from collections import defaultdict

def calculate_co_scores(normalized_data):
    co_scores = defaultdict(float)

    for row in normalized_data:
        key = (row["Student_ID"], row["CO"])

        score = (row["Marks"] / row["Max_Marks"]) * row["Weight"]
        co_scores[key] += score

    return co_scores

def convert_to_percentage(co_scores):
    return {
        key: round(value * 100, 2)
        for key, value in co_scores.items()
    }
