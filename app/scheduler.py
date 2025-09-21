from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.workflows import pre_open, intraday_loop, after_close
from app.log import audit

scheduler = AsyncIOScheduler(timezone="Asia/Seoul")

async def start_schedulers():
    audit.record("스케줄러 시작", "info")

    # 장전 준비 (08:30)
    scheduler.add_job(pre_open.run, "cron", hour=8, minute=30)

    # 장중 루프 (09:00~15:30, 1분마다)
    scheduler.add_job(intraday_loop.run, "cron", hour="9-15", minute="*/1")

    # 장후 마감 (15:40)
    scheduler.add_job(after_close.run, "cron", hour=15, minute=40)

    scheduler.start()
