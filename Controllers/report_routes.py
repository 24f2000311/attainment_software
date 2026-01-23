from flask import Blueprint, render_template, request, send_file
import os
import pandas as pd
from services.state import state, REPORTS_FOLDER
from services.co_scores import calculate_co_scores, convert_to_percentage
from services.co_attainment import calculate_co_attainment
from services.po_attainment import calculate_po_attainment
from services.report_generator import generate_co_report, generate_po_report, generate_cqi_report
from services.pdf_report_generator import generate_pdf_report

reports_bp = Blueprint('reports', __name__)

@reports_bp.route("/reports", methods=["GET", "POST"])
def reports_view():
    if state.cleaned_normalized_data is None or state.config_sheets is None:
        return render_template(
            "error.html",
            error_message="Please upload and process files first."
        )

    if request.method == "POST":
        report_type = request.form.get("report_type")

        # Recompute (stateless)
        co_scores = calculate_co_scores(state.cleaned_normalized_data)
        co_percentages = convert_to_percentage(co_scores)

        co_attainment = calculate_co_attainment(
            co_percentages,
            state.config_sheets["Attainment_Targets"]
        )

        po_attainment = calculate_po_attainment(
            co_attainment,
            state.config_sheets["CO_PO_Mapping"]
        )

        co_df = generate_co_report(co_attainment)
        po_df = generate_po_report(po_attainment)
        cqi_df = generate_cqi_report(state.cqi_actions)

        os.makedirs(REPORTS_FOLDER, exist_ok=True)
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
