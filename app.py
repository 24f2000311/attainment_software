from flask import Flask, render_template, request,send_file
import os,sys
import pandas as pd
from services.read_excels import read_excel_file
from services.validator import (validate_config_sheets,validate_marks_basic)
from services.normalizer import normalize_marks
from services.cleaning_normalized_data import clean_row
from services.co_attainment import (calculate_co_attainment)
from services.co_scores import (calculate_co_scores,convert_to_percentage)
from services.po_attainment import calculate_po_attainment
from services.cqi_gap import identify_co_gaps
from services.report_generator import (
    generate_co_report,
    generate_po_report,
    generate_cqi_report
)
from services.pdf_report_generator import generate_pdf_report

app = Flask(__name__)


def get_runtime_dir():
    if getattr(sys, 'frozen', False):
        # Running as .exe
        return os.path.dirname(sys.executable)
    else:
        # Running normally
        return os.path.dirname(os.path.abspath(__file__))
    
BASE_DIR = get_runtime_dir() 
   
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
REPORTS_FOLDER = os.path.join(BASE_DIR, "reports")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REPORTS_FOLDER, exist_ok=True)

cleaned_normalized_data = None
config_sheets = None
cqi_actions = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    try:
    
        config_file = request.files['config']
        marks_file =  request.files['marks']
        
        config_path = os.path.join(UPLOAD_FOLDER, 'config.xlsx')
        marks_path = os.path.join(UPLOAD_FOLDER, 'marks.xlsx') 
        
        
        config_file.save(config_path)
        marks_file.save(marks_path)
        
        global config_sheets 
        config_sheets = read_excel_file(config_path)
        marks_sheets =read_excel_file(marks_path)
        
        validate_config_sheets(config_sheets)
        validate_marks_basic(marks_sheets)
        
        question_map = config_sheets["Question_CO_Map"]
        weights_df = config_sheets["Assessment_Weightage"]
        
        weights = dict(zip(
            weights_df["Assessment"],
            weights_df["Weight"]
        ))
        
        normalized_data =  normalize_marks(marks_sheets,question_map,weights)
        global cleaned_normalized_data 
        cleaned_normalized_data = [clean_row(r) for r in normalized_data]
        print(cleaned_normalized_data)
        
        return render_template('validate.html', messages=[ "Files uploaded successfully",
                    "Validation completed",
                    f"Normalized rows created: {len(cleaned_normalized_data)}"
                ])

    except ValueError as e:
        return render_template('error.html',error_message=str(e))


@app.route("/co_attainment")
def co_attainment():
    if cleaned_normalized_data is None or config_sheets is None:
        return render_template(
            "error.html",
            error_message="Please upload and validate files first."
        )

    co_scores = calculate_co_scores(cleaned_normalized_data)
    co_percentages = convert_to_percentage(co_scores)

    # 3️⃣ CO attainment
    co_attainment = calculate_co_attainment(
        co_percentages,
        config_sheets["Attainment_Targets"]
    )

    return render_template(
        "co_attainment.html",
        co_attainment=co_attainment
    )


@app.route("/po-attainment")
def po_attainment_view():
    global cleaned_normalized_data, config_sheets

    if cleaned_normalized_data is None or config_sheets is None:
        return render_template(
            "error.html",
            error_message="Please upload and process files first."
        )

    # Recompute CO attainment (safe & stateless)
    co_scores = calculate_co_scores(cleaned_normalized_data)
    co_percentages = convert_to_percentage(co_scores)
    co_attainment = calculate_co_attainment(
        co_percentages,
        config_sheets["Attainment_Targets"]
    )

    # PO attainment
    po_attainment = calculate_po_attainment(
        co_attainment,
        config_sheets["CO_PO_Mapping"]
    )

    return render_template(
        "po_attainment.html",
        po_attainment=po_attainment
    )


