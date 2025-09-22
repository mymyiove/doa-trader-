# app/scheduler.py
from typing import Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

# 실제 전략 모듈 연결
from app.workflows import pre_open, intraday_loop
from app.log import audit

def setup_scheduler(app, timezone: Optional[str] = "Asia/Seoul"):
    scheduler = AsyncIOScheduler(timezone=timezone)

    # 장전 루틴 08:30
    scheduler.add_job(pre_open.run, CronTrigger(hour=8, minute=30))
    audit.record("장전 루틴 스케줄 등록 완료", level="info")

    # 장중 루틴 09:00~15:30 매 1분
    scheduler.add_job(intraday_loop.run, CronTrigger(hour="9-15", minute="0-59"))
    audit.record("장중 루틴 스케줄 등록 완료", level="info")

    # 장후 루틴 15:40
    scheduler.add_job(lambda: audit.record("장후 루틴 실행됨", level="info"),
                      CronTrigger(hour=15, minute=40))

    scheduler.start()
    app.state.scheduler = scheduler
    audit.record(f"스케줄러 시작됨 (timezone={timezone})", level="info")
