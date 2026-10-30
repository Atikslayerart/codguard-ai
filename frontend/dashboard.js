"use strict";

const $ = id => document.getElementById(id);

const money = value => new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 2
}).format(value);

const actionNames = {
    SHIP_AS_IS: "Ship as-is",
    CONFIRM_ON_WHATSAPP: "WhatsApp confirmation",
    NUDGE_PREPAID: "Prepaid nudge",
    HOLD_REVIEW: "Hold / review"
};

let orders = [];
let currentPage = 1;
const pageSize = 20;
let chatState = "NOT_STARTED";
let activeFlow = "";


function showMessage(message) {
    $("app-message").textContent = message;
    $("app-message").hidden = !message;
}


async function api(url, options = {}) {
    const response = await fetch(url, {
        cache: "no-store",
        ...options
    });

    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
        throw new Error(data.error || `Request failed (${response.status})`);
    }

    return data;
}


function addRow(body, values) {
    const row = document.createElement("tr");

    values.forEach(value => {
        const cell = document.createElement("td");
        cell.textContent = String(value);
        row.appendChild(cell);
    });

    body.appendChild(row);
}


function setupNavigation() {
    document.querySelectorAll(".nav-link").forEach(link => {
        link.addEventListener("click", event => {
            event.preventDefault();

            const target = $(link.dataset.page);

            if (!target) return;

            document.querySelectorAll(".nav-link").forEach(item => {
                item.classList.toggle("active", item === link);
            });

            document.querySelectorAll(".page").forEach(page => {
                page.classList.toggle("active", page === target);
            });

            $("page-title").textContent = link.textContent;
        });
    });
}


async function loadData() {
    const button = $("refresh-button");
    button.disabled = true;
    showMessage("Loading historical orders…");

    try {
        const [dashboard, result] = await Promise.all([
            api("/api/dashboard"),
            api("/api/orders")
        ]);

        orders = result.orders;

        const ids = {
            SHIP_AS_IS: "ship-as-is",
            CONFIRM_ON_WHATSAPP: "confirm-whatsapp",
            NUDGE_PREPAID: "prepaid-nudges",
            HOLD_REVIEW: "hold-review"
        };

        $("total-orders").textContent =
            dashboard.total_orders.toLocaleString("en-IN");

        Object.entries(ids).forEach(([action, id]) => {
            $(id).textContent =
                dashboard.decisions[action].toLocaleString("en-IN");
        });

        $("delivered-count").textContent =
            dashboard.delivered_orders.toLocaleString("en-IN");

        $("returned-count").textContent =
            dashboard.rto_orders.toLocaleString("en-IN");

        $("historical-rate").textContent =
            `${dashboard.overall_rto_rate}%`;

        renderBars(dashboard.decisions, dashboard.total_orders);
        renderOrders();
        renderRisk();
        renderIllustrativeImpact(dashboard);

        showMessage("");
    } catch (error) {
        showMessage(`Could not load data: ${error.message}`);
        console.error(error);
    } finally {
        button.disabled = false;
    }
}


function renderIllustrativeImpact(dashboard) {
    const nudgeCount = dashboard.decisions.NUDGE_PREPAID;

    const assumedConversionRate = 0.5;
    const rtoCost = dashboard.financials.rto_cost;

    const demoOrderValue = 649;
    const discountRate = 0.03;
    const discountAmount = demoOrderValue * discountRate;

    const convertedOrders = nudgeCount * assumedConversionRate;

    const grossSavings = convertedOrders * rtoCost;
    const discountCost = convertedOrders * discountAmount;

    const illustrativeNetImpact = grossSavings - discountCost;

    $("illustrative-net-impact").textContent =
        money(illustrativeNetImpact);
}


function renderBars(decisions, total) {
    const container = $("decision-bars");
    container.replaceChildren();

    Object.entries(actionNames).forEach(([action, label]) => {
        const count = decisions[action];
        const percent = total ? count / total * 100 : 0;

        const wrapper = document.createElement("div");

        const heading = document.createElement("p");
        heading.textContent = `${label} — ${count} (${percent.toFixed(1)}%)`;

        const track = document.createElement("div");
        track.className = "bar-track";

        const fill = document.createElement("div");
        fill.className = `bar-fill ${action.toLowerCase()}`;
        fill.style.width = `${percent}%`;

        track.appendChild(fill);
        wrapper.append(heading, track);
        container.appendChild(wrapper);
    });
}


