from flask import Blueprint, render_template, request
from services.state import state
from services.co_scores import calculate_co_scores, convert_to_percentage
from services.co_attainment import calculate_co_attainment
from services.cqi_gap import identify_co_gaps

cqi_bp = Blueprint('cqi', __name__)

@cqi_bp.route("/cqi")
def cqi():
    if state.cleaned_normalized_data is None or state.config_sheets is None:
        return render_template(
            "error.html",
            error_message="Please upload and process files first."
        )

    # Recompute CO attainment
    co_scores = calculate_co_scores(state.cleaned_normalized_data)
    co_percentages = convert_to_percentage(co_scores)
    co_attainment = calculate_co_attainment(
        co_percentages,
        state.config_sheets["Attainment_Targets"]
    )

    # Identify gaps
    weak_cos = identify_co_gaps(co_attainment, target_level=2)

    return render_template(
        "cqi.html",
        weak_cos=weak_cos
    )
    
@cqi_bp.route("/cqi-action", methods=["GET", "POST"])
def cqi_action_view():
    if state.cleaned_normalized_data is None or state.config_sheets is None:
        return render_template(
            "error.html",
            error_message="Please upload and process files first."
        )

    if request.method == "POST":
        co = request.form.get("co")
        cause = request.form.get("cause")
        action = request.form.get("action")
        outcome = request.form.get("outcome")

        state.cqi_actions.append({
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
    co_scores = calculate_co_scores(state.cleaned_normalized_data)
    co_percentages = convert_to_percentage(co_scores)
    co_attainment = calculate_co_attainment(
        co_percentages,
        state.config_sheets["Attainment_Targets"]
    )

    weak_cos = identify_co_gaps(co_attainment, target_level=2)

    return render_template(
        "cqi_action.html",
        weak_cos=weak_cos
    )

@cqi_bp.route("/cqi_summary")
def cqi_summary_view():
    if not state.cqi_actions:
        return render_template(
            "error.html",
            error_message="No CQI actions recorded yet."
        )

    return render_template(
        "cqi_summary.html",
        cqi_actions=state.cqi_actions
    )
