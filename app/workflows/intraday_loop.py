from app.log import audit
from app.data.watchlist import get_watchlist
from app.trade import executor
import os
import httpx
from datetime import datetime, timedelta

async def run():
    try:
        symbols = get_watchlist()
        if not symbols:
            audit.record("관심 종목 없음 → 매매 스킵", "info")
            return

        for sym in symbols:
            price_info = await get_realtime_price(sym)

            # 매수 조건
            if buy_condition(price_info):
                order = {
                    "symbol": sym,
                    "side": "buy",
                    "qty": int(os.getenv("TRADE_QTY", "1")),
                    "price": 0  # 시장가
                }
                resp = await executor.place(order)
                audit.record(f"매수 주문: {sym}", "trade", {"response": resp})

            # 매도 조건
            if sell_condition(price_info):
                order = {
                    "symbol": sym,
                    "side": "sell",
                    "qty": int(os.getenv("TRADE_QTY", "1")),
                    "price": 0  # 시장가
                }
                resp = await executor.place(order)
                audit.record(f"매도 주문: {sym}", "trade", {"response": resp})

    except Exception as e:
        audit.record(f"장중 루프 오류: {e}", "error")


async def get_realtime_price(symbol):
    kis_base = os.getenv("KIS_API_URI_BASE")
    kis_app_key = os.getenv("KIS_APP_KEY")
    kis_app_secret = os.getenv("KIS_APP_SECRET")

    headers = {
        "appkey": kis_app_key,
        "appsecret": kis_app_secret,
        "Content-Type": "application/json",
        "tr_id": "FHKST01010100"  # 주식 현재가
    }
    params = {
        "FID_COND_MRKT_DIV_CODE": "J",
        "FID_INPUT_ISCD": symbol
    }

    async with httpx.AsyncClient(timeout=5) as client:
        r = await client.get(f"{kis_base}/uapi/domestic-stock/v1/quotations/inquire-price",
                             headers=headers, params=params)
        r.raise_for_status()
        data = r.json()
        return {
            "symbol": symbol,
            "price": int(data["output"]["stck_prpr"]),
            "change_rate": float(data["output"]["prdy_ctrt"])
        }


def buy_condition(price_info):
    """
    매수 조건 예시:
    - 전일 대비 상승률이 0.5% 이상
    """
    return price_info["change_rate"] >= 0.5


def sell_condition(price_info):
    """
    매도 조건 예시:
    - 전일 대비 하락률이 -2% 이하 (손절)
    - 또는 상승률이 2% 이상 (익절)
    """
    return price_info["change_rate"] <= -2 or price_info["change_rate"] >= 2
