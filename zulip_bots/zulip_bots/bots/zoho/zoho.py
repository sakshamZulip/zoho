from typing import Any, Dict, List
from zulip_bots.lib import BotHandler
import time

class ZohoHandler:
    def initialize(self, bot_handler: BotHandler) -> None:
        self.message = None
        self.bot_handler = None

        self.commands = [
            "help",
            "list-commands",
            "timer <value> < s (seconds) | m (minutes) >",
        ]

        self.descriptions = [
            "Display bot info",
            "Display the list of available commands",
            "Starts a timer",
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
                    value = commands[1]
                    unit = commands[2]
                    self.bot_handler.send_reply(self.message, f"Timer started for {value} {unit}.")

                    if unit == "s":
                        time.sleep(int(value))
                        return "Timer is up!"
                    elif unit == "m":
                        time.sleep(int(value) * 60)
                        return "Timer is up!"
                    else:
                        return "Invalid unit for timer"
                else:
                    return "Invalid number of arguments."

        except IndexError:
            return "Missing Params."
            
        return "Invalid Command."

handler_class = ZohoHandler