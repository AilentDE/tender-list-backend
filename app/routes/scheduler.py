from fastapi import APIRouter

from schema.response import BaseResponse
from config.state import scheduler_state
from schduler.scheduler import app_scheduler


router = APIRouter()


@router.get("/status")
def status():
    return BaseResponse(
        message="get scheduler status successfully",
        data={"running": scheduler_state.is_running()},
    ).response()


@router.post("/start")
def start():
    app_scheduler.resume_job("print_time")
    scheduler_state.start()
    return BaseResponse(
        message="start scheduler successfully",
        data={"running": scheduler_state.is_running()},
    ).response()


@router.post("/pause")
def pause():
    app_scheduler.pause_job("print_time")
    scheduler_state.stop()
    return BaseResponse(
        message="pause scheduler successfully",
        data={"running": scheduler_state.is_running()},
    ).response()
