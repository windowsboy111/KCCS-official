"""
Message and command handling discord.py extension.

Command processing, command invoking, error handling,
and partial command support here.
"""
import asyncio
import discord
from discord.ext import commands
from modules import lazy as l
import merlin
import special


logger = l.gLogr(__name__)


class CmdHdl(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, e):
        # This prevents any commands with local handlers being handled here in on_command_error.
        if hasattr(ctx.command, "on_error"):
            return logger.debug("Ignore error, there exists on_error")
        # This prevents any cogs with an overwritten cog_command_error being handled here.
        if (
            ctx.cog
            and ctx.cog._get_overridden_method(ctx.cog.cog_command_error)
            is not None
        ):
            logger.debug("Ignore error, there exists cog_command_error")
            return
        logger.debug("Passing error to errhdl")
        err_code = await self.bot.errhdl_g(ctx, e)
        if err_code:
            self.bot.netLogger(
                f"FAIL {err_code}: `{ctx.message.content}`",
                ctx.guild,
                noawait=True,
            )

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        logger.debug(f"Processing message {message.id} (g{message.guild.id})")
        if await special.pre_on_message(message):
            return 0
        await l.a.gather(self.proc_cmd(message), self.chat_hdl(message))
        await special.post_on_message(message)

    async def proc_cmd(self, msg: discord.Message):
        """
        Process commands.

        Check if it is a valid command, then
        log and invoke it.
        """
        # just put a whatever 0 there as the default value, never gonna match
        if msg.channel.id == self.bot.db["sets"].get(f"g{msg.guild.id}", {}).get(
            "chatChannel", 0
        ):
            return

        try:
            # default keep quiet
            ctx = await self.bot.get_context(
                msg,
                interactive=not self.bot.db["sets"][f"g{msg.guild.id}"]
                .get("cmdHdl", {})
                .get("quiet", True),
            )
            if not ctx.command:
                return
            logger.hint(f"Invoke {ctx.command.qualified_name}")
            with l.supp(AttributeError):  # might be in DM
                self.bot.netLogger(
                    f"{msg.channel.mention} {msg.author} has issued command: `{ctx.command.qualified_name}`",
                    msg.guild,
                    noawait=True,
                )
            await self.bot.invoke(ctx)
            with l.supp(KeyError):
                if self.bot.db["sets"][f"g{msg.guild.id}"]["cmdHdl"][
                    "delIssue"
                ]:
                    await msg.delete()
            return 0
        except Exception:
            await msg.add_reaction("❌")
            logger.error(l.tb.format_exc(limit=5))
            return 1

    async def chat_hdl(self, msg: discord.Message):
        settings = self.bot.db["sets"]
        return  # for the time being
        # TODO
        with l.supp(KeyError):
            chatChannelID = settings[f"g{msg.guild.id}"]["chatChannel"]
            if (
                not isinstance(msg.channel, discord.DMChannel)
                and not msg.author.bot
            ):
                if msg.channel.id == chatChannelID:
                    await self.bot.chatting.response(self.bot, msg)
                elif settings[f"g{msg.guild.id}"]["cmdHdl"]["improveExp"]:
                    msgs = await msg.channel.history(limit=2).flatten()
                    await self.bot.chatting.save(msg.content, msgs[1].content)


def setup(bot):
    bot.add_cog(CmdHdl(bot))

    logger.debug("DISABLE on_message")

    @bot.event
    async def on_message(message):
        pass
