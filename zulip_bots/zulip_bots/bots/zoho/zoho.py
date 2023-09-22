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
        msg = message["content"]
        if msg == "help" or msg == "":
            bot_handler.send_reply(message, self.usage())
            return
        reply = requests.get("https://api.susi.ai/susi/chat.json", params=dict(q=msg))
        try:
            answer = reply.json()["answers"][0]["actions"][0]["expression"]
        except Exception:
            answer = "I don't understand. Can you rephrase?"
        bot_handler.send_reply(message, answer)


handler_class = ZohoHandler