function filteredOrders() {
    const query = $("order-search").value.trim().toLowerCase();
    const action = $("action-filter").value;

    return orders.filter(order => {
        const text = `${order.order_id} ${order.customer} ${order.city}`
            .toLowerCase();

        return text.includes(query) && (!action || order.action === action);
    });
}


function renderOrders() {
    const filtered = filteredOrders();
    const totalPages = Math.max(1, Math.ceil(filtered.length / pageSize));

    currentPage = Math.min(currentPage, totalPages);

    const body = $("orders-table");
    body.replaceChildren();

    filtered
        .slice((currentPage - 1) * pageSize, currentPage * pageSize)
        .forEach(order => {
            addRow(body, [
                order.order_id,
                `${order.customer} / ${order.city}`,
                money(order.order_value),
                `${order.risk_score}/100`,
                actionNames[order.action],
                order.reasons.join(" ")
            ]);
        });

    if (!filtered.length) {
        addRow(body, ["No matching orders."]);
    }

    $("orders-count").textContent =
        `${filtered.length} matching orders`;

    $("page-number").textContent =
        `Page ${currentPage} of ${totalPages}`;

    $("previous-page").disabled = currentPage === 1;
    $("next-page").disabled = currentPage === totalPages;
}


function groupOutcomes(key) {
    const groups = new Map();

    orders.forEach(order => {
        const label = String(order[key]);
        const group = groups.get(label) || {
            label,
            count: 0,
            rto: 0
        };

        group.count += 1;
        group.rto += order.actual_status === "RTO" ? 1 : 0;

        groups.set(label, group);
    });

    return [...groups.values()].map(group => ({
        ...group,
        rate: group.rto / group.count * 100
    }));
}


function renderRisk() {
    const cityBody = $("city-table");
    cityBody.replaceChildren();

    groupOutcomes("city")
        .filter(group => group.count >= 30)
        .sort((a, b) => b.rate - a.rate)
        .slice(0, 10)
        .forEach(group => {
            addRow(cityBody, [
                group.label,
                group.count,
                `${group.rate.toFixed(1)}%`
            ]);
        });

    [
        ["address_quality", "address-table"],
        ["prior_rto", "history-table"]
    ].forEach(([key, tableId]) => {
        const body = $(tableId);
        body.replaceChildren();

        groupOutcomes(key)
            .sort((a, b) => a.label.localeCompare(
                b.label,
                undefined,
                { numeric: true }
            ))
            .forEach(group => {
                addRow(body, [
                    group.label,
                    group.count,
                    `${group.rate.toFixed(1)}%`
                ]);
            });
    });
}


