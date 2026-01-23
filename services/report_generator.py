import pandas as pd

def generate_co_report(co_attainment):
    rows = []

    for co, data in co_attainment.items():
        level = data["Attainment_Level"]
        status = (
            "Attained" if level >= 2
            else "Marginal" if level == 1
            else "Not Attained"
        )

        rows.append({
            "CO": co,
            "Attainment Level": level,
            "% Students Achieved": data["Achieved_%"],
            "Status": status
        })

    return pd.DataFrame(rows)


def generate_po_report(po_attainment):
    rows = []

    for po, data in po_attainment.items():
        level = data["PO_Level"]
        status = (
            "Attained" if level >= 2
            else "Marginal" if level == 1
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
