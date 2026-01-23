def clean_row(row):
    return {
        "Student_Name": row["Student_Name"],
        "Assessment": row["Assessment"],
        "Question": row["Question"],
        "CO": row["CO"],
        "Marks": float(row["Marks"]),
        "Max_Marks": float(row["Max_Marks"]),
        "Weight": float(row["Weight"])
    }


