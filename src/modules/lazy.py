"""Makes my life easier."""
from copy import deepcopy as cpy
import asyncio as a
import traceback as tb
from contextlib import suppress as supp
import discord as d
from discord.ext import commands as cmds
from discord.utils import find as f, get as g
from discord.ext.commands import command as c, guild_only as noDM, dm_only
from modules import tools as t
from modules.logcfg import gLogr


b: cmds.Bot
fmt_exc = tb.format_exc


def init(bot: cmds.Bot):
    """Initialise this module."""
    global b
    b = bot


async def gmem(o, s, u=False):
    """
    Params
    ---
    - o: Guild, TextChannel, VoiceChannel, StageChannel
    - s: member snowflake or name
    """
    x = (
        o.guild
        if isinstance(o, (d.TextChannel, d.VoiceChannel, d.StageChannel))
        else o
    )
    with supp(d.HTTPException, AssertionError):
        if isinstance(s, int):
            return x.get_member(s) or await x.fetch_member(s)
        if isinstance(s, str):
            r = o.get_member_named(s)
            assert r
            return r
    if u:
        with supp(d.HTTPException, AssertionError):
            if isinstance(s, int):
                return b.get_user(s) or await b.fetch_user(s)
            if isinstance(s, str):
                return g(b.users, display_name=s)
    return None


class Cog(cmds.Cog):
    """Cog template."""

    def __init__(self):
        self.bot = b


def gensetup(*cogs):
    """
    Generate setup(bot) for extensions.
    ```py
    setup = gen_setup(Cog1, Cog2, Cog3)
    """

    def setup(bot):
        init(bot)
        for c in cogs:
            bot.add_cog(c(bot))

    return setup


def no_await(*coros):
    for coro in coros:
        b.loop.create_task(coro)
