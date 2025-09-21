let priceChart;

// ===== 로그 한 줄 추가 =====
function addLog(entry) {
    const logContainer = document.getElementById("logContainer");
    const div = document.createElement("div");
    div.className = `log-entry ${entry.type}`;
    div.innerHTML = `<strong>[${entry.timestamp}]</strong> ${entry.message}`;
    
    if (entry.details && Object.keys(entry.details).length > 0) {
        const details = document.createElement("pre");
        details.textContent = JSON.stringify(entry.details, null, 2);
        details.style.display = "none";
        div.appendChild(details);
        div.addEventListener("click", () => {
            details.style.display = details.style.display === "none" ? "block" : "none";
        });
    }
    logContainer.prepend(div);
}

// ===== 로그 가져오기 =====
function fetchLogs() {
    fetch("/ui/logs")
        .then(res => res.json())
        .then(logs => {
            document.getElementById("logContainer").innerHTML = "";
            logs.reverse().forEach(addLog);
        })
        .catch(err => console.error("로그 불러오기 실패", err));
}

// ===== 상태 가져오기 =====
function fetchStatus() {
    fetch("/ui/status")
        .then(res => res.json())
        .then(data => {
            document.getElementById("marketStatus").textContent = data.market_status;
            document.getElementById("accountBalance").textContent = data.account_balance;
        })
        .catch(err => console.error("상태 불러오기 실패", err));
}

// ===== 보유 종목 가져오기 =====
function fetchHoldings() {
    fetch("/ui/holdings")
        .then(res => res.json())
        .then(data => {
            const tbody = document.querySelector("#holdingsTable tbody");
            tbody.innerHTML = "";
            if (!data || data.length === 0) {
                tbody.innerHTML = `<tr><td colspan="6" style="text-align:center;">데이터 없음</td></tr>`;
                return;
            }
            data.forEach(item => {
                const tr = document.createElement("tr");
                tr.innerHTML = `
                    <td>${item.symbol}</td>
                    <td>${item.name}</td>
                    <td>${item.qty}</td>
                    <td>${item.avg_price}</td>
                    <td>${item.current_price}</td>
                    <td>${item.pnl}</td>
                `;
                tbody.appendChild(tr);
            });
        })
        .catch(err => console.error("보유 종목 불러오기 실패", err));
}

// ===== 가격 차트 초기화 =====
function initPriceChart() {
    const ctx = document.getElementById("priceChart").getContext("2d");
    priceChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: '가격',
                data: [],
                borderColor: '#00e676',
                backgroundColor: 'rgba(0, 230, 118, 0.1)',
                fill: true,
                tension: 0.2
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false } },
            scales: {
                x: { ticks: { color: '#e6edf3' } },
                y: { ticks: { color: '#e6edf3' } }
            }
        }
    });
}

// ===== 가격 데이터 갱신 =====
function fetchPriceData() {
    fetch("/ui/price")
        .then(res => res.json())
        .then(data => {
            if (!priceChart) return;
            priceChart.data.labels = data.map(p => p.time);
            priceChart.data.datasets[0].data = data.map(p =>
