from typing import Any, Dict
from zulip_bots.lib import BotHandler
import requests

class ZohoHandler:
    def usage(self) -> str:
        return """
        This is a zoho integration bot that sends you
        notifications of you zoho email.
        """

    def handle_message(self, message: Dict[str, Any], bot_handler: BotHandler) -> None:
        original_content = message['content']
        original_sender = message['sender_email']

        bot_handler.send_reply(message, original_content)
        emoji_name = "wave"  # type: str
        bot_handler.react(message, emoji_name)
        return


handler_class = ZohoHandler