from app.data import news, filings, quotes
from app.strategy import scorer
from app.trade import executor, risk
from app.log import audit

async def run():
    # 1. 데이터 수집
    raw = {
        "news": await news.fetch(),
        "filings": await filings.fetch(),
        "quotes": await quotes.fetch_intraday()
    }
    # 2. 전략 점수 계산
    signals = scorer.rank(raw)
    # 3. 리스크 필터링
    picks = risk.filter_candidates(signals)
    # 4. 강제 1주 진입 로직
    if not picks:
        picks = risk.force_one_share(raw)
    # 5. 주문 실행
    for order in picks:
        if risk.preflight(order):
            resp = await executor.place(order)
            await audit.record(order, resp)