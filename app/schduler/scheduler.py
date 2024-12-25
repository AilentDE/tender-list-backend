from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime

from config.state import scheduler_state
from schduler.task.get_tender import check_new_tender

app_scheduler = AsyncIOScheduler()


def print_time():
    print(datetime.now())


def scheduler_jobs_start(scheduler: AsyncIOScheduler):
    scheduler.add_job(
        check_new_tender,
        CronTrigger(hour="1,7", minute=0, second=0),
        id="check_new_tender",
    )
    scheduler.start()
    scheduler_state.start()
