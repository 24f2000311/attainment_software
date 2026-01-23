def identify_co_gaps(co_attainment, target_level=2):
    weak_cos = []

    for co, data in co_attainment.items():
        if data["Attainment_Level"] < target_level:
            weak_cos.append({
                "CO": co,
                "Level": data["Attainment_Level"],
                "Achieved_%": data["Achieved_%"]
            })

    return weak_cos
