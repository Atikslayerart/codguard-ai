from risk_rules import calculate_risk

safe_order = {
    "customer_prior_rto": 0,
    "customer_prior_orders": 2,
    "order_value": 649,
    "address_quality": "GOOD",
    "suspicious_name": False,
    "invalid_phone": False,
    "city": "Mumbai"
}

risky_order = {
    "customer_prior_rto": 2,
    "customer_prior_orders": 0,
    "order_value": 2499,
    "address_quality": "INVALID",
    "suspicious_name": True,
    "invalid_phone": True,
    "city": "Gorakhpur"
}

medium_order = {
    "customer_prior_rto": 1,
    "customer_prior_orders": 0,
    "order_value": 899,
    "address_quality": "WEAK",
    "suspicious_name": False,
    "invalid_phone": False,
    "city": "Delhi"
}

for order in [safe_order, medium_order, risky_order]:
    result = calculate_risk(order)
    print("\nRisk score:", result.risk_score)
    print("Risk level:", result.risk_level)
    print("Recommended action:", result.action)
    print("Reasons:")
    for reason in result.reasons:
        print("-", reason)