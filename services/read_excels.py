import pandas as pd

def read_excel_file(file_path):
    xls = pd.ExcelFile(file_path)
    sheets = {}

    for sheet_name in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet_name)

        if df.empty or df.dropna(how="all").empty:
            raise ValueError(
                f"Excel sheet '{sheet_name}' is empty. "
                "Please ensure all required sheets contain data."
            )

        sheets[sheet_name] = df

    return sheets
