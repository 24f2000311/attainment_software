from collections import defaultdict

def calculate_co_attainment(co_percentages, targets_df):
    results = {}

    # group by CO
    co_group = defaultdict(list)
    for (student, co), percent in co_percentages.items():
        co_group[co].append(percent)

    for co, percents in co_group.items():
        total_students = len(percents)

        for _, row in targets_df.sort_values("Level", ascending=False).iterrows():
            level = int(row["Level"])
            min_marks = row["Min_Marks_%"]
            min_students = row["Min_Students_%"]

            achieved = sum(p >= min_marks for p in percents)
            achieved_percent = (achieved / total_students) * 100

            if achieved_percent >= min_students:
                results[co] = {
                    "Attainment_Level": level,
                    "Achieved_%": round(achieved_percent, 2)
                }
                break
        else:
            results[co] = {
                "Attainment_Level": 0,
                "Achieved_%": round(achieved_percent, 2)
            }

    return results
