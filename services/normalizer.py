import pandas as pd

def normalize_marks(marks_sheets, question_map, weights):
    normalized = []

    for assessment, df in marks_sheets.items():

        # 🚨 Assessment must have weight
        if assessment not in weights:
            raise ValueError(
                f"Weightage not defined for assessment: '{assessment}'"
            )

        for _, row in df.iterrows():
            student = row.get("Student_Name")

            # Skip invalid student rows
            if pd.isna(student):
                continue

            for question in df.columns:
                if question == "Student_Name":
                    continue

                # Skip empty marks
                marks = row.get(question)
                if pd.isna(marks):
                    continue

                # CO mapping lookup
                q_map = question_map[
                    (question_map["Assessment"] == assessment) &
                    (question_map["Question"] == question)
                ]

                if q_map.empty:
                    continue

                # Marks must be numeric
                # if not isinstance(marks, (int, float)):
                #     raise ValueError(
                #         f"Non-numeric marks found for student '{student}' "
                #         f"in assessment '{assessment}', question '{question}'"
                #     )

                normalized.append({
                    "Student_Name": student,
                    "Assessment": assessment,
                    "Question": question,
                    "CO": q_map.iloc[0]["CO_ID"],
                    "Marks": marks,
                    "Max_Marks": q_map.iloc[0]["Max_Marks"],
                    "Weight": weights[assessment]
                })

    return normalized
