document.getElementById("startBtn").addEventListener("click", () => {
    fetch("/orders/start", { method: "POST" });
});
document.getElementById("stopBtn").addEventListener("click", () => {
    fetch("/orders/stop", { method: "POST" });
});
document.getElementById("killBtn").addEventListener("click", () => {
    fetch("/orders/kill", { method: "POST" });
});