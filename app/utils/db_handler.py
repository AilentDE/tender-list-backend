from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from loguru import logger
import sqlite3
import os

from schema.setting import (
    WebhookInput,
    DateInput,
    TagInput,
    WebhookType,
    DateType,
    TagType,
)
from schema.tender import Tender

if os.path.exists(".env"):
    load_dotenv()

tw_timezone = timezone(timedelta(hours=8), "Asia/Taipei")

DB_PATH = os.getenv("DB_PATH")


class DatabaseHandler:

    def __init__(self) -> None:
        self.no_rebuild = os.path.exists(DB_PATH)
        self.db = sqlite3.connect(DB_PATH)
        self.cur = self.db.cursor()
        logger.success(f"Database connected: {DB_PATH}")

    def init_table(self):
        if self.no_rebuild:
            logger.info("Database already exists, pass for init table")
            return
        # tender table
        self.cur.execute(
            """
            CREATE TABLE tender
            (id integer PRIMARY KEY AUTOINCREMENT,
            ref_id VARCHAR(32),
            name TEXT,
            url TEXT,
            startAt DATE,
            endAt DATE,
            budget INT,
            savedAt DATETIME);
        """
        )

        # webhook table
        self.cur.execute(
            """
            CREATE TABLE webhook
            (id integer PRIMARY KEY AUTOINCREMENT,
            type CHAR(16),
            url TEXT,
            createdAt DATETIME);
            """
        )

        # schedule table
        self.cur.execute(
            """
            CREATE TABLE schedule
            (id integer PRIMARY KEY AUTOINCREMENT,
            type CHAR(16),
            date DATE,
            createdAt DATETIME);
            """
        )

        # tag table
        self.cur.execute(
            """
            CREATE TABLE tag
            (id integer PRIMARY KEY AUTOINCREMENT,
            type CHAR(16),
            name TEXT,
            createdAt DATETIME);
            """
        )

        self.db.commit()
        logger.warning("Database initialized")

    def init_setting(self):
        if self.no_rebuild:
            logger.info("Database already exists, pass for init data")
            return
        # webhook
        self.cur.executemany(
            """
            INSERT INTO webhook (type, url, createdAt) VALUES (?, ?, ?);
            """,
            [
                ("primary", os.getenv("WEBHOOK_TOKEN"), datetime.now(tw_timezone)),
                ("debug", os.getenv("WEBHOOK_DEBUG_TOKEN"), datetime.now(tw_timezone)),
            ],
        )

        # tag
        tag_str = os.getenv("INIT_TAGS")
        tag_list = tag_str.split(",")
        self.cur.executemany(
            """
            INSERT INTO tag (type, name, createdAt) VALUES (?, ?, ?);
            """,
            [("keyword", tag, datetime.now(tw_timezone)) for tag in tag_list],
        )
        org_tag_str = os.getenv("INIT_ORG_TAGS")
        org_tag_list = org_tag_str.split(",")
        self.cur.executemany(
            """
            INSERT INTO tag (type, name, createdAt) VALUES (?, ?, ?);
            """,
            [("org", org_tag, datetime.now(tw_timezone)) for org_tag in org_tag_list],
        )
        self.db.commit()
        logger.warning("Database initialized")

    def close(self):
        self.db.close()
        logger.success("Database connection closed")


class DatabaseLogic:

    def __init__(self) -> None:
        self.db = sqlite3.connect(DB_PATH)
        self.cur = self.db.cursor()

    def update_webhook(self, webhook: WebhookInput):
        try:
            self.cur.execute(
                "UPDATE webhook SET url = ? WHERE type = ?",
                (webhook.primary, WebhookType.PRIMARY),
            )
            self.cur.execute(
                "UPDATE webhook SET url = ? WHERE type = ?",
                (webhook.debug, WebhookType.DEBUG),
            )
            self.db.commit()
            logger.success("Webhook updated")
        except Exception as e:
            logger.error(f"Error updating webhook: {e}")
            raise e
        finally:
            self.db.close()

    def update_date(self, date: DateInput):
        try:
            self.cur.execute("DELETE FROM schedule")
            if date.workdays:
                self.cur.executemany(
                    "INSERT INTO schedule (type, date, createdAt) VALUES (?, ?, ?)",
                    [
                        (DateType.WORKDAY, date, datetime.now(tw_timezone))
                        for date in date.workdays
                    ],
                )
            if date.holidays:
                self.cur.executemany(
                    "INSERT INTO schedule (type, date, createdAt) VALUES (?, ?, ?)",
                    [
                        (DateType.HOLIDAY, date, datetime.now(tw_timezone))
                        for date in date.holidays
                    ],
                )
            self.db.commit()
            logger.success("Date updated")
        except Exception as e:
            logger.error(f"Error updating date: {e}")
            raise e
        finally:
            self.db.close()

    def update_tag(self, tag: TagInput):
        try:
            self.cur.execute("DELETE FROM tag")
            self.cur.executemany(
                "INSERT INTO tag (type, name, createdAt) VALUES (?, ?, ?)",
                [(TagType.KEYWORD, tag, datetime.now(tw_timezone)) for tag in tag.tags]
                + [
                    (TagType.ORG, org_tag, datetime.now(tw_timezone))
                    for org_tag in tag.org_tags
                ],
            )
            self.db.commit()
            logger.success("Tag updated")
        except Exception as e:
            logger.error(f"Error updating tag: {e}")
            raise e
        finally:
            self.db.close()

    def select_past_tender(self, days: int = 60) -> list[str]:
        try:
            self.cur.execute(
                "SELECT ref_id FROM tender WHERE savedAt >= ?",
                (datetime.now(tw_timezone) - timedelta(days=days),),
            )
            return [row[0] for row in self.cur.fetchall()]
        except Exception as e:
            logger.error(f"Error selecting past tender: {e}")
            raise e
        finally:
            self.db.close()

    def insert_tenders(self, tenders: list[Tender]):
        try:
            self.cur.executemany(
                "INSERT INTO tender (ref_id, name, url, startAt, endAt, budget, savedAt) VALUES (?, ?, ?, ?, ?, ?, ?)",
                [
                    (
                        tender.ref_id,
                        tender.name,
                        tender.url,
                        tender.startAt,
                        tender.endAt,
                        tender.budget,
                        datetime.now(tw_timezone),
                    )
                    for tender in tenders
                ],
            )
            self.db.commit()
            logger.success("Tenders are inserted")
        except Exception as e:
            logger.error(f"Error inserting tenders: {e}")
            raise e
        finally:
            self.db.close()
