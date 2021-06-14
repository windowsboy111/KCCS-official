#!/bin/python3.8
"""
Merlin discord bot.
Startup script.

Copyright windowsboy111 2020 MIT license
https://github.com/windowsboy111/merlin-py
discord.py -- the main module. In fact the main scr.
"""
#import pre_start
import os
import sys
import types
from dotenv import load_dotenv
from merlin import Bot, asyncio, discord, commands, root_logger


sys.path.append(os.path.dirname(__file__))  # add this directory to the sys path
# initialize runtime variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
bot = Bot()


async def main():
    """Main coro. Run this."""
    async with bot:
        bot.MODE = os.getenv('MODE')
        await bot.start(TOKEN)


if __name__ == "__main__":
    loop = bot.loop
    task = loop.create_task(main())
    loop.run_until_complete(task)
