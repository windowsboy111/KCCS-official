"""This script contains constant paths and objects and also global functions."""
import json
import asyncio
from datetime import datetime
import discord
from discord.ext import commands
from modules import excepts
from modules.consolemod import style
from modules.logcfg import gLogr


with open("data/statuses.txt") as statusf:
    STATUSES = statusf.readlines()

# path for file storing data
BOTSETFILE = "ext/bot_settings.json"
LASTWRDFILE = "data/lastword.json"
SETFILE = "data/settings.json"
WARNFILE = "data/warnings.db"
STRFILE = "ext/wrds.json"
BOTSETFILE = "ext/bot_settings.json"
SETFILE = "data/settings.json"
TAGFILE = "data/tags.db"
RANKFILE = "data/rank.db"


logger, eventLogger, cmdHdlLogger = gLogr(
    "Merlin.root", "Merlin.event", "Merlin.cmdHdl"
)


def get_prefix(bot, message: discord.Message):
    """Get prefix for guild."""
    if isinstance(message.channel, discord.channel.DMChannel):
        return commands.when_mentioned_or(*("/"))(bot, message)
    settings = bot.db["sets"]
    prefix = None
    try:
        prefix = settings["g" + str(message.guild.id)]["prefix"]
    except KeyError:
        settings["g" + str(message.guild.id)] = {"prefix": ["/"]}
        json.dump(settings, open(SETFILE, "w"))
        prefix = ["/"]
    return commands.when_mentioned_or(*prefix)(bot, message)


class Log:
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    async def worker_log(name, queue):
        slept = 0
        while True:
            if slept >= 10:
                return  # timeout
            if queue.empty():
                slept += 0.1
                await asyncio.sleep(0.1)  # come back and check later
                continue
            channel, msg = await queue.get()
            await channel.send(f"[{datetime.utcnow().time()}] {msg}")
            queue.task_done()
            slept = 0  # reset timeout

    async def __call__(self, message: str, guild: discord.Guild = None):
        if guild:
            for channel in guild.channels:
                if channel.name == "merlin-py":
                    await channel.send(message)
                    return
            return
        queue = asyncio.Queue()
        tasks = []
        for i in range(5):
            tasks.append(
                asyncio.create_task(self.worker_log(f"worker-log-{i}", queue))
            )
        for guild in self.bot.guilds:
            for channel in guild.channels:
                if channel.name == "merlin-py":
                    queue.put_nowait((channel, message))
        while not queue.empty():
            await asyncio.sleep(0.2)


def is_sudoers(member: discord.Member):
    """\
    Type: function.
    Checks if the provided member has admin roles (has moderating priviledges)
    This function fetches the Admin roles list from the settings `dict()`
    ---
    return: bool
    """
    settings = json.load(open(SETFILE, "r"))
    if member.guild.owner == member:
        return True
    for role in member.roles:
        try:
            if role.name in settings[f"g{member.guild.id}"]["sudoers"]:
                return True
        except KeyError:
            settings[f"g{member.guild.id}"] = {"sudoers": [], "prefix": ["/"]}
            with open(SETFILE, "w") as outfile:
                json.dump(settings, outfile)
    return False


def chk_sudo():
    """\
    Type: decorator.
    The command will only be able to be executed by the author if the author is owner or have permissions.
    """

    async def predicate(ctx):
        if is_sudoers(ctx.author):
            return True
        await ctx.message.add_reaction("🛑")
        raise excepts.NotMod()

    return commands.check(predicate)


from enum import Enum
import json
import asyncio
from datetime import datetime
import discord
from discord.ext import commands
from modules import excepts
from modules.consolemod import style
from modules.logcfg import gLogr


# path for file storing data
BOTSETFILE = "ext/bot_settings.json"
LASTWRDFILE = "data/lastword.json"
SETFILE = "data/settings.json"
WARNFILE = "data/warnings.db"
STRFILE = "ext/wrds.json"
BOTSETFILE = "ext/bot_settings.json"
SETFILE = "data/settings.json"
TAGFILE = "data/tags.db"
RANKFILE = "data/rank.db"
STATFILE = "data/statuses.txt"


def get_prefix(bot, message: discord.Message):
    """Get prefix for guild."""
    if isinstance(message.channel, discord.channel.DMChannel):
        return commands.when_mentioned_or(*("/"))(bot, message)
    settings = bot.db["sets"]
    prefix = None
    try:
        prefix = settings["g" + str(message.guild.id)]["prefix"]
    except KeyError:
        settings["g" + str(message.guild.id)] = {"prefix": ["/"]}
        json.dump(settings, open(SETFILE, "w"))
        prefix = ["/"]
    return commands.when_mentioned_or(*prefix)(bot, message)


class NetLog:
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    async def worker_log(name, queue):
        slept = 0
        while True:
            if slept >= 10:
                return  # timeout
            if queue.empty():
                slept += 0.1
                await asyncio.sleep(0.1)  # come back and check later
                continue
            channel, msg = await queue.get()
            await channel.send(f"[{datetime.utcnow().time()}] {msg}")
            queue.task_done()
            slept = 0  # reset timeout

    async def acall(self, message: str, guild: discord.Guild):
        if guild:
            for channel in guild.channels:
                if channel.name == "merlin-py":
                    await channel.send(message)
                    return
            return
        queue = asyncio.Queue()
        tasks = []
        for i in range(5):
            tasks.append(
                asyncio.create_task(self.worker_log(f"worker-log-{i}", queue))
            )
        for guild in self.bot.guilds:
            for channel in guild.channels:
                if channel.name == "merlin-py":
                    queue.put_nowait((channel, message))
        while not queue.empty():
            await asyncio.sleep(0.2)

    def call(self, message: str, guild: discord.Guild):
        if guild:
            for channel in guild.channels:
                if channel.name == "merlin-py":
                    asyncio.create_task(channel.send(message))
                    return
            return
        queue = asyncio.Queue()
        tasks = []
        for i in range(5):
            tasks.append(
                asyncio.create_task(self.worker_log(f"worker-log-{i}", queue))
            )
        for guild in self.bot.guilds:
            for channel in guild.channels:
                if channel.name == "merlin-py":
                    queue.put_nowait((channel, message))

    def __call__(
        self, message: str, guild: discord.Guild = None, noawait=False
    ):
        if noawait:
            return self.call(message, guild)
        return self.acall(message, guild)


def is_sudoers(member: discord.Member):
    """\
    Type: function.
    Checks if the provided member has admin roles (has moderating priviledges)
    This function fetches the Admin roles list from the settings `dict()`
    ---
    return: bool
    """
    settings = json.load(open(SETFILE, "r"))
    if member.guild.owner == member:
        return True
    for role in member.roles:
        try:
            if role.name in settings[f"g{member.guild.id}"]["sudoers"]:
                return True
        except KeyError:
            settings[f"g{member.guild.id}"] = {"sudoers": [], "prefix": ["/"]}
            with open(SETFILE, "w") as outfile:
                json.dump(settings, outfile)
    return False


def chk_sudo():
    """\
    Type: decorator.
    The command will only be able to be executed by the author if the author is owner or have permissions.
    """

    async def predicate(ctx):
        if is_sudoers(ctx.author):
            return True
        await ctx.message.add_reaction("🛑")
        raise excepts.NotMod()

    return commands.check(predicate)


class OnlineMode(Enum):
    NORMAL = 0
    DEBUG = 1
    FIX = 2