async function analyzeOrder(event) {
    event.preventDefault();

    const button = $("analyze-button");
    const output = $("analysis-result");

    const payload = {
        customer_name: $("customer-name").value.trim(),
        phone: $("phone").value.trim(),
        city: $("city").value.trim(),
        address: $("address").value.trim(),
        order_value: Number($("order-value").value),
        customer_prior_orders: Number($("prior-orders").value),
        customer_prior_rto: Number($("prior-rto").value)
    };

    if (payload.customer_prior_rto > payload.customer_prior_orders) {
        showMessage("Previous RTOs cannot exceed previous orders.");
        return;
    }

    button.disabled = true;
    button.textContent = "Analyzing…";

    output.classList.remove("hidden");
    $("result-action").textContent = "";
    $("result-risk").textContent = "Checking order…";
    $("result-reasons").replaceChildren();

    try {
        const result = await api("/api/analyze-order", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        $("result-action").textContent =
            `Recommended action: ${actionNames[result.action] || result.action
            }`;

        $("result-risk").textContent =
            `Rule score: ${result.risk_score}/100 (${result.risk_level}) — not a probability`;

        result.reasons.forEach(reason => {
            const item = document.createElement("li");
            item.textContent = reason;
            $("result-reasons").appendChild(item);
        });

        showMessage("");
    } catch (error) {
        $("result-risk").textContent =
            `Could not analyze order: ${error.message}`;
    } finally {
        button.disabled = false;
        button.textContent = "Analyze Order →";
    }
}


function chatMessage(text, customer = false) {
    const bubble = document.createElement("p");
    bubble.className = customer ? "bubble customer" : "bubble";
    bubble.textContent = text;

    $("chat-messages").appendChild(bubble);
    bubble.scrollIntoView({ block: "nearest" });
}


function setChatState(state) {
    chatState = state;

    $("chat-state").textContent =
        `Demo status: ${state.replaceAll("_", " ")}`;

    $("payment-success").disabled =
        state !== "AWAITING_PAYMENT";
}


function startChat() {
    const value = Number($("chat-value").value);

    if (!Number.isFinite(value) || value <= 0) {
        showMessage("Enter a positive demo order value.");
        return;
    }

    showMessage("");
    activeFlow = $("chat-flow").value;

    $("chat-messages").replaceChildren();
    $("chat-reply").value = "";

    setChatState("AWAITING_REPLY");

    if (activeFlow === "CONFIRM_ON_WHATSAPP") {
        chatMessage(
            "Hi! Please confirm demo order DEMO-001. " +
            "Reply YES to confirm or NO to cancel. " +
            "Without a reply in 24 hours, we will hold it for review."
        );
    } else {
        const discount = Math.round(value * 0.03 * 100) / 100;

        chatMessage(
            `Hi! Get an illustrative 3% prepaid discount on DEMO-001: ` +
            `${money(discount)} off. Pay ${money(value - discount)}. ` +
            "Reply PAY for a mock payment link, COD to keep cash on delivery, " +
            "or CANCEL to cancel. No reply in 24 hours means hold for review."
        );
    }
}


function sendReply() {
    const reply = $("chat-reply").value.trim();

    if (!reply) return;

    if (!["AWAITING_REPLY", "AWAITING_PAYMENT"].includes(chatState)) {
        showMessage("Start a new demo before sending another reply.");
        return;
    }

    chatMessage(reply, true);
    $("chat-reply").value = "";

    const normalized = reply.toLowerCase();

    if (
        ["cancel", "nahi"].includes(normalized) ||
        (
            activeFlow === "CONFIRM_ON_WHATSAPP" &&
            ["no", "n"].includes(normalized)
        )
    ) {
        chatMessage(
            "Cancelled as requested. No shipment will be released in this demo."
        );

        setChatState("CANCELLED");
        return;
    }

    if (activeFlow === "CONFIRM_ON_WHATSAPP") {
        if (["yes", "y", "haan", "ha", "ok"].includes(normalized)) {
            chatMessage(
                "Order confirmed. Demo shipment is ready for release."
            );

            setChatState("COD_CONFIRMED");
        } else {
            chatMessage("Please reply YES to confirm or NO to cancel.");
        }

        return;
    }

    if (["pay", "prepaid", "online", "yes"].includes(normalized)) {
        chatMessage(
            "Mock payment link prepared. No real payment link is generated. " +
            "Use 'Simulate successful payment' to continue. " +
            "The order is not paid yet."
        );

        setChatState("AWAITING_PAYMENT");
    } else if (["cod", "no"].includes(normalized)) {
        chatMessage("COD preference confirmed for this demo.");
        setChatState("COD_CONFIRMED");
    } else {
        chatMessage("Please reply PAY, COD or CANCEL.");
    }
}


document.addEventListener("DOMContentLoaded", () => {
    setupNavigation();

    $("refresh-button").addEventListener("click", loadData);
    $("analyze-form").addEventListener("submit", analyzeOrder);

    ["order-search", "action-filter"].forEach(id => {
        $(id).addEventListener(
            id === "order-search" ? "input" : "change",
            () => {
                currentPage = 1;
                renderOrders();
            }
        );
    });

    $("previous-page").addEventListener("click", () => {
        currentPage -= 1;
        renderOrders();
    });

    $("next-page").addEventListener("click", () => {
        currentPage += 1;
        renderOrders();
    });

    $("start-chat").addEventListener("click", startChat);
    $("send-reply").addEventListener("click", sendReply);

    $("chat-reply").addEventListener("keydown", event => {
        if (event.key === "Enter") {
            sendReply();
        }
    });

    $("chat-timeout").addEventListener("click", () => {
        if (!["AWAITING_REPLY", "AWAITING_PAYMENT"].includes(chatState)) {
            return;
        }

        chatMessage(
            "24-hour deadline simulated. Order held for manual review, not cancelled."
        );

        setChatState("HOLD_REVIEW");
    });

    $("payment-success").addEventListener("click", () => {
        if (chatState !== "AWAITING_PAYMENT") return;

        chatMessage(
            "Mock payment success received. Demo order marked prepaid."
        );

        setChatState("PREPAID_CONFIRMED");
    });

    setChatState("NOT_STARTED");
    loadData();
});