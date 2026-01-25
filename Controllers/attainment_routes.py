from flask import Blueprint, render_template
from services.state import state
from services.co_scores import calculate_co_scores, convert_to_percentage
from services.co_attainment import calculate_co_attainment
from services.po_attainment import calculate_po_attainment
from services.co_scores import calculate_co_numeric_scores

attainment_bp = Blueprint('attainment', __name__)

from services.co_attainment import calculate_achieved_percentage, determine_attainment_level

def process_attainment_subset_percentage(data, config_sheets):
    """
    Helper: Returns {CO: Achieved_%} for a subset of data
    """
    if not data:
        return {}
    scores = calculate_co_scores(data)
    percentages = convert_to_percentage(scores)
    return calculate_achieved_percentage(percentages, config_sheets["Attainment_Targets"])

def get_weighted_co_attainment():
    # 1. Get Settings (Global Weights)
    try:
        settings_df = state.config_sheets["Settings"]
        settings = dict(zip(settings_df["Property"], settings_df["Value"]))
        direct_weight = float(settings.get("Direct Weightage", 80)) / 100.0
        indirect_weight = float(settings.get("Indirect Weightage", 20)) / 100.0
        
        # Ensure they sum to 1.0 roughly (warn if not but proceed with normalization if needed? 
        # User said "Global Configuration... Direct=0.8". 
        # Let's assume input is 80/20 integer or 0.8/0.2. 
        # Usually settings like "80" mean 80%. Let's handle both.)
        if direct_weight > 1.0: direct_weight /= 100.0 # Correction if 8000? Unlikely.
        # If user put 80, we divided by 100 -> 0.8. Correct.
        
    except (KeyError, ValueError):
        direct_weight = 0.8
        indirect_weight = 0.2

    # 2. Get Assessment Modes
    assessment_df = state.config_sheets["Assessment_Weightage"]
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

    # 4. Calculate Achieved % for subsets (Metric Calculation Step)
    direct_achieved = process_attainment_subset_percentage(direct_data, state.config_sheets)
    indirect_achieved = process_attainment_subset_percentage(indirect_data, state.config_sheets)

    # 5. Merge and Calculate Final Attainment Level
    final_results = {}
    all_cos = set(direct_achieved.keys()) | set(indirect_achieved.keys())
    
    targets_df = state.config_sheets["Attainment_Targets"]

    for co in all_cos:
        d_im = direct_achieved.get(co, 0.0)
        i_im = indirect_achieved.get(co, 0.0)

        # Weighted Average of the "Achieved Percentage" (e.g. 60% of students passed Direct)
        final_achieved_percent = (d_im * direct_weight) + (i_im * indirect_weight)
        
        # Determine Level based on this weighted percentage
        final_level = determine_attainment_level(final_achieved_percent, targets_df)

        final_results[co] = {
            "Direct": {
                "Achieved_%": round(d_im, 2),
                # Optional: Look up level just for display? 
                "Attainment_Level": determine_attainment_level(d_im, targets_df)
            },
            "Indirect": {
                "Achieved_%": round(i_im, 2),
                "Attainment_Level": determine_attainment_level(i_im, targets_df)
            },
            "Final": {
                "Achieved_%": round(final_achieved_percent, 2),
                "Attainment_Level": final_level
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
