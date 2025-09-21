import os
import httpx
from app.log import audit

_running = False

def start():
    global _running
    if _running:
        audit.record("거래 시작 요청 무시: 이미 실행 중", "info")
        return
    _running = True
    audit.record("거래 루프 시작됨", "info")

def stop():
    global _running
    if not _running:
        audit.record("거래 종료 요청 무시: 이미 중지 상태", "info")
        return
    _running = False
    audit.record("거래 루프 정상 종료", "info")

def kill():
    global _running
    _running = False
    audit.record("거래 루프 긴급 중지", "error")

async def place(order: dict):
    """
    실거래 주문 실행 (KIS API)
    order 예시: {"symbol": "005930", "side": "buy", "qty": 1}
    """
    kis_base = os.getenv("KIS_API_URI_BASE")
    kis_app_key = os.getenv("KIS_APP_KEY")
    kis_app_secret = os.getenv("KIS_APP_SECRET")
    account = os.getenv("KIS_ACCOUNT_NUM")
    account_suffix = os.getenv("KIS_ACCOUNT_SUFFIX", "01")

    if not all([kis_base, kis_app_key, kis_app_secret, account]):
        audit.record("KIS API 환경변수 미설정 → 주문 불가", "error")
        return {"status": "error", "reason": "KIS API 환경변수 없음"}

    try:
        # 매수/매도 구분
        tr_id = "TTTC0802U" if order["side"] == "buy" else "TTTC0801U"

        headers = {
            "appkey": kis_app_key,
            "appsecret": kis_app_secret,
            "Content-Type": "application/json",
            "tr_id": tr_id
        }

        payload = {
            "CANO": account,
            "ACNT_PRDT_CD": account_suffix,
            "PDNO": order["symbol"],
            "ORD_DVSN": "01",  # 지정가
            "ORD_QTY": str(order["qty"]),
            "ORD_UNPR": "0"    # 시장가 주문 시 0
        }

        endpoint = f"{kis_base}/uapi/domestic-stock/v1/trading/order-cash"

        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.post(endpoint, headers=headers, json=payload)
            r.raise_for_status()
            data = r.json()

        audit.record(f"실거래 주문 실행: {order}", "trade", {"response": data})
        return {"status": "ok", "response": data}

    except Exception as e:
        audit.record(f"주문 실패: {e}", "error")
        return {"status": "error", "reason": str(e)}
