import json
from pathlib import Path
from dataclasses import dataclass

CONFIG_PATH = Path(__file__).resolve().parents[1] / "config" / "rules.json"

with open(CONFIG_PATH, "r", encoding="utf-8") as file:
    RULES = json.load(file)


@dataclass
class RiskResult:
    risk_score: int
    risk_level: str
    action: str
    reasons: list


def calculate_risk(order):
    score = 0
    reasons = []

    prior_rto = int(order.get("customer_prior_rto", 0) or 0)
    prior_orders = int(order.get("customer_prior_orders", 0) or 0)
    order_value = float(order.get("order_value", 0) or 0)
    address_quality = str(order.get("address_quality", "MEDIUM")).upper()
    suspicious_name = bool(order.get("suspicious_name", False))
    invalid_phone = bool(order.get("invalid_phone", False))
    city = str(order.get("city", "")).strip().title()

    high_risk_cities = RULES["high_risk_cities"]

    if prior_rto >= 2:
        score += 40
        reasons.append("Customer has 2 or more previous RTOs.")
    elif prior_rto == 1:
        score += 15
        reasons.append("Customer has 1 previous RTO.")

    if address_quality == "INVALID":
        score += 35
        reasons.append("Address is invalid or incomplete.")
    elif address_quality == "MEDIUM":
        score += 15
        reasons.append("Address has limited delivery details.")
    elif address_quality == "WEAK":
        score += 10
        reasons.append("Address is unclear or depends only on landmarks.")

    if suspicious_name:
        score += 20
        reasons.append("Customer name looks suspicious or incomplete.")

    if invalid_phone:
        score += 15
        reasons.append("Phone number is invalid or incorrectly formatted.")

    if city in high_risk_cities:
        city_score = high_risk_cities[city]
        score += city_score
        reasons.append(f"{city} has a high historical RTO rate.")

    if order_value >= 2000:
        score += 15
        reasons.append("Order value is ₹2,000 or more.")
    elif order_value >= 1500:
        score += 10
        reasons.append("Order value is ₹1,500 or more.")

    if prior_orders >= 1 and prior_rto == 0:
        score -= 10
        reasons.append("Customer has previous successful orders and no RTO history.")

    score = max(0, min(100, score))

    thresholds = RULES["risk_thresholds"]

    if score >= thresholds["confirm_whatsapp"]:
        risk_level = "HIGH"
        action = "HOLD_REVIEW"
    elif score >= thresholds["nudge_prepaid"]:
        risk_level = "MEDIUM"
        action = "CONFIRM_ON_WHATSAPP"
    elif score >= thresholds["ship_as_is"]:
        risk_level = "LOW_MEDIUM"
        action = "NUDGE_PREPAID"
    else:
        risk_level = "LOW"
        action = "SHIP_AS_IS"

    if not reasons:
        reasons.append("No major risk signals found.")

    return RiskResult(
        risk_score=score,
        risk_level=risk_level,
        action=action,
        reasons=reasons
    )