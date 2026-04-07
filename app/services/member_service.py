"""Mock Member Data Service"""

MOCK_MEMBERS = {
    "123": {
        "member_id": "123",
        "name": "Alexandra Chen",
        "loyalty_tier": "Gold",
        "partner_id": "partner_alpha",
        "travel_history": [
            {"destination": "Tokyo, Japan", "dates": "2024-11-10 to 2024-11-20", "booking_type": "flight+hotel"},
            {"destination": "Paris, France", "dates": "2024-08-01 to 2024-08-08", "booking_type": "flight+hotel"},
            {"destination": "Maldives", "dates": "2024-03-15 to 2024-03-22", "booking_type": "resort"},
            {"destination": "New York, USA", "dates": "2023-12-28 to 2024-01-02", "booking_type": "hotel"},
            {"destination": "Dubai, UAE", "dates": "2023-09-05 to 2023-09-12", "booking_type": "flight+hotel"},
        ],
    },
    "456": {
        "member_id": "456",
        "name": "Marcus Rivera",
        "loyalty_tier": "Platinum",
        "partner_id": "partner_beta",
        "travel_history": [
            {"destination": "Caribbean Cruise", "dates": "2025-01-05 to 2025-01-15", "booking_type": "cruise"},
            {"destination": "Barcelona, Spain", "dates": "2024-06-10 to 2024-06-18", "booking_type": "flight+hotel"},
            {"destination": "Santorini, Greece", "dates": "2024-04-20 to 2024-04-27", "booking_type": "flight+hotel"},
            {"destination": "Bali, Indonesia", "dates": "2023-10-01 to 2023-10-10", "booking_type": "resort"},
            {"destination": "Sydney, Australia", "dates": "2023-07-14 to 2023-07-22", "booking_type": "flight+hotel"},
        ],
    },
    "789": {
        "member_id": "789",
        "name": "Priya Patel",
        "loyalty_tier": "Silver",
        "partner_id": "partner_gamma",
        "travel_history": [
            {"destination": "London, UK", "dates": "2024-12-20 to 2024-12-27", "booking_type": "flight+hotel"},
            {"destination": "Amsterdam, Netherlands", "dates": "2024-09-03 to 2024-09-08", "booking_type": "hotel"},
            {"destination": "Rome, Italy", "dates": "2024-05-12 to 2024-05-19", "booking_type": "flight+hotel"},
            {"destination": "Prague, Czech Republic", "dates": "2023-11-18 to 2023-11-23", "booking_type": "hotel"},
            {"destination": "Lisbon, Portugal", "dates": "2023-06-25 to 2023-07-02", "booking_type": "flight+hotel"},
        ],
    },
}


def get_member(member_id: str) -> dict:
    """Retrieve member data by ID. Returns member profile including loyalty tier and travel history."""
    member_id = str(member_id).strip()
    if member_id in MOCK_MEMBERS:
        return MOCK_MEMBERS[member_id]
    return {
        "member_id": member_id,
        "name": "Unknown Member",
        "loyalty_tier": "Silver",
        "partner_id": "partner_alpha",
        "travel_history": [],
        "error": f"Member {member_id} not found. Using defaults."
    }