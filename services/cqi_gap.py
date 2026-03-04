def identify_co_gaps(co_attainment, target_levels):
    weak_cos = []

    for co, data in co_attainment.items():
        target = float(target_levels.get(co, 2.0))
        if data["Attainment_Level"] < target:
            weak_cos.append({
                "CO": co,
                "Level": data["Attainment_Level"],
                "Achieved_%": data["Achieved_%"],
                "Target": target
            })

    return weak_cos
