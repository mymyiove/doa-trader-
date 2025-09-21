function addLog(message) {
    const logContainer = document.getElementById("logContainer");
    const entry = document.createElement("div");
    entry.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
    logContainer.prepend(entry);
}

document.getElementById("startBtn").addEventListener("click", () => {
    fetch("/orders/start", { method: "POST" })
        .then(res => res.json())
        .then(data => addLog("거래 시작: " + JSON.stringify(data)))
        .catch(err => addLog("거래 시작 오류: " + err));
});

document.getElementById("stopBtn").addEventListener("click", () => {
    fetch("/orders/stop", { method: "POST" })
        .then(res => res.json())
        .then(data => addLog("거래 종료: " + JSON.stringify(data)))
        .catch(err => addLog("거래 종료 오류: " + err));
});

document.getElementById("killBtn").addEventListener("click", () => {
    fetch("/orders/kill", { method: "POST" })
        .then(res => res.json())
        .then(data => addLog("긴급 중지: " + JSON.stringify(data)))
        .catch(err => addLog("긴급 중지 오류: " + err));
});

// 서버에서 주기적으로 로그 가져오기 (예: 5초마다)
setInterval(() => {
    fetch("/ui/logs") // 나중에 서버에서 로그 API 구현
        .then(res => res.json())
        .then(logs => {
            logs.forEach(log => addLog(log));
        })
        .catch(() => {}); // 로그 API 없으면 무시
}, 5000);
