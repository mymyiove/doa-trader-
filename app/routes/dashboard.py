from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from datetime import datetime, time, timedelta
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

# === 최근 로그 조회 ===
@router.get("/logs")
async def get_logs(limit: int = 50):
    safe_limit = max(1, min(limit, 200))
    return audit.get_recent(safe_limit)

# === 시장 상태 & 계좌 잔고 ===
@router.get("/status")
async def get_status():
    tz = ZoneInfo(os.getenv("TIMEZONE", "Asia/Seoul"))
    now = datetime.now(tz)
    is_weekend = now.weekday() >= 5
    market_open = time(9, 0, 0)
    market_close = time(15, 30, 0)
    tnow = now.time()
    market_status = "장외" if is_weekend or (tnow < market_open) or (tnow >= market_close) else "장중"
    balance = await fetch_account_balance()
    return {
        "market_status": market_status,
        "server_time": now.isoformat(timespec="seconds"),
        "account_balance": balance
    }

async def fetch_account_balance():
    kis_base = os.getenv("KIS_API_URI_BASE")
    kis_app_key = os.getenv("KIS_APP_KEY")
    kis_app_secret = os.getenv("KIS_APP_SECRET")
    account = os.getenv("KIS_ACCOUNT_NUM")
    account_suffix = os.getenv("KIS_ACCOUNT_SUFFIX", "01")
    if not all([kis_base, kis_app_key, kis_app_secret, account]):
        return "₩ -"
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
            return data.get("output2", [{}])[0].get("tot_evlu_amt", "₩ -")
    except Exception as e:
        audit.record(f"계좌 잔고 조회 실패: {e}", "error")
        return "₩ -"

# === 가격 데이터 (차트용) ===
@router.get("/price")
async def get_price():
    kis_base = os.getenv("KIS_API_URI_BASE")
    kis_app_key = os.getenv("KIS_APP_KEY")
    kis_app_secret = os.getenv("KIS_APP_SECRET")
    symbol = os.getenv("CHART_SYMBOL", "005930")
    if not all([kis_base, kis_app_key, kis_app_secret, symbol]):
        return []
    try:
        headers = {
            "appkey": kis_app_key,
            "appsecret": kis_app_secret,
            "Content-Type": "application/json",
            "tr_id": "FHKST03010200"
        }
        params = {
            "FID_ETC_CLS_CODE": "",
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": symbol,
            "FID_INPUT_DATE_1": datetime.now().strftime("%Y%m%d"),
            "FID_INPUT_HOUR_1": "",
            "FID_PW_DATA_INCU_YN": "Y"
        }
        endpoint = f"{kis_base}/uapi/domestic-stock/v1/quotations/inquire-time-itemchartprice"
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(endpoint, headers=headers, params=params)
            r.raise_for_status()
            data = r.json()
            output = data.get("output2", [])
            prices = []
            for row in reversed(output[-10:]):
                prices.append({
                    "time": row.get("stck_cntg_hour", "")[:2] + ":" + row.get("stck_cntg_hour", "")[2:],
                    "price": int(row.get("stck_prpr", 0))
                })
            return prices
    except Exception as e:
        audit.record(f"가격 데이터 조회 실패: {e}", "error")
        return []

# === 보유 종목 현황 ===
@router.get("/holdings")
async def get_holdings():
    kis_base = os.getenv("KIS_API_URI_BASE")
    kis_app_key = os.getenv("KIS_APP_KEY")
    kis_app_secret = os.getenv("KIS_APP_SECRET")
    account = os.getenv("KIS_ACCOUNT_NUM")
    account_suffix = os.getenv("KIS_ACCOUNT_SUFFIX", "01")
    if not all([kis_base, kis_app_key, kis_app_secret, account]):
        return []
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
            output1 = data.get("output1", [])
            holdings = []
            for item in output1:
                holdings.append({
                    "symbol": item.get("pdno"),
                    "name": item.get("prdt_name"),
                    "qty": int(item.get("hldg_qty", 0)),
                    "avg_price": int(item.get("pchs_avg_pric", 0)),
                    "current_price": int(item.get("prpr", 0)),
                    "pnl": item.get("evlu_pfls_amt", "0")
                })
            return holdings
    except Exception as e:
        audit.record(f"보유 종목 조회 실패: {e}", "error")
        return []
