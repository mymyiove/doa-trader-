from app.log import audit

_running = False

def start():
    global _running
    if _running:
        audit.record("거래 시작 요청 무시: 이미 실행 중", "info")
        return
    _running = True
    audit.record("거래 루프 시작됨", "info")
    # TODO: 스케줄러나 전략 루틴 호출 연결
    # 예: intraday_loop.run() 주기적 실행

def stop():
    global _running
    if not _running:
        audit.record("거래 종료 요청 무시: 이미 중지 상태", "info")
        return
    _running = False
    audit.record("거래 루프 정상 종료", "info")
    # TODO: 스케줄러 중지 로직

def kill():
    global _running
    _running = False
    audit.record("거래 루프 긴급 중지", "error")
    # TODO: 모든 포지션 청산, 스케줄러 강제 종료

async def place(order: dict):
    """
    주문 실행 (현재는 모의 실행)
    order 예시: {"symbol": "005930", "side": "buy", "qty": 1}
    """
    audit.record(f"모의 주문 실행: {order}", "trade")
    # TODO: 실제 API 연동 시 체결 결과 반환
    return {"status": "ok", "order": order}
