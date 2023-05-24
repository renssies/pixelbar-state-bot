#!/usr/bin/env python3.9

class DiscordBotInfo:
    def __init__(self, json):
        self.token = json["token"]
        self.servers = list(map(DiscordBotServer, json["servers"]))

class DiscordBotServer:
    def __init__(self, json):
        self.name = json["name"]
        self.id = json["id"]
        self.channels = list(map(DiscordBotChannel, json["channels"]))

class DiscordBotChannel:
    def __init__(self, json):
        self.name = json["name"]
        self.id = json["id"]
        if "use_for_bot_state" in json:
            self.useForBotState = json["use_for_bot_state"]
        else:
            self.useForBotState = False

        if "remove_previous_message" in json:
            self.removePreviousMessage = json["remove_previous_message"]
        else:
            self.removePreviousMessage = False