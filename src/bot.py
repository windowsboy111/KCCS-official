"""
Merlin discord bot.
Startup script.

Copyright windowsboy111 2020-present MIT license
https://github.com/windowsboy111/merlin
"""
import os
import sys
from modules import lazy as l
from dotenv import load_dotenv
from merlin import Bot, asyncio, commands


sys.path.append(os.path.dirname(__file__))
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
ERR_EMOJI_ID = 740034702743830549
bot = Bot.new()
l.init(bot)


@bot.command(name="eval", help="it is eval", hidden=True)
@commands.is_owner()
async def _eval(self, ctx, *, code='"bruh wat to eval"'):
    with l.supp(Exception):
        await ctx.send(eval(code))
        return await ctx.message.add_reaction("✅")
    await asyncio.gather(
        ctx.message.add_reaction(ctx.bot.get_emoji()),
        ctx.send(
            ":x: uh oh. there's an error in your code:\n```\n"
            + l.fmt_exc()
            + "\n```"
        ),
    )


@bot.command(name="exec", help="Execute python", hidden=True)
@commands.is_owner()
async def _exec(self, ctx, *, code='return "???????"'):
    with l.supp(Exception):
        exec(code, globals(), locals())
        return await ctx.message.add_reaction("✅")
    await asyncio.gather(
        ctx.message.add_reaction(ctx.bot.get_emoji(ERR_EMOJI_ID)),
        ctx.send(
            ":x: uh oh. there's an error in your code:\n```\n"
            + l.fmt_exc()
            + "\n```"
        ),
    )


@bot.command(name="reload", help="reload a cog", hidden=True)
@commands.is_owner()
async def _reload(self, ctx, *, module: str):
    ctx.bot.reload_extension(module)
    await ctx.message.add_reaction("✅")


@bot.command(name="unload", help="unload a cog", hidden=True)
@commands.is_owner()
async def _unload(self, ctx, *, module: str):
    ctx.bot.unload_extension(module)
    await ctx.message.add_reaction("✅")


@bot.command(name="load", help="load a cog", hidden=True)
@commands.is_owner()
async def _load(self, ctx, *, module: str):
    ctx.bot.load_extension(module)
    await ctx.message.add_reaction("✅")


async def main():
    """Main coro. Run this."""
    async with bot:
        bot.MODE = os.getenv("MODE")
        await bot.start(TOKEN)


if __name__ == "__main__":
    bot.loop.run_until_complete(main())
