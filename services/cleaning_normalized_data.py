def clean_row(row):
    return {
        "Student_ID": int(row["Student_ID"]),
        "Assessment": row["Assessment"],
        "Question": row["Question"],
        "CO": row["CO"],
        "Marks": float(row["Marks"]),
        "Max_Marks": float(row["Max_Marks"]),
        "Weight": float(row["Weight"])
    }


