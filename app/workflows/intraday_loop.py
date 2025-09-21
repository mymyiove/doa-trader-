from app.data import news, filings, quotes
from app.strategy import scorer
from app.trade import executor, risk
from app.log import audit

async def run():
    try:
        audit.record("장중 루프 시작", "info")
        raw = {
            "news": await news.fetch(),
            "filings": await filings.fetch(),
            "quotes": await quotes.fetch_intraday()
        }
        audit.record("데이터 수집 완료", "info", {"keys": list(raw.keys())})

        signals = scorer.rank(raw)
        audit.record("전략 점수 계산 완료", "decision", {"signals": signals})

        picks = risk.filter_candidates(signals)
        if not picks:
            audit.record("신호 없음 → 강제 1주 진입 로직 실행", "decision")
            picks = risk.force_one_share(raw)

        for order in picks:
            if risk.preflight(order):
                resp = await executor.place(order)
                audit.record(f"주문 실행: {order}", "trade", {"response": resp})
    except Exception as e:
        audit.record(f"오류 발생: {e}", "error")
