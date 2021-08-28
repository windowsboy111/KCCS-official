import sys
import types
import traceback
import contextlib
import merlin
from modules import excepts
from modules.const import discord, commands, style, datetime
from modules.logcfg import gLogr


logger = gLogr(__name__)


async def errhdl_g(self, ctx, error):
    """General global error handler."""
    settings = self.db["sets"]
    stringTable = self.db["strs"]
    if isinstance(error, commands.errors.CommandInvokeError) and isinstance(
        error.original, excepts.HaltInvoke
    ):
        if error.original.msg:
            await ctx.send(error.original.msg)
        return 0  # well it is totally fine after all

    # This tells the issuer that the command cannot be used in DM
    if isinstance(error, commands.errors.NoPrivateMessage):
        with contextlib.suppress(Exception):
            await ctx.author.send(
                f":x::lock: {ctx.command} cannot be used in Private Messages."
            )
        return 3

    # Anything in ignored will return and prevent anything happening.
    if isinstance(error, commands.errors.CommandNotFound):
        try:
            if settings[f"g{ctx.guild.id}"]["cmdHdl"]["cmdNotFound"]:
                await ctx.send(
                    ":interrobang: Welp, I've no idea. Command not found!"
                )
        except KeyError:
            await ctx.send(
                ":interrobang: :two: :x:\n"
                "<:err:740034702743830549> Command not found!\n"
                "<:warn:739838316374917171> something went wrong in db handling, try running `/settings`"
            )
        return 2
    if isinstance(
        error, (commands.BadArgument, commands.MissingRequiredArgument, commands.errors.ConversionError)
    ):
        return await ctx.invoke(
            self.cmd_help, query=ctx.command.qualified_name
        )

    if isinstance(error, commands.errors.DisabledCommand):
        return await ctx.send(
            embed=discord.Embed(
                title=f":no_entry: {ctx.command} has been disabled.",
                description=f":x: `{ctx.command.qualified_name}`",
                color=0xFF0000,
            )
        )

    if isinstance(error, excepts.NotMod):
        await ctx.send(
            error.msg
            or f"`{ctx.author} is not in the sudoers file. This incident will be reported.`"
        )

    if isinstance(error, commands.errors.CommandInvokeError):
        await ctx.send(
            embed=discord.Embed(
                title="<:err:740034702743830549> uh oh. An exception has occurred during the execution of the command",
                description=stringTable["CommandInvokeError"].format(
                    content=ctx.message.content
                ),
                timestamp=datetime.utcnow(),
                color=0xFF0000,
            )
        )

    if isinstance(error, commands.errors.NotOwner):
        await ctx.send(stringTable["notOwner"])
        return 6

    # All other Errors not returned come here. And we can just print the default TraceBack.
    logger.error(
        f"Ignoring exception in command {ctx.command.qualified_name}:\n"
        f"{style.red}{ctx.bot.tls.get_exc(error)}",
    )
    await self.netLogger(
        f"Ignoring exception in command `{ctx.command.qualified_name}`:\n"
        f"\n```{ctx.bot.tls.get_exc(error)}\n```",
        ctx.guild,
    )
    return 1


def setup(bot: merlin.Bot):
    """Ext setup."""
    bot.errhdl_g = types.MethodType(errhdl_g, bot)
