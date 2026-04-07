"""Recommendation Engine — applies partner rules to member travel profiles."""

DESTINATION_CATALOG = [
    {"destination": "Kyoto, Japan", "type": "cultural", "score": 95, "tags": ["asia", "culture", "temples"]},
    {"destination": "Amalfi Coast, Italy", "type": "beach", "score": 92, "tags": ["europe", "beach", "luxury"]},
    {"destination": "Patagonia, Argentina", "type": "adventure", "score": 90, "tags": ["south_america", "trekking"]},
    {"destination": "Maldives Overwater Villas", "type": "resort", "score": 94, "tags": ["asia", "luxury", "beach"]},
    {"destination": "Caribbean Cruise Package", "type": "cruise", "score": 88, "tags": ["caribbean", "cruise"]},
    {"destination": "Safari, Kenya", "type": "adventure", "score": 93, "tags": ["africa", "wildlife", "luxury"]},
    {"destination": "Swiss Alps, Switzerland", "type": "adventure", "score": 91, "tags": ["europe", "skiing", "luxury"]},
    {"destination": "Marrakech, Morocco", "type": "cultural", "score": 87, "tags": ["africa", "culture", "budget"]},
    {"destination": "Phuket, Thailand", "type": "beach", "score": 89, "tags": ["asia", "beach", "budget"]},
    {"destination": "New Zealand Road Trip", "type": "adventure", "score": 90, "tags": ["oceania", "adventure"]},
    {"destination": "Mediterranean Cruise", "type": "cruise", "score": 86, "tags": ["europe", "cruise", "cultural"]},
    {"destination": "Iceland Northern Lights", "type": "adventure", "score": 92, "tags": ["europe", "nature", "luxury"]},
    {"destination": "Bali Wellness Retreat", "type": "resort", "score": 88, "tags": ["asia", "wellness", "budget"]},
    {"destination": "New York City Weekend", "type": "city", "score": 84, "tags": ["north_america", "city", "cultural"]},
    {"destination": "Cape Town, South Africa", "type": "cultural", "score": 89, "tags": ["africa", "city", "adventure"]},
]

TIER_SCORE_BOOST = {"Platinum": 5, "Gold": 2, "Silver": 0}


def generate_recommendations(member: dict, rules: dict) -> list:
    """
    Generate personalized travel recommendations for a member, 
    enforcing partner-specific rules (caps, exclusions, preferred categories).
    """
    loyalty_tier = member.get("loyalty_tier", "Silver")
    past_destinations = {h["destination"] for h in member.get("travel_history", [])}
    excluded_types = set(rules.get("exclude_types", []))
    if not rules.get("allow_cruise_offers", True):
        excluded_types.add("cruise")

    preferred_categories = rules.get("preferred_categories", [])
    boost = TIER_SCORE_BOOST.get(loyalty_tier, 0)

    scored = []
    for dest in DESTINATION_CATALOG:
        if dest["destination"] in past_destinations:
            continue
        if dest["type"] in excluded_types:
            continue

        score = dest["score"] + boost
        if preferred_categories and dest["type"] in preferred_categories:
            score += 3

        scored.append({**dest, "score": score, "loyalty_tier_applied": loyalty_tier})

    scored.sort(key=lambda x: x["score"], reverse=True)

    max_recs = rules.get("max_recommendations")
    if max_recs is not None:
        scored = scored[:max_recs]

    return scored