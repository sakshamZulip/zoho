from typing import Any, Dict, List
from zulip_bots.lib import BotHandler
import time, requests


class ZohoHandler:
    def initialize(self, bot_handler: BotHandler) -> None:
        self.message = None
        self.bot_handler = None
        self.headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': 'Basic em9oby1ib3QtYm90QHp1bGlwLmNvbnZlcnNhbmNlLmNvOjZId3Q5S25VMHlFY0tpS1RlTTFSbDFucHRvcHN1VTRJ'
        }
        self.scheduled_messgaes_url = "https://zulip.conversance.co/api/v1/scheduled_messages"

        self.commands = [
            "help",
            "list-commands",
            "timer <value> < s (seconds) | m (minutes) | h (hours) >",
            "test",
        ]

        self.descriptions = [
            "Display bot info",
            "Display the list of available commands",
            "Starts a timer",
            "test",
        ]

    def usage(self) -> str:
        return """
        Hi, I am your butler Alfred.
        Enter `list-commands` to show the list of available commands.
        Version 1.0
        """

    def handle_message(self, message: Dict[str, Any], bot_handler: BotHandler) -> None:
        content = message["content"].strip().split()

        if content == []:
            bot_handler.send_reply(message, "No Command Specified")
            return

        content[0] = content[0].lower()

        if content == ["help"]:
            bot_handler.send_reply(message, self.usage())
            return

        if content == ["list-commands"]:
            response = "**Available Commands:** \n"
            for command, description in zip(self.commands, self.descriptions):
                response += f" - {command} : {description}\n"

            bot_handler.send_reply(message, response)
            return

        self.message = message
        self.bot_handler = bot_handler
        response = self.generate_response(content)
        bot_handler.send_reply(message, response)
        return

    def generate_response(self, commands: List[str]) -> str:
        instruction = commands[0]
        try:
            if instruction == "timer":
                if len(commands) == 3:
                    current_time = int(time.time())
                    value = commands[1]
                    unit = commands[2]
                    self.bot_handler.send_reply(self.message, f"Timer started for {value} {unit}.")

                    if unit == "s":
                        value += current_time
                    elif unit == "m":
                        value = (value * 60) + current_time
                    elif unit == "h":
                        value = (value * 3600) + current_time
                    else:
                        return "Invalid unit for timer"
                    
                    payload = f'type=direct&to=%5B18%5D&content=Timer%20is%20up!&scheduled_delivery_timestamp={value}'
                    try:
                        response = requests.request("POST", self.scheduled_messgaes_url, headers=self.headers, data=payload)
                        if response.status_code == 200:
                            print("Message scheduled successfully!")
                        else:
                            print(f"Error: {response.status_code} - {response.text}")
                    except Exception as e:
                        print(f"An error occurred: {str(e)}")
                else:
                    return "Invalid number of arguments."
        except IndexError:
            return "Missing Params."

        return "Invalid Command."


handler_class = ZohoHandler
