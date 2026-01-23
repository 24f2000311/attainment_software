import pandas as pd

def normalize_marks(marks_sheets, question_map, weights):
    normalized = []

    for assessment, df in marks_sheets.items():

        # each sheet = one assessment
        for _, row in df.iterrows():
            student = row.get("Student_ID")

            if pd.isna(student):
                continue

            for question in df.columns:
                if question == "Student_ID":
                    continue

                q_map = question_map[
                    (question_map["Assessment"] == assessment) &
                    (question_map["Question"] == question)
                ]

                if q_map.empty:
                    continue

                normalized.append({
                    "Student_ID": student,
                    "Assessment": assessment,
                    "Question": question,
                    "CO": q_map.iloc[0]["CO_ID"],
                    "Marks": row[question],
                    "Max_Marks": q_map.iloc[0]["Max_Marks"],
                    "Weight": weights[assessment]
                })

    return normalized
