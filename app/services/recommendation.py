def generate_recommendations(member, rules):

    offers = [
        {"destination": "Hawaii", "type": "flight"},
        {"destination": "Paris", "type": "hotel"},
        {"destination": "Caribbean Cruise", "type": "cruise"},
        {"destination": "Tokyo", "type": "flight"},
    ]

    if rules["exclude_cruise"]:
        offers = [o for o in offers if o["type"] != "cruise"]

    history = {h["destination"] for h in member["travel_history"]}

    for o in offers:
        o["score"] = 2 if o["destination"] in history else 1

    ranked = sorted(offers, key=lambda x: x["score"], reverse=True)

    if rules["max_recommendations"]:
        ranked = ranked[:rules["max_recommendations"]]

    return ranked