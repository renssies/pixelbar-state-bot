#!/usr/bin/env python3.9

class MastodonBotinfo:
    def __init__(self, json):
        self.instance = json["instance"]
        self.account = json["account"]
        self.clientKey = json["client_key"]
        self.clientSecret = json["client_secret"]
        self.accessToken = json["access_token"]