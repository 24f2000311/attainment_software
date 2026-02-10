"""
Report Generation Routes
========================

This Blueprint handles the generation and download of Attainment Reports (Excel/PDF).

Features:
- /reports: Renders the report selection UI.
- POST /reports: Generates the requested report type.
  - Re-calculates attainment to ensure freshness.
  - Tries to open a native OS "Save As" dialog using Tkinter (for local desktop experience).
  - Falls back to browser download if Tkinter fails (e.g., running on a headless server).
"""

from flask import Blueprint, render_template, request, send_file
import os
import pandas as pd
import tkinter as tk
from tkinter import filedialog

from services.state import state, REPORTS_FOLDER
from services.co_attainment import calculate_weighted_co_attainment
from services.po_attainment import calculate_po_attainment
from services.report_generator import (
    generate_co_report,
    generate_po_report,
    generate_cqi_report
)
from services.pdf_report_generator import generate_pdf_report


reports_bp = Blueprint("reports", __name__)


@reports_bp.route("/reports", methods=["GET", "POST"])
def reports_view():
    """
    Handles report generation requests.
    
    GET: Renders the report generation page.
    POST: Processes the form submission to generate Excel or PDF reports.
    
    Logic:
    1. Re-calculates Weighted CO Attainment & PO Attainment.
    2. Generates DataFrames for the report tables.
    3. Attempt 1: Open native system "Save As" dialog (Tkinter).
    4. Attempt 2: If native dialog fails, save to server 'reports/' folder and trigger browser download.
    """

    if state.cleaned_normalized_data is None or state.config_sheets is None:
        return render_template(
            "error.html",
            error_message="Please upload and process files first."
        )

    if request.method == "POST":
        report_type = request.form.get("report_type")

        # ---------- RECOMPUTE ATTAINMENT ----------
        # Use weighted attainment logic (Consolidated)
        weighted_results = calculate_weighted_co_attainment(
            state.cleaned_normalized_data,
            state.config_sheets
        )

        # Flatten to get just the Final attainment for reports/graphs
        # This matches the structure expected by generate_co_report and calculate_po_attainment
        co_attainment = {
           co: val["Final"] for co, val in weighted_results.items()
        }

        # PO Attainment
        po_attainment = calculate_po_attainment(
            co_attainment,
            state.config_sheets["CO_PO_Mapping"]
        )

        # ---------- DATAFRAMES ----------
        co_df = generate_co_report(co_attainment)
        po_df = generate_po_report(po_attainment)
        cqi_df = generate_cqi_report(state.cqi_actions)

        # ---------- SAVE DIALOG ----------
        save_path = None

        try:
            # Attempt to open a local GUI dialog for saving the file
            # This works if the app is running locally on the user's machine.
            root = tk.Tk()
            root.withdraw()
            root.attributes("-topmost", True)

            if report_type == "excel":
                save_path = filedialog.asksaveasfilename(
                    defaultextension=".xlsx",
                    filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                    title="Save Excel Report As",
                    initialfile="NBA_Attainment_Report.xlsx"
                )
            else:  # pdf
                save_path = filedialog.asksaveasfilename(
                    defaultextension=".pdf",
                    filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                    title="Save PDF Report As",
                    initialfile="NBA_Attainment_Report.pdf"
                )

            root.destroy()

        except Exception as e:
            # Tkinter might fail on headless servers or non-main threads
            print(f"Error invoking Tkinter dialog: {e}")
            save_path = None

        # ---------- SAVE (Local Path) ----------
        if save_path:
            if report_type == "excel":
                with pd.ExcelWriter(save_path, engine="openpyxl") as writer:
                    co_df.to_excel(writer, sheet_name="CO_Attainment", index=False)
                    po_df.to_excel(writer, sheet_name="PO_Attainment", index=False)
                    cqi_df.to_excel(writer, sheet_name="CQI_Summary", index=False)

            elif report_type == "pdf":
                generate_pdf_report(
                    co_df,
                    po_df,
                    cqi_df,
                    co_attainment,   
                    po_attainment,   
                    save_path        
                )

            return render_template(
                "cqi_success.html",
                message=f"Report saved successfully to: {save_path}"
            )

        # ---------- CANCELLED ----------
        if save_path == "":
            return render_template("reports.html")

        # ---------- FALLBACK (BROWSER DOWNLOAD) ----------
        # If Tkinter failed or was skipped, save to temp folder and send via HTTP
        os.makedirs(REPORTS_FOLDER, exist_ok=True)

        if report_type == "excel":
            path = os.path.join(REPORTS_FOLDER, "NBA_Attainment_Report.xlsx")
            with pd.ExcelWriter(path, engine="openpyxl") as writer:
                co_df.to_excel(writer, sheet_name="CO_Attainment", index=False)
            )

    return render_template("reports.html")
