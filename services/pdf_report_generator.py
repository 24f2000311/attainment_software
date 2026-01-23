from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors


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


def generate_pdf_report(co_df, po_df, cqi_df, output_path):
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

    # Title
    elements.append(Paragraph(
        "<b>NBA OBE Attainment Report</b>",
        styles["Title"]
    ))
    elements.append(Spacer(1, 20))

    # CO Attainment
    elements.append(Paragraph("<b>Course Outcome (CO) Attainment</b>", styles["Heading2"]))
    elements.append(Spacer(1, 10))
    elements.append(dataframe_to_table(co_df))
    elements.append(PageBreak())

    # PO Attainment
    elements.append(Paragraph("<b>Program Outcome (PO) Attainment</b>", styles["Heading2"]))
    elements.append(Spacer(1, 10))
    elements.append(dataframe_to_table(po_df))
    elements.append(PageBreak())

    # CQI Summary
    elements.append(Paragraph("<b>Continuous Quality Improvement (CQI) Summary</b>", styles["Heading2"]))
    elements.append(Spacer(1, 10))

    if not cqi_df.empty:
        elements.append(dataframe_to_table(cqi_df))
    else:
        elements.append(Paragraph("No CQI actions recorded.", styles["Normal"]))

    doc.build(elements)
