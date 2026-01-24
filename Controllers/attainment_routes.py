from flask import Blueprint, render_template
from services.state import state
from services.co_scores import calculate_co_scores, convert_to_percentage
from services.co_attainment import calculate_co_attainment
from services.po_attainment import calculate_po_attainment
from services.co_scores import calculate_co_numeric_scores

attainment_bp = Blueprint('attainment', __name__)

# Helper function to process data subset
def process_attainment_subset(data, config_sheets):
    if not data:
        return {}
    scores = calculate_co_scores(data)
    percentages = convert_to_percentage(scores)
    return calculate_co_attainment(percentages, config_sheets["Attainment_Targets"])

def get_weighted_co_attainment():
    # 1. Get Settings (Weights)
    try:
        settings_df = state.config_sheets["Settings"]
        settings = dict(zip(settings_df["Property"], settings_df["Value"]))
        direct_weight = float(settings.get("Direct Weightage", 80))
        indirect_weight = float(settings.get("Indirect Weightage", 20))
    except (KeyError, ValueError):
        direct_weight = 80.0
        indirect_weight = 20.0

    # 2. Get Assessment Modes
    assessment_df = state.config_sheets["Assessment_Weightage"]
    # If Mode missing, default to Direct (validation should catch this earlier but safety first)
    if "Mode" in assessment_df.columns:
        assessment_mode_map = dict(zip(assessment_df["Assessment"], assessment_df["Mode"]))
    else:
        assessment_mode_map = {}

    # 3. Split Data
    direct_data = []
    indirect_data = []

    for record in state.cleaned_normalized_data:
        mode = assessment_mode_map.get(record["Assessment"], "Direct") 
        if str(mode).strip().lower() == "indirect":
            indirect_data.append(record)
        else:
            direct_data.append(record)

    # 4. Calculate for subsets
    direct_results = process_attainment_subset(direct_data, state.config_sheets)
    indirect_results = process_attainment_subset(indirect_data, state.config_sheets)

    # 5. Merge and Calculate Final
    final_results = {}
    all_cos = set(direct_results.keys()) | set(indirect_results.keys())

    for co in all_cos:
        d_res = direct_results.get(co, {"Attainment_Level": 0, "Achieved_%": 0})
        i_res = indirect_results.get(co, {"Attainment_Level": 0, "Achieved_%": 0})

        d_level = d_res["Attainment_Level"]
        i_level = i_res["Attainment_Level"]

        final_level = (d_level * direct_weight + i_level * indirect_weight) / 100.0

        final_results[co] = {
            "Direct": d_res,
            "Indirect": i_res,
            "Final": {
                "Attainment_Level": round(final_level, 2),
            }
        }
    return final_results

@attainment_bp.route("/co_attainment")
def co_attainment():
    if state.cleaned_normalized_data is None or state.config_sheets is None:
        return render_template(
            "error.html",
            error_message="Please upload and validate files first."
        )

    final_results = get_weighted_co_attainment()
    
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
    final_results = get_weighted_co_attainment()

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
