def calculate_risk_score(order):
    score = 0
    reasons = []

    if order.get("previous_rto"):
        score += 25
        reasons.append("Previous RTO history")

    if order.get("address_quality") in ["weak", "invalid"]:
        score += 20
        reasons.append("Weak or invalid address")

    if order.get("high_risk_pincode"):
        score += 15
        reasons.append("High-risk pincode")

    if order.get("order_value", 0) > 1500:
        score += 10
        reasons.append("High-value order")

    if not order.get("valid_phone"):
        score += 5
        reasons.append("Suspicious phone number")

    return {
        "risk_score": score,
        "reasons": reasons
    }