@app.route("/cqi")
def cqi():
    global cleaned_normalized_data, config_sheets

    if cleaned_normalized_data is None or config_sheets is None:
        return render_template(
            "error.html",
            error_message="Please upload and process files first."
        )

    # Recompute CO attainment
    co_scores = calculate_co_scores(cleaned_normalized_data)
    co_percentages = convert_to_percentage(co_scores)
    co_attainment = calculate_co_attainment(
        co_percentages,
        config_sheets["Attainment_Targets"]
    )

    # Identify gaps
    weak_cos = identify_co_gaps(co_attainment, target_level=2)

    return render_template(
        "cqi.html",
        weak_cos=weak_cos
    )
    
@app.route("/cqi-action", methods=["GET", "POST"])
def cqi_action_view():
    global cqi_actions, cleaned_normalized_data, config_sheets

    if cleaned_normalized_data is None or config_sheets is None:
        return render_template(
            "error.html",
            error_message="Please upload and process files first."
        )

    if request.method == "POST":
        co = request.form.get("co")
        cause = request.form.get("cause")
        action = request.form.get("action")
        outcome = request.form.get("outcome")

        cqi_actions.append({
            "CO": co,
            "Cause": cause,
            "Action": action,
            "Outcome": outcome
        })

        return render_template(
            "cqi_success.html",
            message="CQI Action Plan saved successfully."
        )

    # GET request → show weak COs
    co_scores = calculate_co_scores(cleaned_normalized_data)
    co_percentages = convert_to_percentage(co_scores)
    co_attainment = calculate_co_attainment(
        co_percentages,
        config_sheets["Attainment_Targets"]
    )

    weak_cos = identify_co_gaps(co_attainment, target_level=2)

    return render_template(
        "cqi_action.html",
        weak_cos=weak_cos
    )

@app.route("/cqi_summary")
def cqi_summary_view():
    global cqi_actions

    if not cqi_actions:
        return render_template(
            "error.html",
            error_message="No CQI actions recorded yet."
        )

    return render_template(
        "cqi_summary.html",
        cqi_actions=cqi_actions
    )
    
@app.route("/reports", methods=["GET", "POST"])
def reports_view():
    global cleaned_normalized_data, config_sheets, cqi_actions

    if cleaned_normalized_data is None or config_sheets is None:
        return render_template(
            "error.html",
            error_message="Please upload and process files first."
        )

    if request.method == "POST":
        report_type = request.form.get("report_type")

        # Recompute (stateless)
        co_scores = calculate_co_scores(cleaned_normalized_data)
        co_percentages = convert_to_percentage(co_scores)

        co_attainment = calculate_co_attainment(
            co_percentages,
            config_sheets["Attainment_Targets"]
        )

        po_attainment = calculate_po_attainment(
            co_attainment,
            config_sheets["CO_PO_Mapping"]
        )

        co_df = generate_co_report(co_attainment)
        po_df = generate_po_report(po_attainment)
        cqi_df = generate_cqi_report(cqi_actions)

        os.makedirs("reports", exist_ok=True)
        if report_type == "excel":
            path = os.path.join(REPORTS_FOLDER, "NBA_Attainment_Report.xlsx")
            with pd.ExcelWriter(path, engine="openpyxl") as writer:
                co_df.to_excel(writer, sheet_name="CO_Attainment", index=False)
                po_df.to_excel(writer, sheet_name="PO_Attainment", index=False)
                cqi_df.to_excel(writer, sheet_name="CQI_Summary", index=False)

            return send_file(
                        path,
                        as_attachment=True,
                        download_name=os.path.basename(path)
)

        elif report_type == "pdf":
            path = os.path.join(REPORTS_FOLDER, "NBA_Attainment_Report.pdf")
            generate_pdf_report(co_df, po_df, cqi_df, path)
            return send_file(
                            path,
                            as_attachment=True,
                            download_name=os.path.basename(path)
)

    return render_template("reports.html")


if __name__ == '__main__':
    app.run(debug=True)