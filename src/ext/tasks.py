"""
This file is a discord extension. Load it on startup (both pre and post is okay).
Contains events and tasks
"""
import json
import discord
import random
import asyncio
import os
import merlin
from ext.const import SETFILE, STATUSES, eventLogger
# settings = json.load(open(SETFILE))


async def status(bot: merlin.Bot):
    await bot.wait_until_ready()
    MODE = bot.MODE
    while True:
        try:
            if not MODE or MODE == 'NORMAL':
                activity = discord.Game(name=random.choice(STATUSES))
                await bot.change_presence(status=discord.Status.online, activity=activity)
            elif MODE == 'DEBUG':
                activity = discord.Activity(type=discord.ActivityType(
                    3), name="windowsboy111 debugging me")
                await bot.change_presence(status=discord.Status.idle, activity=activity)
            elif MODE == 'FIX':
                await bot.change_presence(status=discord.Status.dnd, activity=discord.Activity(type=discord.ActivityType(3), name="windowsboy111 fixing me"))
            await asyncio.sleep(30)
        except Exception:
            pass


async def on_member_join(member: discord.Member):
    eventLogger.info(f"{member} has joined {member.guild}")
    print(f"{member} has joined {member.guild}")
    return 0


async def on_guild_join(guild: discord.Guild):
    sudoers = []
    for name in [role.name for role in guild.owner.roles]:
        if ['admin', 'mod', 'owner'] in name.lower():
            sudoers.append(name)
    f = json.load(open(SETFILE, 'r'))
    f[f'g{guild.id}'] = {"prefix": ['/'],
                         "cmdHdl": {"cmdNotFound": 0}, "sudoers": sudoers}
    with open(SETFILE, 'w') as outfile:
        json.dump(f, outfile)
    return 0


def setup(bot: discord.ext.commands.Bot):
    bot.loop.create_task(status(bot))
    bot.event(on_member_join)
    # bot.event(on_guild_join)
