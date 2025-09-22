# app/routes/orders.py
from fastapi import APIRouter
from app.trading import executor
from app.log import audit

router = APIRouter()

@router.post("/start")
async def start_trading():
    try:
        executor.start()
        audit.record("거래 루프 시작됨 (수동)", "info")
        return {"ok": True, "message": "거래 루프 시작"}
    except Exception as e:
        audit.record(f"거래 시작 실패: {e}", "error")
        return {"ok": False, "message": f"시작 실패: {e}"}

@router.post("/stop")
async def stop_trading():
    try:
        executor.stop()
        audit.record("거래 루프 중지됨 (수동)", "info")
        return {"ok": True, "message": "거래 루프 중지"}
    except Exception as e:
        audit.record(f"거래 중지 실패: {e}", "error")
        return {"ok": False, "message": f"중지 실패: {e}"}

@router.post("/kill")
async def kill_trading():
    try:
        executor.kill()
        audit.record("거래 루프 긴급중지됨 (수동)", "warning")
        return {"ok": True, "message": "긴급중지 완료"}
    except Exception as e:
        audit.record(f"긴급중지 실패: {e}", "error")
        return {"ok": False, "message": f"긴급중지 실패: {e}"}
