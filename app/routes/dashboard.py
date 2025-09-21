from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def dashboard_home():
    return {
        "status": "ok",
        "message": "DOA Trader Dashboard is running",
        "note": "여기에 나중에 대시보드 HTML/JS를 연결할 예정"
    }
