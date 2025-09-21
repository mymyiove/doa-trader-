from app.log import audit
from app.data.watchlist import get_watchlist
from app.trade import executor
import os
import httpx

async def run():
    try:
        symbols = get_watchlist()
        if not symbols:
            audit.record("관심 종목 없음 → 매매 스킵", "info")
            return

        for sym in symbols:
            price_info = await get_realtime_price(sym)
            if buy_condition(price_info):
                order = {"symbol": sym, "side": "buy", "qty": int(os.getenv("TRADE_QTY", "1")), "price": 0}
                resp = await executor.place(order)
                audit.record(f"매수 주문: {sym}", "trade", {"response": resp})
            if sell_condition(price_info):
                order = {"symbol": sym, "side": "sell", "qty": int(os.getenv("TRADE_QTY", "1")), "price": 0}
                resp = await executor.place(order)
                audit.record(f"매도 주문: {sym}", "trade", {"response": resp})

    except Exception as e:
        audit.record(f"오류 발생: {e}", "error")

async def get_realtime_price(symbol):
    kis_base = os.getenv("KIS_API_URI_BASE")
    kis_app_key = os.getenv("KIS_APP_KEY")
    kis_app_secret = os.getenv("KIS_APP_SECRET")
    headers = {
        "appkey": kis_app_key,
        "appsecret": kis_app_secret,
        "Content-Type": "application/json",
        "tr_id": "FHKST01010100"
    }
    params = {"FID_COND_MRKT_DIV_CODE": "J", "FID_INPUT_ISCD": symbol}
    async with httpx.AsyncClient(timeout=5) as client:
        r = await client.get(f"{kis_base}/uapi/domestic-stock/v1/quotations/inquire-price",
                             headers=headers, params=params)
        r.raise_for_status()
        data = r.json()
        return {"symbol": symbol, "price": int(data["output"]["stck_prpr"])}

def buy_condition(price_info):
    # 예: 가격이 5분 전보다 0.5% 이상 상승
    return True

def sell_condition(price_info):
    # 예: 목표 수익률 2% 또는 손절 -2%
    return False
