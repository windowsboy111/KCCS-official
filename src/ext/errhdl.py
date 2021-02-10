import sys
import types
import traceback
import contextlib
import merlin
from ext import excepts
from ext.const import discord, commands, style, datetime


async def errhdl_g(self, ctx, error):
    """General global error handler."""
    settings = self.db['sets']
    stringTable = self.db['strs']
    if isinstance(error, commands.errors.CommandInvokeError) and isinstance(error.original, excepts.HaltInvoke):
        if error.original.msg:
            await ctx.send(error.original.msg)
        return 0  # well it is totally fine after all

    # This tells the issuer that the command cannot be used in DM
    if isinstance(error, commands.errors.NoPrivateMessage):
        with contextlib.suppress(Exception):
            await ctx.author.send(f':x::lock: {ctx.command} cannot be used in Private Messages.')
        return 3

    # Anything in ignored will return and prevent anything happening.
    if isinstance(error, commands.errors.CommandNotFound):
        try:
            if settings[f'g{ctx.guild.id}']['cmdHdl']['cmdNotFound']:
                await ctx.send(":interrobang: Welp, I've no idea. Command not found!")
        except KeyError:
            await ctx.send(":interrobang: :two: :x:\n<:err:740034702743830549> Command not found!\n<:warn:739838316374917171> something went wrong, please run `/settings`")
        return 2
    if isinstance(error, (commands.BadArgument, commands.MissingRequiredArgument)):
        return await ctx.invoke(self.cmd_help, cmdName=ctx.command.qualified_name)

    if isinstance(error, commands.errors.DisabledCommand):
        return await ctx.send(embed=discord.Embed(
            title=f':no_entry: {ctx.command} has been disabled.',
            description=f':x: `{ctx.message.content}`',
            color=0xff0000
        ))

    if isinstance(error, excepts.NotMod):
        await ctx.send(error.msg or f"`{ctx.author} is not in the sudoers file.  This incident will be reported.`")

    if isinstance(error, commands.errors.CommandInvokeError):
        await ctx.send(embed=discord.Embed(
            title='<:err:740034702743830549> uh oh. An exception has occurred during the execution of the command',
            description=stringTable['CommandInvokeError'].format(
                content=ctx.message.content),
            timestamp=datetime.utcnow(),
            color=0xff0000
        ))

    if isinstance(error, commands.errors.NotOwner):
        await ctx.send(stringTable['notOwner'])
        return 6
    if isinstance(error, commands.errors.ConversionError):
        await ctx.send(
            ':bangbang: Hey bud, seems like you tried to input some invalid type of arguments to the command call!\n'
            'Either CoNsUlT a PsYcHiAtRiSt or check the usage. Please!')
        return 4

    if isinstance(error, commands.errors.BadArgument):
        await ctx.send(
            ':grey_question: Whoops. The discord special expression you have specified when issuing that command is invalid.'
            ':mag: This error occurrs usually because of the bot fails to find the object.')
        return 4

    # All other Errors not returned come here. And we can just print the default TraceBack.
    print(f"{style.red2}Ignoring exception in command {ctx.message.content}:\n{style.red}{merlin.get_exc(error)}{style.reset}", file=sys.stderr)
    await self.netLogger(f'Ignoring exception in command `{ctx.message.content}`:\n\n```{merlin.get_exc(error)}\n```', guild=ctx.guild)
    return 1


def setup(bot: merlin.Bot):
    """Ext setup."""
    bot.errhdl_g = types.MethodType(errhdl_g, bot)
