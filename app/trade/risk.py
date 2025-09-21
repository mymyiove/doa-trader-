LIMITS = {
    "max_exposure": 0.20,
    "max_per_symbol": 0.25,
    "stop_loss": -0.007,
    "daily_loss_limit": -0.015,
    "spread_cap": 0.003,
}

def filter_candidates(signals):
    return [s for s in signals if s["score"] > 0.8]

def force_one_share(raw):
    # 강제 1주 진입 로직
    return [{"symbol": "005930", "side": "buy", "qty": 1}]

def preflight(order):
    return True
