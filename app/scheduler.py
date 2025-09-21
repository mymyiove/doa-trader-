from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.workflows import pre_open, intraday_loop, after_close

scheduler = AsyncIOScheduler(timezone="Asia/Seoul")

async def start_schedulers():
    scheduler.add_job(pre_open.run, "cron", hour=8, minute=30)
    scheduler.add_job(intraday_loop.run, "cron", hour="9-15", minute="*/1")
    scheduler.add_job(after_close.run, "cron", hour=15, minute=40)
    scheduler.start()