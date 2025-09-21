from fastapi import APIRouter
from app.trade import executor
from app.log import audit

router = APIRouter()

@router.post("/start")
async def start_trading():
    audit.record("거래 시작 명령 수신", "info")
    executor.start()
    return {"status": "started"}

@router.post("/stop")
async def stop_trading():
    audit.record("거래 종료 명령 수신", "info")
    executor.stop()
    return {"status": "stopped"}

@router.post("/kill")
async def kill_switch():
    audit.record("긴급 중지 명령 수신", "error")
    executor.kill()
    return {"status": "killed"}
