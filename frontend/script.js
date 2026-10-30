async function loadDashboard() {
    const response = await fetch("/api/dashboard");
    const data = await response.json();

    document.getElementById("total-orders").innerText =
        data.total_orders.toLocaleString();

    document.getElementById("ship-as-is").innerText =
        data.buckets.SHIP_AS_IS.toLocaleString();

    document.getElementById("confirm-first").innerText =
        data.buckets.CONFIRM_FIRST.toLocaleString();

    document.getElementById("prepaid-only").innerText =
        data.buckets.PREPAID_ONLY.toLocaleString();

    document.getElementById("cancel").innerText =
        data.buckets.CANCEL.toLocaleString();

    document.getElementById("estimated-cost").innerText =
        "₹" + data.estimated_rto_cost.toLocaleString();

    const tableBody = document.getElementById("orders-table-body");
    tableBody.innerHTML = "";

    data.recent_orders.forEach(order => {
        const row = document.createElement("tr");

        row.innerHTML = `
            <td>${order.order_id}</td>
            <td>${order.customer}</td>
            <td>${order.city}</td>
            <td>₹${order.order_value}</td>
            <td>${order.bucket}</td>
            <td>${order.score}</td>
        `;

        tableBody.appendChild(row);
    });
}

loadDashboard();