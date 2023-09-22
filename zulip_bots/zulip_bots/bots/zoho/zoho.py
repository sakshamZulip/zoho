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
        print(message)

        clientId = "1000.4FA9E4QL6LNEECL3M4WGV7PJ6B5J0B"
        clientSecret = "b504b9dd8a70e1d02015699482db5ff35b42541138"
        scope = "ZohoMail.folders.READ"
        redirect_uri = "https://zoho-pao5.onrender.com"

        query = f"https://accounts.zoho.com/oauth/v2/auth?scope={scope}&client_id={clientId}&response_type=code&access_type=offline&redirect_uri={redirect_uri}"

        """ zoho_auth_token = "YOUR_ZOHO_AUTH_TOKEN"
        zoho_email_endpoint = "https://mail.zoho.com/api/accounts/YOUR_ACCOUNT_ID/messages"
        zulip_bot_email = "YOUR_ZULIP_BOT_EMAIL"
        zulip_api_key = "YOUR_ZULIP_API_KEY"
        zulip_api_url = "https://your-zulip-instance.zulipchat.com/api/v1/messages" """

        try:
            response = requests.get(query)
            print(response)
            """ if response.status_code == 200:
                # Parse the Zoho email response to extract email details
                # You can customize this part based on the Zoho API response format
                zoho_email_data = response.json()

                # Send a notification to your Zulip account
                zulip_message = {
                    "type": "private",
                    "to": zulip_bot_email,
                    "content": f"New email received in Zoho: {zoho_email_data['subject']}"
                }

                # Send the message to Zulip
                zulip_response = requests.post(
                    zulip_api_url,
                    json=zulip_message,
                    auth=(zulip_bot_email, zulip_api_key)
                )

                if zulip_response.status_code == 200:
                    bot_handler.send_reply(message, "Notification sent successfully.")
                else:
                    bot_handler.send_reply(message, "Failed to send notification to Zulip.")
            else:
                bot_handler.send_reply(message, "Failed to fetch Zoho email data.") """
        except Exception as e:
            bot_handler.send_reply(message, f"An error occurred: {str(e)}")

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
