import json
from pathlib import Path

CONFIG_PATH = Path(__file__).resolve().parents[1] / "config" / "rules.json"

with open(CONFIG_PATH, "r", encoding="utf-8") as file:
    RULES = json.load(file)


def calculate_rto_cost():
    financials = RULES["financials"]

    forward_shipping = financials["forward_shipping_cost"]
    return_shipping = financials["return_shipping_cost"]
    packaging = financials["packaging_handling_cost"]

    damaged_loss = (
        financials["damaged_return_rate"]
        * financials["average_product_cost"]
    )

    total_rto_cost = (
        forward_shipping
        + return_shipping
        + packaging
        + damaged_loss
    )

    return round(total_rto_cost, 2)


def calculate_expected_savings():
    financials = RULES["financials"]

    cod_rto_rate = financials["cod_rto_rate"]
    prepaid_rto_rate = financials["prepaid_rto_rate"]

    rto_cost = calculate_rto_cost()

    expected_savings = (cod_rto_rate - prepaid_rto_rate) * rto_cost

    return round(expected_savings, 2)


def calculate_prepaid_discount(order_value):
    discount_percent = RULES["business_rules"]["prepaid_discount_percent"]

    discount_amount = order_value * discount_percent / 100

    return round(discount_amount, 2)


def calculate_nudge_impact(order_value):
    expected_savings = calculate_expected_savings()
    discount_amount = calculate_prepaid_discount(order_value)

    net_benefit = expected_savings - discount_amount

    return {
        "order_value": order_value,
        "expected_rto_savings": expected_savings,
        "prepaid_discount": discount_amount,
        "net_expected_benefit": round(net_benefit, 2)
    }

def calculate_cancelled_order_loss(order_value, gross_margin=0.62):
    lost_margin = order_value * gross_margin

    return round(lost_margin, 2)


if __name__ == "__main__":
    print("Expected cost per RTO:")
    print("₹", calculate_rto_cost())

    print("\nExpected RTO savings if COD becomes prepaid:")
    print("₹", calculate_expected_savings())

    print("\nExample: ₹649 order")
    result = calculate_nudge_impact(649)
    print(result)