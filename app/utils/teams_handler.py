import requests
from collections import namedtuple
from loguru import logger

from config.state import get_setting

MentionUser = namedtuple("MentionUser", ["id", "name"])


class TeamsWebhook:

    _webhook: str
    _session: requests.Session
    messages: list[str] = []
    mention_user_target: MentionUser | None = None

    def __init__(self, debug: bool = False):
        (webhook, _, _) = get_setting()
        self._webhook = webhook.debug if debug else webhook.primary
        self._session = requests.Session()
        self._session.headers.update({"Content-Type": "application/json"})

    def add_message(self, message: str):
        self.messages.append({"type": "TextBlock", "text": message})

    def mention_user(self, email: str, display_name: str):
        self.mention_user_target = MentionUser(email, display_name)

    def send_message(self):
        data = {
            "type": "message",
            "attachments": [
                {
                    "contentType": "application/vnd.microsoft.card.adaptive",
                    "content": {
                        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                        "type": "AdaptiveCard",
                        "version": "1.2",
                        "body": self.messages,
                        "msteams": {"width": "Full"},
                    },
                }
            ],
        }
        if self.mention_user_target:
            self.messages.append(
                {
                    "type": "TextBlock",
                    "text": "<at>mention</at>",
                }
            )
            data["attachments"][0]["content"]["msteams"]["entities"] = [
                {
                    "type": "mention",
                    "text": "<at>mention</at>",
                    "mentioned": {
                        "id": self.mention_user_target.id,
                        "name": self.mention_user_target.name,
                    },
                }
            ]
        try:
            r = self._session.post(self._webhook, json=data, timeout=30)
            logger.success(f"Message sent to Teams: {r.text}")
            if r.status_code != 200:
                logger.error(f"Failed to send message to Teams: {r.text}")
                raise Exception(f"Failed to send message to Teams: {r.text}")
        except Exception as e:
            logger.critical(f"Failed to send message to Teams: {e}")
            raise e

    def clear_messages(self):
        self.messages = []
        self.mention_user_target = None

    def close(self):
        self._session.close()
