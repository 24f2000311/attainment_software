"""
Attainment Routes
=================

This Blueprint handles the display of Attainment results.
Routes:
- /co_attainment: Displays CO Attainment levels and numeric scores.
- /po-attainment: Displays PO Attainment levels based on CO results.
"""

from flask import Blueprint, render_template
from services.state import state
from services.co_scores import calculate_co_scores, convert_to_percentage
from services.co_attainment import calculate_co_attainment, calculate_weighted_co_attainment
from services.po_attainment import calculate_po_attainment
import re

def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split('([0-9]+)', str(s))]

attainment_bp = Blueprint('attainment', __name__)

@attainment_bp.route("/co_attainment")
def co_attainment():
    """
    Renders the Course Outcome (CO) Attainment page.
    
    1. Checks if data is loaded.
    2. Calculates weighted CO attainment (Direct + Indirect).
    3. Derives Numeric Scores (0-3) from the Final Attainment Levels.
    4. Renders 'co_attainment.html'.
    """
    if state.cleaned_normalized_data is None or state.config_sheets is None:
        return render_template(
            "error.html",
            error_message="Please upload and validate files first."
        )

    # Use shared service function
    final_results = calculate_weighted_co_attainment(state.cleaned_normalized_data, state.config_sheets)
    
    # Sort final_results by CO keys naturally (CO1, CO2, CO10)
    final_results = dict(sorted(final_results.items(), key=lambda item: natural_sort_key(item[0])))
    
    co_list_df = state.config_sheets["CO_List"]
    co_targets = dict(zip(co_list_df["CO_ID"], co_list_df["Target"]))

    return render_template(
        "co_attainment.html",
        co_attainment=final_results,
        co_targets=co_targets
    )


@attainment_bp.route("/po-attainment")
def po_attainment_view():
    """
    Renders the Program Outcome (PO) Attainment page.
    
    1. Re-calculates CO attainment.
    2. Uses CO-PO mapping to compute PO values.
    3. Renders 'po_attainment.html'.
    """
    if state.cleaned_normalized_data is None or state.config_sheets is None:
        return render_template(
            "error.html",
            error_message="Please upload and process files first."
        )

    # Recompute CO attainment with weights
    final_results = calculate_weighted_co_attainment(state.cleaned_normalized_data, state.config_sheets)

    # Flatten for PO calculation: extract Final Attainment Level
    # mimic the expected structure {CO: {"Attainment_Level": X}}
    simplified_co_attainment = {
       co: val["Final"] for co, val in final_results.items()
    }

    # PO attainment
    po_attainment_val = calculate_po_attainment(
        simplified_co_attainment,
        state.config_sheets["CO_PO_Mapping"]
    )

    # Sort POs naturally
    po_attainment_val = dict(sorted(po_attainment_val.items(), key=lambda item: natural_sort_key(item[0])))

    po_list_df = state.config_sheets["PO_List"]
    po_targets = dict(zip(po_list_df["PO_ID"], po_list_df["Target"]))

    return render_template(
        "po_attainment.html",
        po_attainment=po_attainment_val,
        po_targets=po_targets
    )
