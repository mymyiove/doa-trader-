function addLog(message) {
    const logContainer = document.getElementById("logContainer");
    const entry = document.createElement("div");
    entry.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
    logContainer.prepend(entry);
}

document.getElementById("startBtn").addEventListener("click", () => {
    fetch("/orders/start", { method: "POST" })
        .then(res => res.json())
        .then(data => addLog("거래 시작: " + JSON.stringify(data)));
});

document.getElementById("stopBtn").addEventListener("click", () => {
    fetch("/orders/stop", { method: "POST" })
        .then(res => res.json())
        .then(data => addLog("거래 종료: " + JSON.stringify(data)));
});

document.getElementById("killBtn").addEventListener("click", () => {
    fetch("/orders/kill", { method: "POST" })
        .then(res => res.json())
        .then(data =>
