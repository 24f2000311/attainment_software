"""
CQI Routes
==========

This Blueprint handles Continuous Quality Improvement (CQI) features.

Routes:
- /cqi: Gap Identification (COs below target level).
- /cqi-action: Entry form for remedial actions.
- /cqi_summary: Dashboard showing improvements and action plans.
"""

from flask import Blueprint, render_template, request
from time import time

from services.state import state, resource_path
from services.co_attainment import calculate_weighted_co_attainment
from services.po_attainment import calculate_po_attainment
from services.cqi_gap import identify_co_gaps
from services.cqi_web_charts import save_co_cqi_chart, save_po_cqi_chart


cqi_bp = Blueprint("cqi", __name__)


# =========================
# CQI GAP IDENTIFICATION
# =========================
@cqi_bp.route("/cqi")
def cqi():
    if state.cleaned_normalized_data is None or state.config_sheets is None:
        return render_template(
            "error.html",
            error_message="Please upload and process files first."
        )

    # Use weighted attainment logic
    weighted_results = calculate_weighted_co_attainment(
        state.cleaned_normalized_data,
        state.config_sheets
    )
    
    # Flatten to get just the Final attainment for gap analysis
    final_co_attainment = {
       co: val["Final"] for co, val in weighted_results.items()
    }

    weak_cos = identify_co_gaps(final_co_attainment, target_level=2)

    return render_template(
        "cqi.html",
        weak_cos=weak_cos
    )


# =========================
# CQI ACTION ENTRY
# =========================
@cqi_bp.route("/cqi-action", methods=["GET", "POST"])
def cqi_action_view():
    if state.cleaned_normalized_data is None or state.config_sheets is None:
        return render_template(
            "error.html",
            error_message="Please upload and process files first."
        )

    if request.method == "POST":
        state.cqi_actions.append({
            "CO": request.form.get("co"),
            "Cause": request.form.get("cause"),
            "Action": request.form.get("action"),
            "Outcome": request.form.get("outcome")
        })

        return render_template(
            "cqi_success.html",
            message="CQI Action Plan saved successfully."
        )

    # Use weighted attainment logic
    weighted_results = calculate_weighted_co_attainment(
        state.cleaned_normalized_data,
        state.config_sheets
    )
    
    final_co_attainment = {
       co: val["Final"] for co, val in weighted_results.items()
    }

    weak_cos = identify_co_gaps(final_co_attainment, target_level=2)

    return render_template(
        "cqi_action.html",
        weak_cos=weak_cos
    )


# =========================
# CQI SUMMARY (GRAPHS)
# =========================
@cqi_bp.route("/cqi_summary")
def cqi_summary():

    if state.cleaned_normalized_data is None or state.config_sheets is None:
        return render_template(
            "error.html",
            error_message="Please upload and process files first."
        )

    # ---- CO ATTAINMENT (Weighted) ----
    weighted_results = calculate_weighted_co_attainment(
        state.cleaned_normalized_data,
        state.config_sheets
    )
    
    final_co_attainment = {
       co: val["Final"] for co, val in weighted_results.items()
    }

    # ---- PO ATTAINMENT ----
    po_attainment = calculate_po_attainment(
        final_co_attainment,
        state.config_sheets["CO_PO_Mapping"]
    )

    # ---- GENERATE WEB CHARTS (MATPLOTLIB) ----
    save_co_cqi_chart(final_co_attainment, 2, resource_path("static/cqi_co.png"))
    save_po_cqi_chart(po_attainment, 2, resource_path("static/cqi_po.png"))

    return render_template(
        "cqi_summary.html",
        cqi_actions=state.cqi_actions,
        timestamp=int(time())  # cache-busting
    )
