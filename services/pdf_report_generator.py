from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors

from services.cqi_graphs import build_co_cqi_graph, build_po_cqi_graph


def dataframe_to_table(df):
    data = [list(df.columns)] + df.values.tolist()

    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONT", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
    ]))
    return table


def generate_pdf_report(
    co_df,
    po_df,
    cqi_df,
    co_attainment,
    po_attainment,
    output_path
):
    """
    Generates final NBA OBE PDF report

    co_df         -> CO attainment table (DataFrame)
    po_df         -> PO attainment table (DataFrame)
    cqi_df        -> CQI actions table (DataFrame)
    co_attainment -> dict output of calculate_co_attainment()
    po_attainment -> dict output of calculate_po_attainment()
    """

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )

    styles = getSampleStyleSheet()
    elements = []

    # ================= TITLE =================
    elements.append(Paragraph(
        "<b>NBA OBE Attainment Report</b>",
        styles["Title"]
    ))
    elements.append(Spacer(1, 20))

    # ================= CO ATTAINMENT =================
    elements.append(Paragraph(
        "<b>Course Outcome (CO) Attainment</b>",
        styles["Heading2"]
    ))
    elements.append(Spacer(1, 10))
    elements.append(dataframe_to_table(co_df))
    elements.append(PageBreak())

    # ================= PO ATTAINMENT =================
    elements.append(Paragraph(
        "<b>Program Outcome (PO) Attainment</b>",
        styles["Heading2"]
    ))
    elements.append(Spacer(1, 10))
    elements.append(dataframe_to_table(po_df))
    elements.append(PageBreak())

    # ================= CQI SUMMARY =================
    elements.append(Paragraph(
        "<b>Continuous Quality Improvement (CQI) Summary</b>",
        styles["Heading2"]
    ))
    elements.append(Spacer(1, 15))

    # ---- CQI GRAPHS (ReportLab) ----
    elements.append(build_co_cqi_graph(co_attainment, target_level=2))
    elements.append(Spacer(1, 20))

    elements.append(build_po_cqi_graph(po_attainment, target_level=2))
    elements.append(Spacer(1, 20))

    # ---- CQI TABLE ----
    if not cqi_df.empty:
        elements.append(dataframe_to_table(cqi_df))
    else:
        elements.append(
            Paragraph("No CQI actions recorded.", styles["Normal"])
        )

    # ================= BUILD PDF =================
    doc.build(elements)
