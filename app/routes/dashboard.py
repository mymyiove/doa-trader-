from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def dashboard_home():
    return {"message": "DOA Trader Dashboard is running"}
