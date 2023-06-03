#!/usr/bin/env python3.9

import time
import discord
import asyncio
import aiohttp
import json
import io
import sys
from discord.ext import commands
from mastodon import Mastodon
from datetime import datetime
from models.config import ConfigFile
from pytz import timezone

config_filepath = './data/config.json'
if len(sys.argv) > 1:
    config_filepath = sys.argv[1]
    
config = ConfigFile(config_filepath)

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

previous_space_state = None
previous_state_messages = {}

async def get_space_state() -> bool:
    url = config.state_url

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            response_json = await response.json()
            state = response_json["state"]
            if state == "open":
                return True
            elif state == "closed":
                return False
            else:
                print(f"Unknown response ${response_json}")
                print("Sending closed instead")
                return False

        
def send_mastodon_toot(state: bool):
    if config.mastodon_bot == None:
        return
    
    mastodon = Mastodon(
        client_id=config.mastodon_bot.clientKey, 
        client_secret=config.mastodon_bot.clientSecret, 
        access_token=config.mastodon_bot.accessToken, 
        api_base_url=config.mastodon_bot.instance
    )

    message = None
    if state:
        message = "Pixelbar is opened at {time}"
    else:
        message = "Pixelbar is closed at {time}"
        
    message = message.format(time=datetime.now(timezone('Europe/Amsterdam')).strftime("%H:%M:%S"))
    mastodon.status_post(message, visibility="unlisted")

async def send_state_discord_message(state: bool, ctx) -> discord.Message:
    if state:
        return await ctx.send("Pixelbar is open!")
    else:
        return await ctx.send("Pixelbar is closed")

async def update_discord_bot_presence(state: bool): 
    global bot

    if bot == None:
        return
    
    if state:
        await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.listening, name="Pixelbar is Open!", url="https://pixelbar.nl"))
    else:
        await bot.change_presence(status=discord.Status.dnd, activity=discord.Activity(type=discord.ActivityType.listening, name="Pixelbar is closed", url="https://pixelbar.nl"))

async def space_state_did_change(state: bool, send_channel_message: bool = True):
    global previous_space_state

    print(f"Space state did change to \"{'Open' if state == True else 'Closed'}\"")

    previous_space_state = state
    await update_discord_bot_presence(state)

    send_mastodon_toot(state)

    if send_channel_message == False:
        return
    
    for serverInfo in config.discord_bot.servers:
        for channelInfo in serverInfo.channels:
            channel = bot.get_channel(channelInfo.id)
            if channel == None:
                continue

            if channelInfo.removePreviousMessage == True and channelInfo.id in previous_state_messages:
                message = previous_state_messages[channelInfo.id]
                await message.delete()

            previous_state_messages[channelInfo.id] = await send_state_discord_message(state, channel)
                

async def run_polling():
    global previous_space_state
    while True:
        print(".", end="")
        try:
            space_state = await get_space_state()
            if previous_space_state != space_state:
                await space_state_did_change(space_state)
            await asyncio.sleep(config.poll_interval) # Wait for 2 minutes
        except Exception as e:
            print("Error getting space state")
            print(e)

@bot.hybrid_command()
async def state(ctx): 
   global previous_space_state
   try:
        space_state = await get_space_state()
        if previous_space_state != space_state:
            await space_state_did_change(space_state, False)
        await send_state_discord_message(space_state, ctx)
   except Exception as e:
       print("Error getting space state")
       print(e)
       await ctx.send("Failed to get space state")


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

    messages = set()
    for serverInfo in config.discord_bot.servers:
        for channelInfo in serverInfo.channels:
            if channelInfo.useForBotState:
                channel = bot.get_channel(channelInfo.id)
                if channel != None:
                    message = await channel.send("Bot started, this message will self-destruct in 3 seconds...")
                    messages.add(message)

    await asyncio.sleep(0.5)

    for message in messages:
         await message.delete()

    bot.loop.create_task(run_polling())

bot.run(config.discord_bot.token)