# app/log/audit.py
from datetime import datetime
from typing import List, Dict

# 메모리 기반 로그 저장 (필요 시 DB로 교체)
_logs: List[Dict] = []

def record(message: str, log_type: str = "info", details: dict = None):
    _logs.append({
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "type": log_type,  # info | decision | trade | error
        "message": message,
        "details": details or {}
    })
    # 로그 개수 제한 (최근 500개 유지)
    if len(_logs) > 500:
        del _logs[:100]

def get_recent(limit: int = 100) -> List[Dict]:
    if limit <= 0:
        limit = 1
    return _logs[-limit:]
