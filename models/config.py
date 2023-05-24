#!/usr/bin/env python3.9

import json
from .discord_bot import DiscordBotInfo
from .mastodon_bot import MastodonBotinfo

class ConfigFile:
    def __init__(self, filepath: str):
        config_data = {}
        with open(filepath, 'r') as config_file:
            config_data = json.load(config_file)

        self.state_url = config_data["state_url"] 

        if "poll_interval" in config_data:
            self.poll_interval = config_data["poll_interval"]
        else:
            self.poll_interval = 30

        if "mastodon" in config_data:
            self.mastodon_bot = MastodonBotinfo(config_data["mastodon"])
        else:
            self.mastodon_bot = None

        self.discord_bot = DiscordBotInfo(config_data["discord"])
