from typing import Any, Dict
from zulip_bots.lib import BotHandler

class ZohoHandler:
    def usage(self) -> str:
        return """
        This is a zoho integration bot that sends you
        notifications of you zoho email.
        """

    def handle_message(self, message: Dict[str, Any], bot_handler: BotHandler) -> None:
        original_content = message['content']
        original_sender = message['sender_email']
        print(message)

        clientId = "1000.JK7QUA9K97LSRR3F0DTTT3OFMU4JHH"
        clientSecret = "b504b9dd8a70e1d02015699482db5ff35b42541138"
        scope = "ZohoMail.folders.READ"
        redirect_uri = "https://google.com"

        f"https://accounts.zoho.com/oauth/v2/auth?scope={scope}&client_id={clientId}&response_type=code&access_type=offline&redirect_uri={redirect_uri}"

        """
        bot_handler.send_message(dict(
            type='stream', # can be 'stream' or 'private'
            to=stream_name, # either the stream name or user's email
            subject=subject, # message subject
            content=message, # content of the sent message
        ))

        bot_handler.update_message(dict(
            message_id=self.message_id, # id of message to be updated
            content=str(self.number), # string with which to update message with
        ))

        bot_handler.storage.put("foo", "bar")
        print(bot_handler.storage.get("foo"))  # print "bar"
        """

        bot_handler.send_reply(message, original_content)
        emoji_name = "wave"  # type: str
        bot_handler.react(message, emoji_name)
        return


handler_class = ZohoHandler
