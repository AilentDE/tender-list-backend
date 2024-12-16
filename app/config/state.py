from utils.db_handler import DatabaseHandler
from schema.setting import Webhook, Date, Tag, WebhookType, DateType, TagType
from loguru import logger
from functools import lru_cache


class SchedulerState:

    _run: bool = False

    def __init__(self) -> None:
        self._run = False

    def start(self):
        self._run = True

    def stop(self):
        self._run = False

    def is_running(self):
        return self._run


scheduler_state = SchedulerState()


@lru_cache(maxsize=1)
def get_setting() -> tuple[Webhook, Date, Tag]:
    try:
        logger.info("Fetching setting from database")
        db_handler = DatabaseHandler()

        db_handler.cur.execute("SELECT * FROM webhook")
        webhook = db_handler.cur.fetchall()
        webhook_data = [None, None]
        for row in webhook:
            if row[1] == WebhookType.PRIMARY:
                webhook_data[0] = row[2]
            elif row[1] == WebhookType.DEBUG:
                webhook_data[1] = row[2]

        db_handler.cur.execute("SELECT * FROM schedule ORDER BY type, date")
        schedule = db_handler.cur.fetchall()
        schedule_data = [
            [row[2] for row in schedule if row[1] == DateType.WORKDAY],
            [row[2] for row in schedule if row[1] == DateType.HOLIDAY],
        ]

        db_handler.cur.execute("SELECT * FROM tag ORDER BY type, name")
        tag = db_handler.cur.fetchall()
        tag_data = [
            [row[2] for row in tag if row[1] == TagType.KEYWORD],
            [row[2] for row in tag if row[1] == TagType.ORG],
        ]

        db_handler.close()

        return (
            Webhook(primary=webhook_data[0], debug=webhook_data[1]),
            Date(workdays=schedule_data[0], holidays=schedule_data[1]),
            Tag(tags=tag_data[0], org_tags=tag_data[1]),
        )
    except Exception as e:
        logger.error(f"Error getting setting: {e}")
        raise e
