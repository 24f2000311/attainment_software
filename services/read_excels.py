import pandas as pd

def read_excel_file(file_path):
    xls = pd.ExcelFile(file_path)
    sheets = {}
    
    for sheet in xls.sheet_names:
        sheets[sheet] = pd.read_excel(xls, sheet_name=sheet)
        
    return sheets
