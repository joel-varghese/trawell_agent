import random

def get_member(member_id: str):
    return {
        "member_id": member_id,
        "loyalty_tier": random.choice(["Silver", "Gold", "Platinum"]),
        "partner_id": random.choice(["partner_a", "partner_b"]),
        "travel_history": [
            {"destination": "Hawaii", "type": "flight"},
            {"destination": "Paris", "type": "hotel"},
            {"destination": "Alaska Cruise", "type": "cruise"},
        ]
    }