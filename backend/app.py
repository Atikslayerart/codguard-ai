import math
import re
from pathlib import Path

import pandas as pd
from flask import Flask, jsonify, request

from financial_calculator import calculate_rto_cost
from risk_rules import calculate_risk


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = BASE_DIR / "data" / "cleaned_orders.csv"
FRONTEND_PATH = BASE_DIR / "frontend"

app = Flask(
    __name__,
    static_folder=str(FRONTEND_PATH),
    static_url_path=""
)

app.config["MAX_CONTENT_LENGTH"] = 64 * 1024

ACTIONS = (
    "SHIP_AS_IS",
    "CONFIRM_ON_WHATSAPP",
    "NUDGE_PREPAID",
    "HOLD_REVIEW",
)


def load_orders():
    """Read historical orders while preserving phone and pincode strings."""
    frame = pd.read_csv(
        DATA_PATH,
        dtype={
            "phone": "string",
            "phone_clean": "string",
            "pincode": "string",
            "pincode_clean": "string",
        },
    )

    required_columns = {
        "order_id",
        "order_datetime",
        "customer_name",
        "city",
        "order_value",
        "customer_prior_orders",
        "customer_prior_rto",
        "address_quality",
        "suspicious_name",
        "invalid_phone",
        "final_status",
    }

    missing = required_columns - set(frame.columns)

    if missing:
        raise ValueError(
            "Missing columns in cleaned_orders.csv: "
            + ", ".join(sorted(missing))
        )

    frame["final_status"] = (
        frame["final_status"].astype(str).str.strip().str.upper()
    )

    frame = frame[
        frame["final_status"].isin(["DELIVERED", "RTO"])
    ].copy()

    # Convert booleans explicitly: bool("False") would incorrectly be True.
    for column in ("suspicious_name", "invalid_phone"):
        frame[column] = frame[column].map(
            lambda value: str(value).strip().lower()
            in {"true", "1", "yes"}
        )

    for column in (
        "order_value",
        "customer_prior_orders",
        "customer_prior_rto",
    ):
        frame[column] = pd.to_numeric(frame[column], errors="coerce")

        if (
            frame[column].isna().any()
            or not frame[column].map(math.isfinite).all()
        ):
            raise ValueError(
                f"Column '{column}' contains missing or invalid numbers."
            )

    frame["is_rto"] = (frame["final_status"] == "RTO").astype(int)

    return frame


def text_value(value):
    return "" if pd.isna(value) else str(value)


def build_order_records(frame):
    sorted_frame = frame.sort_values(
        "order_datetime",
        ascending=False,
    )

    records = []

    for _, row in sorted_frame.iterrows():
        result = calculate_risk(row.to_dict())

        records.append({
            "order_id": text_value(row["order_id"]),
            "customer": text_value(row["customer_name"]),
            "city": text_value(row["city"]),
            "order_value": float(row["order_value"]),
            "prior_rto": int(row["customer_prior_rto"]),
            "address_quality": text_value(row["address_quality"]),
            "actual_status": text_value(row["final_status"]),
            "date": text_value(row["order_datetime"]),
            "risk_score": int(result.risk_score),
            "risk_level": result.risk_level,
            "action": result.action,
            "reasons": result.reasons,
        })

    return records


def required_text(data, field):
    value = data.get(field)

    if not isinstance(value, str) or not value.strip():
        raise ValueError(
            f"{field.replace('_', ' ').capitalize()} is required."
        )

    if len(value) > 1000:
        raise ValueError(f"{field} is too long.")

    return value.strip()


def numeric_value(data, field, integer=False, minimum=0):
    raw = data.get(field)

    if isinstance(raw, bool) or raw is None:
        raise ValueError(f"{field} must be a number.")

    try:
        value = float(raw)
    except (TypeError, ValueError):
        raise ValueError(f"{field} must be a number.")

    if not math.isfinite(value) or value < minimum:
        raise ValueError(
            f"{field} must be a finite number of at least {minimum}."
        )

    if integer and not value.is_integer():
        raise ValueError(f"{field} must be a whole number.")

    return int(value) if integer else value


