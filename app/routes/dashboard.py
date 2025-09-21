from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from datetime import datetime, time
from zoneinfo import ZoneInfo
from app.log import audit
import os
import httpx

router = APIRouter()

# === 정적 파일 서빙 ===
web_root = (Path(__file__).parent.parent.parent / "web").resolve()
static_dir = (web_root / "static").resolve()
router.mount("/static", StaticFiles(directory=static_dir), name="static")

# === 대시보드 HTML ===
@router.get("/", response_class=HTMLResponse)
async def dashboard_home(request: Request):
    html_path = (web_root / "index.html").resolve()
    if not html_path.exists():
        raise HTTPException(status_code=500, detail="index.html 파일이 없습니다.")
    return HTMLResponse(content=html_path.read_text(encoding="utf-8"))

# === 최근 로그 조회 API ===
@router.get("/logs")
async def get_logs(limit: int = 50):
    safe_limit = max(1, min(limit, 200))
    return audit.get_recent(safe_limit)

# === 시장 상태 & 계좌 잔고 API ===
@router.get("/status")
async def get_status():
    tz = ZoneInfo(os.getenv("TIMEZONE", "Asia/Seoul"))
    now = datetime.now(tz)

    # 장 상태 판별
    is_weekend = now.weekday() >= 5
    market_open = time(9, 0, 0)
    market_close = time(15, 30, 0)
    tnow = now.time()

    if is_weekend or (tnow < market_open) or (tnow >= market_close):
        market_status = "장외"
    else:
        market_status = "장중"

    # 계좌 잔고 조회
    balance = await fetch_account_balance()

    return {
        "market_status": market_status,
        "server_time": now.isoformat(timespec="seconds"),
        "account_balance": balance
    }

# === KIS API 계좌 잔고 조회 ===
async def fetch_account_balance():
    kis_base = os.getenv("KIS_API_URI_BASE")
    kis_app_key = os.getenv("KIS_APP_KEY")
    kis_app_secret = os.getenv("KIS_APP_SECRET")
    account = os.getenv("KIS_ACCOUNT_NUM")
    account_suffix = os.getenv("KIS_ACCOUNT_SUFFIX", "01")

    if not all([kis_base, kis_app_key, kis_app_secret, account]):
        # 필수 정보 없으면 기본값 반환
        return "₩ 100,000,000"

    try:
        headers = {
            "appkey": kis_app_key,
            "appsecret": kis_app_secret,
            "Content-Type": "application/json"
        }
        endpoint = f"{kis_base}/uapi/domestic-stock/v1/trading/inquire-balance"
        params = {
            "CANO": account,
            "ACNT_PRDT_CD": account_suffix,
            "AFHR_FLPR_YN": "N",
            "OFL_YN": "",
            "INQR_DVSN": "02",
            "UNPR_DVSN": "01",
            "FUND_STTL_ICLD_YN": "N",
            "FNCG_AMT_AUTO_RDPT_YN": "N",
            "PRCS_DVSN": "00",
            "CTX_AREA_FK100": "",
            "CTX_AREA_NK100": ""
        }
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(endpoint, headers=headers, params=params)
            r.raise_for_status()
            data = r.json()
            # KIS 응답 구조에 맞춰 파싱
            return data.get("output2", [{}])[0].get("tot_evlu_amt", "₩ -")
    except Exception as e:
        audit.record(f"계좌 잔고 조회 실패: {e}", "error")
        return "₩ -"
