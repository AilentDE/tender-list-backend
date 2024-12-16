from fastapi import APIRouter

from schema.response import BaseResponse
from schema.setting import SettingOutput, WebhookInput, DateInput, TagInput
from config.state import get_setting
from utils.db_handler import DatabaseLogic

router = APIRouter()


@router.get("/")
def show_setting():
    try:
        (webhook, date, tag) = get_setting()
    except Exception as e:
        return BaseResponse(
            success=False, message="get task setting failed", detail=str(e)
        ).response()
    return BaseResponse(
        message="get task setting successfully",
        data=SettingOutput(
            webhook=WebhookInput(
                primary=webhook.primary,
                debug=webhook.debug,
            ),
            date=DateInput(workdays=date.workdays, holidays=date.holidays),
            tag=TagInput(tags=tag.tags, org_tags=tag.org_tags),
        ).model_dump(),
    ).response()


@router.put("/webhook")
def update_webhook(webhook: WebhookInput):
    try:
        DatabaseLogic().update_webhook(webhook)
    except Exception as e:
        return BaseResponse(
            success=False, message="update webhook failed", detail=str(e)
        ).response()
    finally:
        get_setting.cache_clear()
    return BaseResponse(message="update webhook successfully").response()


@router.put("/date")
def update_date(date: DateInput):
    try:
        DatabaseLogic().update_date(date)
    except Exception as e:
        return BaseResponse(
            success=False, message="update date failed", detail=str(e)
        ).response()
    finally:
        get_setting.cache_clear()
    return BaseResponse(message="update date successfully").response()


@router.put("/tag")
def update_tag(tag: TagInput):
    try:
        DatabaseLogic().update_tag(tag)
    except Exception as e:
        return BaseResponse(
            success=False, message="update tag failed", detail=str(e)
        ).response()
    finally:
        get_setting.cache_clear()
    return BaseResponse(message="update tag successfully").response()
