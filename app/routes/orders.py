from fastapi import APIRouter

router = APIRouter()

@router.post("/start")
async def start_trading():
    # TODO: 거래 시작 로직 연결
    return {"status": "started"}

@router.post("/stop")
async def stop_trading():
    # TODO: 거래 중지 로직 연결
    return {"status": "stopped"}

@router.post("/kill")
async def kill_switch():
    # TODO: 긴급 중지 로직 연결
    return {"status": "killed"}
