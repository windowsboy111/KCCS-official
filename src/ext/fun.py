from discord.ext import commands
import discord
import random
import json
lolpwd = 'samples/'
from modules.const import LASTWRDFILE


class Fun(commands.Cog):
    """\
    This cog is for fun only. Most of the commands here are for the author to
    experiment with discord.py. Most of them are out of support and contains
    hard-coded strings and objects which isn't great.
    ---
    ## Commands
    - cough
    - test
    - stupid
    - whatis
    - boomer
    - media
    - say
    - send
    """
    description = "Funny and old commands I guess."
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        lastword = self.bot.db["lastwrds"]
        try:
            lastword[f"g{message.guild.id}"][str(message.author.id)] = message.id
        except KeyError:
            lastword[f"g{message.guild.id}"] = {message.author.id: message.id}
        self.bot.db['lastwrds'] = lastword

    @commands.command(name='cough', help="Simulate cough. :)")
    async def cough(self, ctx):
        lolcough = [
            "What? You being infected coronavirus?", str(self.bot.get_emoji(684291327818596362)),
            "Please don't:\nSneeze on me;\nCough on me;\nTalk to me,\nNo oh oh!",
            "🤢", "Run, run, until it's done, done, until the sun comes up in the morn'."
        ]
        response = random.choice(lolcough)
        msg = await ctx.send(response)
        await msg.add_reaction('👀')
        return

    @commands.command(name='test', help="Respond with test messages!")
    async def test(self, ctx):
        loltest = [
            "!urban MEE6", "Am I a joke to you?", "!8ball Siriu-smart?", f"What? Are you a developer?{ctx.message.author.mention}",
            "Didn't expect anyone would use this command, but there it is!", "No test.", "Ping Pong!", "No.", "?????",
            "Siriusly, What did you expect?", "Stop.", "!8ball are you stupid?", "Vincidiot"
        ]
        response = random.choice(loltest)
        msg = await ctx.send(response)
        await msg.add_reaction('👍')
        return

    @commands.command(name='stupid', help='Shout at stupid things')
    async def stupid(self, ctx, *, args='that'):
        await ctx.send(random.choice([
            f'{args} is so so stupid!', f"I can't believe how stupid {args} is!",
            f"Seriously, {args}'s the stupidest thing I've ever heard!",
            f"STUPID STUPID STUPID STUPID STUPID STUPID STUPID STUPID {args}!",
            f"I can't believe {args}'s even a thing."
        ]))

    @commands.command(name='whatis', help='Tells you what the input is. /whatis minecraft')
    async def whatis(self, ctx, *, args=""):
        if args == "":
            await ctx.send("Bruh, where's the argument???")
            return
        await ctx.send(
            random.choice([
                f"{args} is generally {args}.", f"Technically, {args} is {args}!", f"To know what {args} is, please run `!urban {args}`",
                f"Well, not in a nutshell, {args} as {args} is {args} in {args} on {args} at {args} from {args} to {args}...It's just...{args}!!!!!",
                f"You are so dumb that you even don't know what {args} is!"
            ])
        )

    @commands.command(name='boomer', help="/boomer [person]", aliases=['boom', 'okboomer'])
    async def boomer(self, ctx, *, person=""):
        if person == "":
            person = ctx.message.author
            await ctx.send(f'OK BOOMER {person.mention}')
            return
        await ctx.send(f'OK BOOMER {person}')

    @commands.command(name='say', help='the bot is talking!')
    async def say(self, ctx, *, args=""):
        if args == '':
            return
        await ctx.send(args, tts=True)
        await ctx.message.delete()
        return

    @commands.command(name='send', help='The bot is sending messages!')
    async def send(self, ctx, *, args=""):
        if args == "":
            return
        await ctx.send(args)
        await ctx.message.delete()
        return
    
    @commands.command(name='quote', help='last message of that guy')
    async def quote(self, ctx, members: commands.Greedy[discord.Member]):
        lastword, result = json.load(open(LASTWRDFILE, 'r')), ""
        for member in members:
            try:
                lastmsg = await discord.TextChannel.fetch_message(ctx.message.channel, lastword[f'g{ctx.guild.id}'][str(member.id)])
                quoteResult = "\n> ".join(lastmsg.content.split("\n"))
                result += f'Last message by {member.mention}: {lastmsg.jump_url}\n> {quoteResult}\n\n'
            except Exception:
                result += f"Cannot find last message by {member.mention}\n"
        assert result != "", "no result"
        return await ctx.send(result)
    
    @quote.error
    async def quote_error(self, ctx, error):
        if isinstance(error, AssertionError) and str(error) == "no result":
            return await ctx.send("ｃｈｅｃｋ　ｔｈｅ　ｕｓａｇｅ！！！")
        await self.bot.errhdl_g(ctx, error)


def setup(bot):
    bot.add_cog(Fun(bot))
    # Adds the Fun commands to the bot
    # Note: The "setup" function has to be there in every cog file
