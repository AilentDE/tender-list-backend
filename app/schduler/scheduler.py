from apscheduler.schedulers.asyncio import AsyncIOScheduler

# from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime


app_scheduler = AsyncIOScheduler()


def print_time():
    print(datetime.now())


def scheduler_jobs_start(scheduler: AsyncIOScheduler):
    # scheduler.add_job(print_time, CronTrigger.from_crontab("* * * * *"))
    scheduler.add_job(print_time, IntervalTrigger(seconds=1), id="print_time")
    scheduler.start()
