def calculate_po_attainment(co_attainment, co_po_df):
    po_results = {}

    # Extract PO columns (everything except CO_ID)
    po_columns = [col for col in co_po_df.columns if col != "CO_ID"]

    for po in po_columns:
        numerator = 0
        denominator = 0

        for _, row in co_po_df.iterrows():
            co = row["CO_ID"]
            strength = row[po]

            if strength == 0:
                continue

            co_level = co_attainment.get(co, {}).get("Attainment_Level", 0)

            numerator += co_level * strength
            denominator += strength

        po_value = round(numerator / denominator, 2) if denominator != 0 else 0

        po_results[po] = {
            "PO_Value": po_value,
            "PO_Level": round(po_value)
        }

    return po_results
