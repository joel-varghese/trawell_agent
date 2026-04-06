def get_partner_config(partner_id: str):
    configs = {
        "partner_a": {"max_recommendations": 3, "exclude_cruise": True},
        "partner_b": {"max_recommendations": None, "exclude_cruise": False},
    }
    return configs.get(partner_id, configs["partner_a"])