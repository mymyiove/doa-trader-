from app.log import audit

async def run():
    audit.record("장후 루틴 시작", "info")
    # TODO: 당일 거래 결과 요약, 손익 계산, 리포트 생성
    audit.record("당일 거래 요약", "info", {
        "total_trades": 5,
        "win_rate": "60%",
        "pnl": "+1.25%"
    })
    audit.record("장후 루틴 종료", "info")
