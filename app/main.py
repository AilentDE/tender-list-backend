from contextlib import asynccontextmanager
from fastapi import FastAPI
from loguru import logger

from routes.scheduler import router as scheduler_router
from routes.task_setting import router as scheduler_setting_router
from schduler.scheduler import app_scheduler, scheduler_jobs_start
from utils.db_handler import DatabaseHandler, DatabaseLogic

from utils.teams_handler import TeamsWebhook
from utils.tender_crawler import TenderCrawler

from schduler.task.get_tender import check_new_tender


@asynccontextmanager
async def lifespan(app: FastAPI):
    db_handler = DatabaseHandler()
    db_handler.init_table()
    db_handler.init_data()
    db_handler.close()

    scheduler_jobs_start(app_scheduler)
    yield
    logger.success("Server shutdown")


app = FastAPI(lifespan=lifespan)

app.include_router(scheduler_router, prefix="/scheduler", tags=["scheduler"])
app.include_router(scheduler_setting_router, prefix="/task/setting", tags=["task"])


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/test_teams")
def test_teams():
    teams_handler = TeamsWebhook()
    teams_handler.add_message("Hello, World!")
    teams_handler.mention_user("de@distantnova.com", "DE活下去")
    teams_handler.send_message()
    teams_handler.close()
    return {"Hello": "World"}


@app.get("/test_tender")
def test_tender():
    tender_crawler = TenderCrawler()
    tags = ["桌遊", "教材", "教具"]
    orgs = ["基隆市文化局"]
    for tag in tags:
        tender_crawler.get_tenders(keyword=tag)
    for org in orgs:
        tender_crawler.get_tenders(org=org)

    DatabaseLogic().insert_tenders(tender_crawler.tenders)
    ids = DatabaseLogic().select_past_tender()
    logger.success(ids)
    return {"Hello": "World"}


@app.get("/test_task")
def test_task():
    check_new_tender()
    return {"Hello": "World"}
