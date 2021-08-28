"""Extension for important utilities."""
import typing
import discord
from discord import flags
from discord.ext import commands
import merlin
from modules import cmds


class Core(commands.Cog):
    """
    Type: discord.ext.commands.Cog.

    The important uilities (sorta like cli) are in this cog / extension.
    Load this extension as an external file with `client.load_extension('cogs.core')`
    ---
    This cog contains:
    """
    description = "The core utilities"

    def __init__(self, bot):
        self.bot: merlin.Bot = bot

    @commands.command(name='id')
    @cmds.cli(showfmt=1)
    async def cmd_id(self, ctx, val: typing.Union[discord.TextChannel, discord.VoiceChannel, discord.User, discord.Message, discord.Role, discord.Invite]):
        """
        Return the id of a mention/obj.
        Supports text channels, voice channels, users, members, links to messages/invites, and roles
        """
        return val.id

    @commands.command(name='reply')
    async def reply(self, ctx, msg: str):
        """
        Reply to the message you are replying to.
        If you are not replying to a message, the bot will reply to you.
        """
        return await ctx.message.reply(msg)

    @commands.command(name="embed")
    async def embed(self, ctx):
        """
        Create a customised embed.
        """
        return  # not impl'd


def setup(bot: merlin.Bot):
    bot.add_cog(Core(bot))
