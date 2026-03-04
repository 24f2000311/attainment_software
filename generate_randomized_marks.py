import os
import pandas as pd
import numpy as np

def generate_randomized_marks():
    """
    Generates a randomized Marks_Randomized.xlsx file that ensures varied passing percentages 
    for students, so we can see the full range of CO attainment interpolation levels.
    """
    base_dir = r"c:\Users\madha\Desktop\attainment_software\Test_data\New_Architecture\Complex_Scenario"
    marks_file = os.path.join(base_dir, "Marks_Styled_Final.xlsx")
    output_file = os.path.join(base_dir, "Marks_Randomized_Interpolation.xlsx")
    
    # 1. Load the existing marks structure
    print(f"Loading existing structure from: {marks_file}")
    xls = pd.ExcelFile(marks_file)
    sheets = {sheet: xls.parse(sheet) for sheet in xls.sheet_names}
    
    print("Randomizing student marks to ensure fractional class achievement percentages...")
    
    # We assume students start at row 0 for pure data (no metadata headers if it's already stripped, but styled usually has it)
    # Check if 'Student_Name' is in columns.
    
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        for sheet_name, marks_df in sheets.items():
            print(f"Processing sheet: {sheet_name}")
            new_marks_df = marks_df.copy()
            
            # Find the starting row of actual student data. Usually, row 0 and 1 have max marks/weight, but let's check
            student_start_idx = 0
            if 'Student_001' not in str(marks_df.iloc[0].values):
                student_start_idx = 2 # Assuming 2 rows of headers for styled
                
            question_cols = [c for c in marks_df.columns if pd.notna(c) and c not in ["Student_ID", "Student_Name", "Student Name", "Roll No", "Roll Number"] and not "Unnamed" in str(c)]
            
            for col in question_cols:
                if len(marks_df) <= student_start_idx: continue
                
                # Max marks logic
                max_marks = marks_df[col].iloc[0] if student_start_idx > 0 else 10
                try: max_marks = float(max_marks)
                except: max_marks = 10.0
                
                target_pass_rate = np.random.uniform(0.35, 0.85) 
                pass_threshold = max_marks * 0.60
                
                for idx in range(student_start_idx, len(marks_df)):
                    # Ensure student exists here
                    if pd.isna(marks_df.at[idx, marks_df.columns[0]]):
                        continue
                        
                    if np.random.rand() < target_pass_rate:
                        score = np.random.uniform(pass_threshold, max_marks)
                    else:
                        score = np.random.uniform(0, pass_threshold - 0.1)
                        
                    new_marks_df.at[idx, col] = round(score)
            
            # Save sheet
            new_marks_df.to_excel(writer, sheet_name=sheet_name, index=False)
    print("Done generating test data.")

if __name__ == "__main__":
    generate_randomized_marks()
