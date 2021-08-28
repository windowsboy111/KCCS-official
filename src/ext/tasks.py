"""
This file is a discord extension. Load it on startup (both pre and post is okay).
Contains events and tasks
"""
import json
import discord
import random
import asyncio
import os
from discord.ext import tasks
from discord.ext import commands
from modules.const import SETFILE, STATFILE, OnlineMode
from modules.logcfg import gLogr

logger = gLogr('merlin.tasks')
logger.debug("Loading statuses")
statf = open(STATFILE, "r")


class Tasks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.status.start(bot)
        self.logger = logger

    def cog_unload(self):
        self.status.cancel()

    @tasks.loop(seconds=30)
    async def status(self, bot):
        stat = act = None
        if not bot.MODE or bot.MODE == OnlineMode.NORMAL:
            stat = discord.Status.online
            act = discord.Game(name=random.choice(statf.readlines()))
        elif bot.MODE == OnlineMode.DEBUG:
            stat = discord.Status.idle
            act = discord.Activity(
                type=discord.ActivityType(3),
                name="windowsboy111 debugging me",
            )
        elif bot.MODE == OnlineMode.FIX:
            stat = discord.Status.dnd
            act = discord.Activity(
                type=discord.ActivityType(3),
                name="windowsboy111 fixing me",
            )
        await bot.change_presence(status=stat, activity=act)

    @status.before_loop
    async def status_before(self):
        await self.bot.wait_until_ready()

    @status.error
    async def status_error(self, e):
        logger.warn("FAILED to set status")
        logger.warn(self.bot.tls.get_exc(e))

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        logger.debug(f"Having {member} joining guild {member.guild.id}")

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        logger.info(f"Joined guild {guild.id}")


def setup(bot):
    bot.add_cog(Tasks(bot))
