import discord
from discord.ext import commands
import enum
import random
import typing


class Rps:
    ROCK = 0
    PAPER = 1
    SCISSORS = 2

    @classmethod
    def get_emoji(cls, num: int):
        if num == cls.ROCK:
            return ":punch:"
        elif num == cls.PAPER:
            return ":hand_splayed:"
        elif num == cls.SCISSORS:
            return ":v:"
    
    @classmethod
    async def convert(cls, ctx, arg: str):
        """return paper, rock or scissors, intended to be a function argument converter (function annotation)"""
        if arg.lower() not in ('rock', 'paper', 'scissors'):
            raise commands.BadArgument('Either rock, paper or scissors.')
        return ('rock', 'paper', 'scissors').index(arg.lower())


class Games(commands.Cog):
    """\
    This cog store games :) you can play with it.
    ---
    ## Commands
    - rps (rock paper scissors)
    """
    description = "it is what it is."
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['rockpaperscissors', 'rock_paper_scissors', 'rock-paper-scissors'])
    async def rps(self, ctx, val: typing.Union[Rps, discord.Member]):
        """Enjoy your rock paper scissors"""
        if isinstance(val, discord.Member):
            pass
            # # play double
            # p1 = ctx.author
            # p2 = val
            # await p2.send(f'You have been challenged by {p1.mention} to play uhh rock paper scissors. what a boring game. do you wanna proceed?')
        myChoice = random.choice((0, 1, 2))
        embed = None
        desc = f'Me: {Rps.get_emoji(myChoice)}\nYou: {Rps.get_emoji(val)}'
        if myChoice == val:
            embed = discord.Embed(title="Draw!",        description=desc, color=0xffff00)
        elif myChoice - val == 1 or (myChoice + 2) == val:
            embed = discord.Embed(title="You lose!",    description=desc, color=0xff0000)
        else:
            embed = discord.Embed(title="You win!",     description=desc, color=0x00ff00)
        await ctx.send(embed=embed)

    @commands.command(aliases=['coin'])
    async def coinflip(self, ctx):
        """flip a coin: head or tail?"""
        await ctx.send('head' if round(random.random()) == 1 else 'tail')
        return 0

    @commands.command()
    async def answer(self, ctx, *, question):
        """answer a yes / no question"""
        # the idea of this command comes from the gurb bot in FlytechVideos discord server
        if not question.endswith(('?', '？')):
            await ctx.send("A question shall ends with a `?`")
            return 2
        await ctx.send(random.choice(['Yes.', 'Absolutely.', 'Nah.', 'Yes? No? Maybe? Can you please repeat the question?', 'Definitely not.', 'Probably.', 'Maybe.', 'Of course.', 'Ask me later.', 'Can you rephrase your question?', 'Damn right yes!', 'WTF NO!']))
        return 0

def setup(bot):
    bot.add_cog(Games(bot))
