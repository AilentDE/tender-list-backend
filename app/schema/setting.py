from pydantic import BaseModel
from collections import namedtuple
from enum import StrEnum


Webhook = namedtuple("Webhook", ["primary", "debug"])
Date = namedtuple("Date", ["workdays", "holidays"])
Tag = namedtuple("Tag", ["tags", "org_tags"])


class WebhookType(StrEnum):
    PRIMARY = "primary"
    DEBUG = "debug"


class DateType(StrEnum):
    WORKDAY = "workday"
    HOLIDAY = "holiday"


class TagType(StrEnum):
    KEYWORD = "keyword"
    ORG = "org"


class WebhookInput(BaseModel):
    primary: str
    debug: str


class DateInput(BaseModel):
    workdays: list[str]
    holidays: list[str]


class TagInput(BaseModel):
    tags: list[str]
    org_tags: list[str]


class SettingOutput(BaseModel):
    webhook: WebhookInput
    date: DateInput
    tag: TagInput
