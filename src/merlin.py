#!../bin/python
"""Core part, inheritance."""
import os
import sys
import json
import random
import asyncio
import traceback
import contextlib

# additional libs
import discord
from discord.ext import commands, tasks
import aiosqlite

# python external files
from modules.logcfg import gLogr
from modules.const import (
    style,
    NetLog,
    BOTSETFILE,
    LASTWRDFILE,
    SETFILE,
    WARNFILE,
    STRFILE,
    TAGFILE,
    RANKFILE,
    get_prefix,
    OnlineMode,
)
from modules import tools
from internal.classes import Tools, Context

__all__ = ["Bot"]
exts = [
    "jishaku",
    "modules.chat.chat",
]
logger = gLogr(__name__)

# scan the cogs folder
for ext in os.listdir("ext/"):
    if ext.endswith(".py"):
        exts.append("ext." + ext[:-3])


class Bot(commands.Bot):
    """
    Class for Merlin Bot client.

    subset of discord.Bot
    """
    initialize = True
    MODE = os.getenv("MODE")
    FILES = {
        BOTSETFILE: "botsets",
        LASTWRDFILE: "lastwrds",
        SETFILE: "sets",
        WARNFILE: "warns",
        STRFILE: "strs",
        TAGFILE: "tags",
        RANKFILE: "ranks",
    }
    db = {}
    tls = Tools
    netLogger: NetLog
    chatting: None

    def __init__(self, *args, **kwargs):
        logger.debug("Building bot...")
        super().__init__(*args, **kwargs)
        if kwargs.get("testing", 1):
            logger.info("Loading Extensions...")
            for ext in exts:
                print(end=f" >> \tLoading {ext}...\r")
                try:
                    self.load_extension(ext)
                    logger.hint(
                        style.green2 + f"Loaded: {ext}" + style.reset + "   "
                    )
                except commands.errors.ExtensionAlreadyLoaded:
                    return logger.hint(
                        "Loaded tasks already, continue execution."
                    )
                except Exception as err:
                    logger.error(
                        f"FAILED: {ext}{style.grey} - {style.yellow}"
                        + traceback.format_exception_only(err.__class__, err)[
                            0
                        ]
                    )
                    logger.debug("", exc_info=1)

    async def __aenter__(self):
        """Basically `async with bot:`."""
        logger.info("Starting tasks")
        self.fsyncs.start()
        self.netLogger = NetLog(self)

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        with contextlib.suppress(BaseException):
            logger.info("Cleaning up")
            for file, name in self.FILES.items():
                if file.endswith(".json"):
                    db_new = json.load(open(file, "r"))
                    self.db[name].update(db_new)
                    json.dump(self.db[name], open(file, "w"))
                if file.endswith(".db"):
                    await self.db[name].close()

    @classmethod
    def new(cls):
        return cls(
            command_prefix=get_prefix,
            description="an awesome open source discord bot coded in python",
            owner_id=653086042752286730,
            case_insensitive=True,
            intents=discord.Intents.all(),
        )

    async def fsync(self, file, name):
        """Sync configs/db to file."""
        if self.initialize:
            if file.endswith(".json"):
                self.db[name] = json.load(open(file, "r"))
            if file.endswith(".db"):
                self.db[name] = await aiosqlite.connect(file)
            return
        if file.endswith(".json"):
            db_new = json.load(open(file, "r"))
            db_new.update(self.db[name])
            self.db[name] = db_new
            json.dump(self.db[name], open(file, "w"))
        if file.endswith(".db"):
            await self.db[name].commit()

    @tasks.loop(minutes=1)
    async def fsyncs(self):
        """Task: Sync all files."""
        to_do_coro = []
        for file in self.FILES:
            name = self.FILES[file]
            to_do_coro.append(self.fsync(file, name))
        await asyncio.gather(*to_do_coro)

    # allow shorterned commands (SAP)
    async def get_command(self, name_s, i: discord.Message = None):
        if " " not in name_s:
            return await tools.get_cmd_i(
                self, name_s, tools.HashableDict(self.all_commands), i
            )

        names = name_s.split()
        if not names:
            return None
        cmd = await tools.get_cmd_i(
            self, names[0], tools.HashableDict(self.all_commands), i
        )
        if not isinstance(cmd, commands.GroupMixin):
            return cmd

        for name in names[1:]:
            new = None
            try:
                new = await tools.get_cmd_i(
                    self, name, tools.HashableDict(cmd.all_commands), i
                )
            except AttributeError:
                return cmd
            if new is None:
                return cmd
            cmd = new
        return cmd

    async def get_context(
        self,
        message: discord.Message,
        *,
        cls=Context,
        cmd=None,
        interactive: bool = False,
    ):
        view = commands.view.StringView(message.content)
        ctx = cls(prefix=None, view=view, bot=self, message=message)

        if self._skip_check(message.author.id, self.user.id):
            return ctx

        prefix = await self.get_prefix(message)
        invoked_prefix = prefix

        if isinstance(prefix, str):
            if not view.skip_string(prefix):
                return ctx
        else:
            if message.content.startswith(tuple(prefix)):
                invoked_prefix = discord.utils.find(view.skip_string, prefix)
            else:
                return ctx

        invoker = await self.get_command(
            view.get_word(), i=message if interactive else None
        )
        ctx.command = invoker
        if invoker is not None:
            invoker = invoker.qualified_name
        ctx.invoked_with = invoker
        ctx.prefix = invoked_prefix
        return ctx

    async def on_disconnect(self):
        logger.hint("disconnected")

    async def on_resumed(self):
        logger.hint("session resumed")

    async def on_connect(self):
        """Connected to Guilded."""
        logger.info(
            f"Logged in as {style.cyan}{self.user.name}{style.reset}"
            f" - {style.italic}{self.user.id}{style.reset}"
            f" in {style.magenta}{self.MODE} mode"
        )
        self.initialize = False

    async def on_ready(self):
        """Bot is ready."""
        self.netLogger("I'm ready!", noawait=True)

    async def on_error(self, event, *args, **kwargs):
        logger.fatal(
            f"Ignoring exception in event {event}:",
            # f"{style.red}{self.tls.get_exc(sys.exc_info()[1])}",
            exc_info=1,
        )
        if self.MODE != OnlineMode.FIX:
            logger.hint("Running in FIX MODE due to previous fatal exception")
            self.MODE = OnlineMode.FIX
