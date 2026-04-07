"""Mock Partner Configuration Service"""

PARTNER_CONFIGS = {
    "partner_alpha": {
        "partner_id": "partner_alpha",
        "partner_name": "Horizon Travel Group",
        "max_recommendations": 3,
        "exclude_types": [],
        "preferred_categories": ["luxury", "adventure"],
        "commission_tier": "standard",
        "allow_cruise_offers": True,
        "notes": "Caps recommendations at 3 per session. Full offer catalog available.",
    },
    "partner_beta": {
        "partner_id": "partner_beta",
        "partner_name": "Elite Voyages",
        "max_recommendations": None,  # Unlimited
        "exclude_types": ["cruise"],
        "preferred_categories": ["cultural", "beach", "city"],
        "commission_tier": "premium",
        "allow_cruise_offers": False,
        "notes": "Unlimited recommendations. Cruise offers are excluded per contract.",
    },
    "partner_gamma": {
        "partner_id": "partner_gamma",
        "partner_name": "BudgetWings",
        "max_recommendations": 5,
        "exclude_types": ["resort"],
        "preferred_categories": ["budget", "backpacker", "city"],
        "commission_tier": "economy",
        "allow_cruise_offers": True,
        "notes": "Caps at 5 recommendations. Resort-only packages excluded.",
    },
}


def get_partner_config(partner_id: str) -> dict:
    """Retrieve partner-specific rules and configuration for multi-tenant enforcement."""
    partner_id = str(partner_id).strip()
    if partner_id in PARTNER_CONFIGS:
        return PARTNER_CONFIGS[partner_id]
    return {
        "partner_id": partner_id,
        "partner_name": "Unknown Partner",
        "max_recommendations": 3,
        "exclude_types": [],
        "preferred_categories": [],
        "commission_tier": "standard",
        "allow_cruise_offers": True,
        "notes": "Default config applied — partner not found.",
        "error": f"Partner {partner_id} not found. Defaults applied."
    }