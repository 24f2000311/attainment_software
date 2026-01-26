from flask import Blueprint, render_template
from services.state import state
from services.co_scores import calculate_co_scores, convert_to_percentage, calculate_co_numeric_scores
from services.co_attainment import calculate_co_attainment, calculate_weighted_co_attainment
from services.po_attainment import calculate_po_attainment

attainment_bp = Blueprint('attainment', __name__)

@attainment_bp.route("/co_attainment")
def co_attainment():
    if state.cleaned_normalized_data is None or state.config_sheets is None:
        return render_template(
            "error.html",
            error_message="Please upload and validate files first."
        )

    # Use shared service function
    final_results = calculate_weighted_co_attainment(state.cleaned_normalized_data, state.config_sheets)
    
    # Global numeric scores (kept on all data)
    co_scores = calculate_co_scores(state.cleaned_normalized_data)
    co_percentages = convert_to_percentage(co_scores) 
    co_numeric_scores = calculate_co_numeric_scores(co_percentages)

    return render_template(
        "co_attainment.html",
        co_attainment=final_results,
        co_numeric_scores=co_numeric_scores 
    )


@attainment_bp.route("/po-attainment")
def po_attainment_view():
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

    return render_template(
        "po_attainment.html",
        po_attainment=po_attainment_val
    )
