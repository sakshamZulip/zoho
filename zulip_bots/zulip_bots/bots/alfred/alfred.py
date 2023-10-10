from typing import Any, Dict, List
from zulip_bots.lib import BotHandler
import time, requests, json
from datetime import datetime, timezone

# 1000.4FA9E4QL6LNEECL3M4WGV7PJ6B5J0B
# https://zoho-pao5.onrender.com/?code=1000.045c9afd2bc8edc7bcb631f4b829d6e2.8692867ba47934504a5a6faf9b2e1d52&location=us&accounts-server=https%3A%2F%2Faccounts.zoho.com
# zulip-bot-shell -b zulip_bots/zulip_bots/bots/alfred/alfred.conf alfred

# 650c92045c881944f09ec1b1


class ZohoHandler:
    def initialize(self, bot_handler: BotHandler) -> None:
        #########################################################
        """Basic"""
        #########################################################
        self.commands_basic = ["help", "list-commands", "patch-notes"]

        self.descriptions_basic = [
            "Display bot info",
            "Display the list of available commands",
            "Display the latest features",
        ]

        #########################################################
        """ Zulip Timer """
        #########################################################
        self.commands_timer = ["timer <value> < s (seconds) | m (minutes) | h (hours) >"]

        self.descriptions_timer = ["Starts a timer"]

        self.zulip_timer_headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": "Basic em9oby1ib3QtYm90QHp1bGlwLmNvbnZlcnNhbmNlLmNvOjZId3Q5S25VMHlFY0tpS1RlTTFSbDFucHRvcHN1VTRJ",
        }
        self.zulip_timer_scheduled_messgaes_url = (
            "https://zulip.conversance.co/api/v1/scheduled_messages"
        )

        #########################################################
        """ Clockify """
        #########################################################
        self.clockify_api_key = "NjkyMDBhYWYtZDNlNS00YzA3LThjMTktZjQ2NDAzNTdmMmQ3"
        self.clockify_workspace_id = "62503fbf4d9e3d2acb74af33"
        self.clockify_base_url = "https://api.clockify.me/api/v1"
        self.clockify_headers = {
            "content-type": "application/json",
            "x-api-key": self.clockify_api_key,
        }

        self.commands_clockify = ["clock list"]

        self.descriptions_clockify = ["List Clockify projects"]

        #########################################################
        """Metadata"""
        #########################################################
        self.version = "2.2"
        self.message = None
        self.bot_handler = None
        self.commands = [
            ["Basic :working_on_it:", [self.commands_basic, self.descriptions_basic]],
            ["Timer :timer:", [self.commands_timer, self.descriptions_timer]],
            ["Clockify :time:", [self.commands_clockify, self.descriptions_clockify]],
        ]
        self.notes = ["Clockify integration"]

    def usage(self) -> str:
        return """
        Hi, I am your butler Alfred.
        Enter `list-commands` to show the list of available commands.
        Version {version}
        """.format(
            version=self.version
        )

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
            response = "`Available Commands:` \n"
            for command in self.commands:
                command_type = command[0]
                command_details = command[1]
                response += f"```spoiler {command_type}\n"
                for command, description in zip(command_details[0], command_details[1]):
                    response += f" - {command} : {description}\n"
                response += "```\n"

            bot_handler.send_reply(message, response)
            return

        if content == ["patch-notes"]:
            response = self.getPatchNotes()
            bot_handler.send_reply(message, response)
            return

        self.message = message
        self.bot_handler = bot_handler
        response = self.generate_response(content, message)
        bot_handler.send_reply(message, response)
        return

    def generate_response(self, commands: List[str], message: Dict[str, Any]) -> str:
        instruction = commands[0]
        try:
            if instruction == "timer":
                if len(commands) == 3:
                    current_time = int(time.time())
                    value = int(commands[1])
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

                    payload = f"type=direct&to=%5B18%5D&content=Timer%20is%20up!&scheduled_delivery_timestamp={value}"
                    try:
                        response = requests.request(
                            "POST",
                            self.zulip_timer_scheduled_messgaes_url,
                            headers=self.zulip_timer_headers,
                            data=payload,
                        )
                        if response.status_code == 200:
                            print("Message scheduled successfully!")
                        else:
                            print(f"Error: {response.status_code} - {response.text}")
                    except Exception as e:
                        print(f"An error occurred: {str(e)}")
                else:
                    return "Invalid number of arguments."
            elif instruction == "clock":
                if len(commands) >= 2:
                    subcommand = commands[1]
                    if subcommand == "list":
                        response_arr = self.getClockifyProjectsArr()
                        projects = [x["name"] for x in response_arr]

                        reply = "**Projects:**\n"
                        for project in projects:
                            reply += f" - {project}\n"
                        return reply
                    elif subcommand == "in":
                        project_label = commands[2]
                        task_description = " ".join(commands[3:])

                        # get project id
                        response_arr = self.getClockifyProjectsArr()
                        project = [x["id"] for x in response_arr if x["name"] == project_label]

                        if len(project) == 0:
                            return "Invalid project. Check list using `clock list`."

                        project_id = project[0]

                        # start timer
                        route = f"{self.clockify_base_url}/workspaces/{self.clockify_workspace_id}/time-entries"
                        startTime = (
                            datetime.now().astimezone(timezone.utc).isoformat(timespec="seconds")
                        )
                        startTime.replace("+00:00", "Z")
                        try:
                            response = requests.request(
                                "POST",
                                route,
                                headers=self.clockify_headers,
                                data=json.dumps(
                                    {
                                        "start": startTime,
                                        "projectId": project_id,
                                        "description": task_description,
                                    }
                                ),
                            )
                            if response.status_code != 201:
                                print(f"Error: {response.status_code} - {response.text}")
                        except Exception as e:
                            print(f"An error occurred: {str(e)}")

                        return f"Clockify timer started for `{task_description}` under project `{project_label}`."
                    elif subcommand == "out":
                        user = self.getClockifyUser()
                        user_id = user["id"]

                        route = f"{self.clockify_base_url}/workspaces/{self.clockify_workspace_id}/user/{user_id}/time-entries"
                        endTime = (
                            datetime.now().astimezone(timezone.utc).isoformat(timespec="seconds")
                        )
                        endTime.replace("+00:00", "Z")
                        try:
                            response = requests.request(
                                "PATCH",
                                route,
                                headers=self.clockify_headers,
                                data=json.dumps({
                                    "end": endTime
                                })
                            )
                            if response.status_code != 200:
                                print(f"Error: {response.status_code} - {response.text}")
                        except Exception as e:
                            print(f"An error occurred: {str(e)}")

                        return "Clockify timer stopped."
                    else:
                        return "Invalid Command."
                else:
                    return "Invalid number of arguments."
            else:
                return "Invalid Command."
        except IndexError:
            return "Missing Params."
        except Exception as e:
            print(f"An error occurred: {str(e)}")

    def getPatchNotes(self):
        response = "**Version {version} features:** \n".format(version=self.version)
        for note in self.notes:
            response += f" - {note}\n"
        return response

    def getClockifyUser(self):
        route = f"{self.clockify_base_url}/user"
        try:
            response = requests.request(
                "GET",
                route,
                headers=self.clockify_headers,
            )
            if response.status_code != 200:
                print(f"Error: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"An error occurred: {str(e)}")

        user = json.loads(response.content)
        return user
    
    def getClockifyProjectsArr(self):
        route = f"{self.clockify_base_url}/workspaces/{self.clockify_workspace_id}/projects"
        try:
            response = requests.request(
                "GET",
                route,
                headers=self.clockify_headers,
            )
            if response.status_code != 200:
                print(f"Error: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"An error occurred: {str(e)}")

        response_arr = json.loads(response.content)
        return response_arr

handler_class = ZohoHandler
