from typing import Any, Dict, List
from zulip_bots.lib import BotHandler
import time, requests, json, os, io
from datetime import datetime, timezone
from minio import Minio

# zulip-bot-shell -b zulip_bots/zulip_bots/bots/alfred/alfred.conf alfred


class ZohoHandler:
    def initialize(self, bot_handler: BotHandler) -> None:
        #########################################################
        """Keys and Clients"""
        #########################################################
        self.ZULIP_API_KEY = os.getenv("ZULIP_API_KEY")
        self.CLOCKIFY_API_KEY = os.getenv("CLOCKIFY_API_KEY")
        self.CLOCKIFY_WORKSPACE_ID = os.getenv("CLOCKIFY_WORKSPACE_ID")

        self.s3client = Minio(
            "s3.intranet:9000",
            access_key=os.getenv("S3_ACCESS_KEY"),
            secret_key=os.getenv("S3_SECRET_KEY"),
        )

        self.bucket_name = "alfred"

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
            "Authorization": f"Basic {self.ZULIP_API_KEY}",
        }
        self.zulip_timer_scheduled_messgaes_url = (
            "https://zulip.conversance.co/api/v1/scheduled_messages"
        )

        #########################################################
        """ Clockify """
        #########################################################
        self.clockify_key_subfolder = "clockify/key"
        self.clockify_workspace_id = self.CLOCKIFY_WORKSPACE_ID
        self.clockify_base_url = "https://api.clockify.me/api/v1"
        self.clockify_headers = {
            "content-type": "application/json",
            "x-api-key": self.CLOCKIFY_API_KEY,
        }

        self.commands_clockify = [
            "clock key <api_key>"
            "clock list",
            "clock in <project_label> <project_description>",
            "clock out",
        ]

        self.descriptions_clockify = [
            "Add API key for clockify"
            "List Clockify projects",
            "Start a new time entry",
            "Stop current timer",
        ]

        #########################################################
        """Metadata"""
        #########################################################
        self.version = "2.3"
        self.message = None
        self.bot_handler = None
        self.commands = [
            ["Basic :working_on_it:", [self.commands_basic, self.descriptions_basic]],
            ["Timer :timer:", [self.commands_timer, self.descriptions_timer]],
            ["Clockify :time:", [self.commands_clockify, self.descriptions_clockify]],
        ]
        self.notes = [
            "Clockify integration",
            "Ability to clock in tasks and clock out",
            "env variables added",
        ]

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
        email = message["sender_email"]
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
                    if subcommand == "key":
                        api_key = io.BytesIO(commands[2].encode('utf-8'))
                        email = message["sender_email"]
                        object_name = f"{self.clockify_key_subfolder}/{email}"
                        self.s3client.put_object(self.bucket_name, object_name, api_key, api_key.getbuffer().nbytes)
                        return "Key added successfully!"
                    elif subcommand == "list":
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

                        # get user
                        user = self.getClockifyUser(email)
                        user_id = user["id"]

                        # start timer
                        route = f"{self.clockify_base_url}/workspaces/{self.clockify_workspace_id}/user/{user_id}/time-entries"
                        startTime = (
                            datetime.now().astimezone(timezone.utc).isoformat(timespec="seconds")
                        )
                        startTime.replace("+00:00", "Z")
                        try:
                            response = requests.request(
                                "POST",
                                route,
                                headers=self.getClockifyHeaders(message["sender_email"]),
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
                        user = self.getClockifyUser(email)
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
                                headers=self.getClockifyHeaders(message["sender_email"]),
                                data=json.dumps({"end": endTime}),
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
            return f"An error occured: {str(e)}"

    def getPatchNotes(self):
        response = "**Version {version} features:** \n".format(version=self.version)
        for note in self.notes:
            response += f" - {note}\n"
        return response
    
    def getClockifyHeaders(self, email):
        try:
            object_name = f"{self.clockify_key_subfolder}/{email}"
            response = self.s3client.get_object(self.bucket_name, object_name)
            api_key = response.read().decode('utf-8')
        finally:
            response.close()
            response.release_conn()
        
        return {
            "content-type": "application/json",
            "x-api-key": api_key,
        }

    def getClockifyUser(self, email):
        route = f"{self.clockify_base_url}/workspaces/{self.clockify_workspace_id}/users"
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

        users = json.loads(response.content)
        user = [x for x in users if x["email"] == email][0]
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
