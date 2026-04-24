import pandas as pd

def generate_co_report(co_attainment, co_targets):
    rows = []

    for co, data in co_attainment.items():
        level = data["Attainment_Level"]
        target = float(co_targets.get(co, 2.0))
        status = (
            "Attained" if level >= target
            else "Marginal" if level >= (target / 2)
            else "Not Attained"
        )

        rows.append({
            "CO": co,
            "Attainment Level": level,
            "% Students Achieved": data["Achieved_%"],
            "Status": status
        })

    return pd.DataFrame(rows)


def generate_po_report(po_attainment, po_targets):
    rows = []

    for po, data in po_attainment.items():
        level = data["PO_Level"]
        target = float(po_targets.get(po, 2.0))
        status = (
            "Attained" if level >= target
            else "Marginal" if level >= (target / 2)
            else "Not Attained"
        )

        rows.append({
            "PO": po,
            "Computed Value": data["PO_Value"],
            "Attainment Level": level,
            "Status": status
        })

    return pd.DataFrame(rows)


def generate_cqi_report(cqi_actions):
    return pd.DataFrame(cqi_actions)