def address_quality(address):
    """Local heuristic fallback, not an AI deliverability check."""
    normalized = address.strip().lower()

    if normalized in {
        "", "xyz", "home", "call me", "test", ".", "none", "nan"
    }:
        return "INVALID"

    strong_keywords = (
        "house no",
        "flat",
        "apartment",
        "society",
        "sector",
        "nagar",
        "road",
        "marg",
    )

    if any(keyword in normalized for keyword in strong_keywords):
        return "GOOD"

    landmark_keywords = (
        "ke paas",
        "ke peeche",
        "ke andar",
        "ke saamne",
        "ghar ka naam",
        "ph krke",
    )

    if any(keyword in normalized for keyword in landmark_keywords):
        return "WEAK"

    return "MEDIUM"


@app.get("/")
def home():
    return app.send_static_file("index.html")


@app.get("/favicon.ico")
def favicon():
    # No favicon file is required for this prototype.
    return "", 204


@app.get("/api/dashboard")
def dashboard():
    frame = load_orders()
    records = build_order_records(frame)

    decisions = {action: 0 for action in ACTIONS}

    for order in records:
        decisions[order["action"]] += 1

    total_orders = len(frame)
    rto_orders = int(frame["is_rto"].sum())

    return jsonify({
        "total_orders": total_orders,
        "delivered_orders": total_orders - rto_orders,
        "rto_orders": rto_orders,
        "overall_rto_rate": (
            round(rto_orders / total_orders * 100, 2)
            if total_orders else 0
        ),
        "decisions": decisions,
        "mode": "historical_replay",
        "score_type": "heuristic_points_not_probability",
        "financials": {
            "rto_cost": calculate_rto_cost(),
            "estimated_rto_savings": None,
            "estimated_lost_revenue": None,
            "net_impact": None,
            "status": "not_measured",
            "note": (
                "Intervention savings are not validated. "
                "Held orders are not assumed cancelled."
            ),
        },
    })


@app.get("/api/orders")
def historical_orders():
    frame = load_orders()
    return jsonify({"orders": build_order_records(frame)})


@app.post("/api/analyze-order")
def analyze_order():
    if not request.is_json:
        return jsonify({
            "error": "Send the order as JSON."
        }), 415

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "The request must contain a JSON object."
        }), 400

    try:
        name = required_text(data, "customer_name")
        phone = required_text(data, "phone")
        city = required_text(data, "city")
        address = required_text(data, "address")

        order_value = numeric_value(
            data, "order_value", minimum=0.01
        )

        prior_orders = numeric_value(
            data, "customer_prior_orders", integer=True
        )

        prior_rto = numeric_value(
            data, "customer_prior_rto", integer=True
        )

        if prior_rto > prior_orders:
            raise ValueError(
                "Previous RTOs cannot exceed previous orders."
            )

    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    digits = re.sub(r"[^0-9]", "", phone)

    if len(digits) == 12 and digits.startswith("91"):
        digits = digits[2:]

    valid_phone = bool(re.fullmatch(r"[6-9][0-9]{9}", digits))

    suspicious_names = {
        "test",
        "test order",
        "qwerty",
        "asdf",
        "xyz",
        "abc",
        "demo",
        "sample",
        "unknown",
    }

    order = {
        "customer_name": name,
        "phone": digits,
        "city": city,
        "address": address,
        "order_value": order_value,
        "customer_prior_orders": prior_orders,
        "customer_prior_rto": prior_rto,
        "address_quality": address_quality(address),
        "suspicious_name": name.lower() in suspicious_names,
        "invalid_phone": not valid_phone,
    }

    result = calculate_risk(order)

    return jsonify({
        "risk_score": int(result.risk_score),
        "risk_level": result.risk_level,
        "action": result.action,
        "reasons": result.reasons,
        "score_type": "heuristic_points_not_probability",
        "text_analysis_mode": "local_rules",
    })


@app.errorhandler(FileNotFoundError)
def missing_data_file(error):
    app.logger.error("Required file missing: %s", error)

    return jsonify({
        "error": (
            "Cannot find data/cleaned_orders.csv. "
            "Run python data_cleaning.py from the backend folder first."
        )
    }), 500


@app.errorhandler(ValueError)
def invalid_dataset(error):
    app.logger.error("Invalid data: %s", error)
    return jsonify({"error": str(error)}), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)