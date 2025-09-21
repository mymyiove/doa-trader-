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

function fetchLogs() {
    fetch("/ui/logs")
        .then(res => res.json())
        .then(logs => {
            document.getElementById("logContainer").innerHTML = "";
            logs.reverse().forEach(addLog);
        })
        .catch(err => console.error("로그 불러오기 실패", err));
}

document.getElementById("startBtn").addEventListener("click", () => {
    fetch("/orders/start", { method: "POST" })
        .then(res => res.json())
        .then(data => addLog({timestamp: new Date().toLocaleTimeString(), type: "info", message: "거래 시작", details: data}));
});

document.getElementById("stopBtn").addEventListener("click", () => {
    fetch("/orders/stop", { method: "POST" })
        .then(res => res.json())
        .then(data => addLog({timestamp: new Date().toLocaleTimeString(), type: "info", message: "거래 종료", details: data}));
});

document.getElementById("killBtn").addEventListener("click", () => {
    fetch("/orders/kill", { method: "POST" })
        .then(res => res.json())
        .then(data => addLog({timestamp: new Date().toLocaleTimeString(), type: "error", message: "긴급 중지", details: data}));
});

// 5초마다 로그 갱신
setInterval(fetchLogs, 5000);
fetchLogs();
