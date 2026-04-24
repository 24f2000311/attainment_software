# services/cqi_graphs.py

from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing, String
from reportlab.graphics.charts.barcharts import VerticalBarChart

def _build_bar_chart(labels, achieved, target, title, max_level=3):
    drawing = Drawing(450, 280)

    chart = VerticalBarChart()
    chart.x = 50
    chart.y = 50
    chart.height = 180
    chart.width = 350

    chart.data = [achieved, target]
    chart.categoryAxis.categoryNames = labels
    chart.categoryAxis.labels.fontSize = 8

    chart.valueAxis.valueMin = 0
    chart.valueAxis.valueMax = max_level
    chart.valueAxis.valueStep = 1

    chart.bars[0].fillColor = colors.darkblue
    chart.bars[1].fillColor = colors.lightgrey

    drawing.add(chart)

    drawing.add(String(
        225, 260, title,
        textAnchor="middle",
        fontSize=12
    ))

    return drawing


def build_co_cqi_graph(co_attainment, co_targets):
    labels = sorted(co_attainment.keys())
    achieved = [co_attainment[c]["Attainment_Level"] for c in labels]
    target = [float(co_targets.get(c, 2.0)) for c in labels]

    return _build_bar_chart(
        labels, achieved, target,
        "CO Attainment: Targeted vs Achieved"
    )


def build_po_cqi_graph(po_attainment, po_targets):
    labels = sorted(po_attainment.keys())
    achieved = [po_attainment[p]["PO_Level"] for p in labels]
    target = [float(po_targets.get(p, 2.0)) for p in labels]

    return _build_bar_chart(
        labels, achieved, target,
        "PO Attainment: Targeted vs Achieved"
    )
