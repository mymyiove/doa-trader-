from datetime import datetime
from typing import List, Dict

# 메모리 기반 로그 저장 (필요하면 DB로 교체 가능)
_logs: List[Dict] = []

def record(message: str, log_type: str = "info", details: dict = None):
    _logs.append({
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "type": log_type,  # info, decision, trade, error
        "message": message,
        "details": details or {}
    })
    # 로그 개수 제한 (최근 200개만 유지)
    if len(_logs) > 200:
        _logs.pop(0)

def get_recent(limit: int = 50) -> List[Dict]:
    return _logs[-limit:]
