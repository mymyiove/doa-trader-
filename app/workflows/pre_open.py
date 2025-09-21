from app.log import audit
import httpx
import os

async def run():
    audit.record("장전 루틴 시작 - 종목 발굴", "info")
    candidates = await find_candidates()
    from app.data.watchlist import set_watchlist
    set_watchlist(candidates)
    audit.record("장전 종목 발굴 완료", "decision", {"candidates": candidates})
    audit.record("장전 루틴 종료", "info")

async def find_candidates():
    kis_base = os.getenv("KIS_API_URI_BASE")
    kis_app_key = os.getenv("KIS_APP_KEY")
    kis_app_secret = os.getenv("KIS_APP_SECRET")

    headers = {
        "appkey": kis_app_key,
        "appsecret": kis_app_secret,
        "Content-Type": "application/json",
        "tr_id": "FHKST03010100"  # 전종목 시세
    }
    params = {
        "FID_COND_MRKT_DIV_CODE": "J",
        "FID_COND_SCR_DIV_CODE": "20171",
        "FID_INPUT_ISCD": "0000"
    }

    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(f"{kis_base}/uapi/domestic-stock/v1/quotations/inquire-daily-itemchartprice",
                             headers=headers, params=params)
        r.raise_for_status()
        data = r.json()
        # 여기서 거래량, 변동률, 거래대금 기준으로 상위 5개 추출
        items = data.get("output", [])
        scored = []
        for item in items:
            score = calc_score(item)
            scored.append((item["stck_shrn_iscd"], score))
        scored.sort(key=lambda x: x[1], reverse=True)
        top_symbols = [s[0] for s in scored[:5]]
        return top_symbols

def calc_score(item):
    # 거래량, 변동률, 거래대금 기반 점수 계산
    vol = int(item.get("acml_vol", 0))
    change = float(item.get("prdy_ctrt", 0))
    value = int(item.get("acml_tr_pbmn", 0))
    return (vol / 100000) + change + (value / 1_000_000_000)
