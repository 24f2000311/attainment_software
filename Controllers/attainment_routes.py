from flask import Blueprint, render_template
from services.state import state
from services.co_scores import calculate_co_scores, convert_to_percentage
from services.co_attainment import calculate_co_attainment
from services.po_attainment import calculate_po_attainment

attainment_bp = Blueprint('attainment', __name__)

@attainment_bp.route("/co_attainment")
def co_attainment():
    if state.cleaned_normalized_data is None or state.config_sheets is None:
        return render_template(
            "error.html",
            error_message="Please upload and validate files first."
        )

    co_scores = calculate_co_scores(state.cleaned_normalized_data)
    co_percentages = convert_to_percentage(co_scores)

    # 3️⃣ CO attainment
    co_attainment_val = calculate_co_attainment(
        co_percentages,
        state.config_sheets["Attainment_Targets"]
    )

    return render_template(
        "co_attainment.html",
        co_attainment=co_attainment_val
    )

@attainment_bp.route("/po-attainment")
def po_attainment_view():
    if state.cleaned_normalized_data is None or state.config_sheets is None:
        return render_template(
            "error.html",
            error_message="Please upload and process files first."
        )

    # Recompute CO attainment (safe & stateless)
    co_scores = calculate_co_scores(state.cleaned_normalized_data)
    co_percentages = convert_to_percentage(co_scores)
    co_attainment_val = calculate_co_attainment(
        co_percentages,
        state.config_sheets["Attainment_Targets"]
    )

    # PO attainment
    po_attainment_val = calculate_po_attainment(
        co_attainment_val,
        state.config_sheets["CO_PO_Mapping"]
    )

    return render_template(
        "po_attainment.html",
        po_attainment=po_attainment_val
    )
