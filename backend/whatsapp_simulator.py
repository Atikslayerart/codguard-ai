from financial_calculator import (
    calculate_prepaid_discount,
    calculate_nudge_impact
)


def send_confirmation_message(order):
    customer_name = order.get("customer_name", "Customer")
    order_id = order.get("order_id", "your order")

    message = (
        f"Hi {customer_name},\n\n"
        f"Your COD order {order_id} is ready to ship.\n\n"
        "Please reply YES to confirm your order, "
        "or NO to cancel it.\n\n"
        "If we do not receive a reply within 24 hours, "
        "your order will be placed on hold."
    )

    return message


def send_prepaid_nudge(order):
    customer_name = order.get("customer_name", "Customer")
    order_id = order.get("order_id", "your order")
    order_value = float(order.get("order_value", 0))

    discount = calculate_prepaid_discount(order_value)
    final_amount = order_value - discount

    message = (
        f"Hi {customer_name},\n\n"
        f"Your COD order {order_id} is eligible for a "
        f"3% prepaid discount.\n\n"
        f"Pay online now and get ₹{discount:.2f} off.\n"
        f"New amount to pay: ₹{final_amount:.2f}\n\n"
        "Reply PAY to switch to prepaid.\n"
        "Reply COD to continue with Cash on Delivery."
    )

    return message


def handle_customer_reply(reply, action):
    reply = reply.strip().lower()

    if action == "CONFIRM_ON_WHATSAPP":
        if reply in ["yes", "y", "haan", "ha", "ok"]:
            return {
                "status": "CONFIRMED",
                "next_action": "SHIP_AS_IS",
                "message": "Thank you! Your COD order has been confirmed and will be shipped."
            }

        if reply in ["no", "n", "nahi", "cancel"]:
            return {
                "status": "CANCELLED",
                "next_action": "CANCEL_ORDER",
                "message": "Your order has been cancelled as requested."
            }

        return {
            "status": "NEEDS_CLARIFICATION",
            "next_action": "ASK_AGAIN",
            "message": "Please reply YES to confirm your order or NO to cancel it."
        }

    if action == "NUDGE_PREPAID":
        if reply in ["pay", "prepaid", "online", "yes"]:
            return {
                "status": "PREPAID_SELECTED",
                "next_action": "SEND_PAYMENT_LINK",
                "message": "Great! Please complete your prepaid payment using the secure payment link."
            }

        if reply in ["cod", "cash on delivery", "no"]:
            return {
                "status": "COD_CONFIRMED",
                "next_action": "SHIP_AS_IS",
                "message": "Your COD order has been confirmed and will be shipped."
            }

        return {
            "status": "NEEDS_CLARIFICATION",
            "next_action": "ASK_AGAIN",
            "message": "Please reply PAY to choose prepaid or COD to continue with Cash on Delivery."
        }

    return {
        "status": "INVALID_ACTION",
        "next_action": "REVIEW_ORDER",
        "message": "Unable to process this order action."
    }


if __name__ == "__main__":
    sample_order = {
        "order_id": "KT100193",
        "customer_name": "Lakshmi Shaikh",
        "order_value": 649
    }

    print("=== CONFIRMATION FLOW ===")
    print(send_confirmation_message(sample_order))

    print("\nCustomer replies: YES")
    print(handle_customer_reply("YES", "CONFIRM_ON_WHATSAPP"))

    print("\n=== PREPAID NUDGE FLOW ===")
    print(send_prepaid_nudge(sample_order))

    print("\nCustomer replies: PAY")
    print(handle_customer_reply("PAY", "NUDGE_PREPAID"))

    print("\nCustomer replies: random text")
    print(handle_customer_reply("maybe later", "CONFIRM_ON_WHATSAPP"))