let priceChart;

// ===== 토스트 알림 =====
function showToast(type, message) {
    const container = document.getElementById("toastContainer");
    const toast = document.createElement("div");
    toast.className = `toast ${type}`;
    toast.textContent = message;
    container.appendChild(toast);
    setTimeout(() => {
        if (toast.parentNode) {
            container.removeChild(toast);
        }
    }, 3000);
}

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
            priceChart.data.datasets[0].data = data.map(p => p.price);
            priceChart.update();
        })
        .catch(err => console.error("가격 데이터 불러오기 실패", err));
}

// ===== 버튼 로딩 상태 =====
function setLoading(btn, isLoading) {
    if (isLoading) {
        btn.classList.add("loading");
    } else {
        btn.classList.remove("loading");
    }
}

// ===== 버튼 이벤트 =====
document.getElementById("startBtn").addEventListener("click", async () => {
    const btn = document.getElementById("startBtn");
    setLoading(btn, true);
    try {
        const res = await fetch("/orders/start", { method: "POST" });
        const data = await res.json();
        addLog({ timestamp: new Date().toLocaleTimeString(), type: "info", message: "거래 시작", details: data });
        showToast("success", "거래 루프 시작됨 ✅");
    } catch (err) {
        showToast("error", "거래 시작 실패 ❌");
    } finally {
        setLoading(btn, false);
    }
});

document.getElementById("stopBtn").addEventListener("click", async () => {
    const btn = document.getElementById("stopBtn");
    setLoading(btn, true);
    try {
        const res = await fetch("/orders/stop", { method: "POST" });
        const data = await res.json();
        addLog({ timestamp: new Date().toLocaleTimeString(), type: "info", message: "거래 종료", details: data });
        showToast("info", "거래 루프 종료됨 ⏹️");
    } catch (err) {
        showToast("error", "거래 종료 실패 ❌");
    } finally {
        setLoading(btn, false);
    }
});

document.getElementById("killBtn").addEventListener("click", async () => {
    const btn = document.getElementById("killBtn");
    setLoading(btn, true);
    try {
        const res = await fetch("/orders/kill", { method: "POST" });
        const data = await res.json();
        addLog({ timestamp: new Date().toLocaleTimeString(), type: "error", message: "긴급 중지", details: data });
        showToast("error", "긴급 중지 실행됨 💥");
    } catch (err) {
        showToast("error", "긴급 중지 실패 ❌");
    } finally {
        setLoading(btn, false);
    }
});

// ===== 현재 시간 표시 =====
function updateTime() {
    const now = new Date();
    document.getElementById("currentTime").textContent = now.toLocaleTimeString();
}
setInterval(updateTime, 1000);
updateTime();

// ===== 초기화 & 주기적 갱신 =====
initPriceChart();
fetchLogs();
fetchStatus();
fetchHoldings();
fetchPriceData();

setInterval(fetchLogs, 5000);
setInterval(fetchStatus, 10000);
setInterval(fetchHoldings, 15000);
setInterval(fetchPriceData, 10000);
