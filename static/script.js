let chartInstance = null;

function loadExpenses() {
    fetch("/get_expenses")
        .then(res => res.json())
        .then(data => {
            const tbody = document.querySelector("#expenseTable tbody");
            tbody.innerHTML = "";

            data.forEach(r => {
                const tr = document.createElement("tr");
                tr.innerHTML = `
                    <td>${r.id}</td>
                    <td>₹${Number(r.amount).toFixed(2)}</td>
                    <td>${r.category}</td>
                    <td>${r.date}</td>
                    <td>
                        <button class="delete-btn" onclick="deleteExpense(${r.id})">
                            Delete
                        </button>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        });
}

function addExpense() {
    const amount = document.getElementById("amount").value;
    const category = document.getElementById("category").value;

    if (!amount) {
        alert("Enter a valid amount");
        return;
    }

    fetch("/add_expense", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ amount, category })
    })
    .then(() => {
        document.getElementById("amount").value = "";
        loadExpenses();
        updateChart();
    });
}

function deleteExpense(id) {
    fetch("/delete_expense", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ id })
    })
    .then(() => {
        loadExpenses();
        updateChart();
    });
}


function updateChart() {
    fetch("/pie_data")
        .then(res => res.json())
        .then(data => {
            const labels = data.map(x => x.category);
            const values = data.map(x => x.total);

            const ctx = document.getElementById("chart").getContext("2d");

            if (chartInstance) chartInstance.destroy();

            chartInstance = new Chart(ctx, {
                type: "pie",
                data: {
                    labels,
                    datasets: [{ data: values }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { position: "bottom" } }
                }
            });
        });
}


loadExpenses();
updateChart();


setInterval(() => {
    loadExpenses();
    updateChart();
}, 5000);
