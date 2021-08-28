"""Extension storing utilities commands."""
import csv
import random
import typing
import asyncio
from modules import tools
import contextlib
from datetime import datetime
import discord
from discord.ext import commands
from modules import minecraft
from modules import base_encoding, tools
from modules.const import STRFILE, chk_sudo
import json
from modules import excepts
import aiosqlite
import duckduckgo
import pyTableMaker
from modules.logcfg import gLogr
stringTable = json.load(open(STRFILE, 'r'))

class PollingCTL:
    @staticmethod
    async def cvt_valid_name(msg: discord.Message, name: str):
        if len(msg.mentions) > 0:
            for mention in msg.mentions:
                if mention.mention in name:
                    index = name.index(mention.mention)
                    name = name[0:index] + "@" + mention.display_name + name[(index+len(mention.mention)):]
        if len(msg.channel_mentions) > 0:
            for mention in msg.channel_mentions:
                if mention.mention in name:
                    index = name.index(mention.mention)
                    name = name[0:index] + "#" + mention.name + name[(index+len(mention.mention)):]
        if len(msg.role_mentions) > 0:
            for mention in msg.role_mentions:
                if mention.mention in name:
                    index = name.index(mention.mention)
                    name = name[0:index] + "@" + mention.name + name[(index+len(mention.mention)):]
        return name


class Utils(commands.Cog):
    """\
    Type: discord.ext.commands.Cog  
    Most of the utilities are stored in this cog  
    Load this extension as an external file with `client.load_extension('cogs.utils')`
    ---
    This cog contains:  
    ## Commands  
    - vote / poll
    - mc
    - invite
    - avatar
    - search
    - emoji
    """
    description = "Utilities command"
    def __init__(self, bot):
        self.bot = bot

    @commands.group(pass_context=True, help="/help vote", aliases=['poll', 'voting'], name='vote')
    async def vote(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("2 bed idk wat u r toking 'bout, but wut?")
            return

    @vote.command(name='create', aliases=['make', 'mk', 'new'])
    async def create(self, ctx: commands.Context, name='', *options: str):
        """
        Create a new poll
        Add your choice by reacting to the message
        end a poll with /poll end <id>
        """
        p = tools.AsyncPool()
        @p.make_worker()
        async def react(msg, emoji):
           await msg.add_reaction(emoji)

        name = await PollingCTL.cvt_valid_name(ctx.message, name)
        if name == '':
            await ctx.send('Bruh, wuts da title of the poll?')
            return 2
        if len(options) <= 1:
            options = ('yes', 'no')
        if len(options) > 26:
            await ctx.send('You cannot make a poll for more than 26 things!')
            return 3
        msg = await ctx.send("Once apon a time, there was a poll, that YOU SHOULDN'T SEE DIS MESSAGE! OR ELSE DISCORD IS LAGGY!")

        if len(options) == 2 and options[0].lower() == 'yes' and options[1].lower() == 'no':
            reactions = ['✅', '❌']
        elif len(options) <= 10:
            reactions = ['1⃣', '2⃣', '3⃣', '4⃣', '5⃣', '6⃣', '7⃣', '8⃣', '9⃣', '🔟']
        else:
            reactions = ['🇦', '🇧', '🇨', '🇩', '🇪', '🇫', '🇬', '🇭', '🇮', '🇯', '🇰', '🇱', '🇲', '🇳', '🇴', '🇵', '🇶', '🇷', '🇸', '🇹', '🇺', '🇻', '🇼', '🇽', '🇾', '🇿', '0️⃣', '1️⃣', '2️⃣', '3⃣', '4⃣', '5⃣', '6⃣', '7⃣', '8⃣', '9⃣', '🔟']
        description = []
        # form the output embed
        for x, option in enumerate(options):
            description += f'\n {reactions[x]} {option}'
        embed = discord.Embed(title=name, description=''.join(description), color=0x00FFBB)
        embed.set_author(name=ctx.message.author, icon_url=ctx.message.author.avatar_url)
        await msg.edit(embed=embed)
        # add reactions
        for i, reaction in enumerate(reactions[:len(options)]):
            if i == 20: msg = await ctx.send('And more reactions...')
            await p.add_task_nowait(msg, reaction)
        p.start(2)
        # change footer
        text = f'Poll ID: {base_encoding.IntEncoder.encode_base64(msg.id)}'
        if i > 19:
            text = "Not tally-able"
        embed.set_footer(text=text)
        embed.timestamp = datetime.utcnow()
        await msg.edit(embed=embed, content='')
        p.join()
        return 0

    @vote.command(name='check', help='Check polls that has not ended', aliases=['chk'])
    async def check(self, ctx, *, num='0'):
        if num == '0':
            num = 0xFFFFFF
        result = ''
        result2 = list()
        pollID = list()
        msg = await ctx.send('You have forgotten something...')
        messages = None
        if not num:
            messages = await ctx.message.channel.history(limit=0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF).flatten()
        else:
            messages = await ctx.message.channel.history(limit=int(num)).flatten()
        for message in messages:
            if message.author != ctx.message.guild.me:
                continue
            if not message.embeds:
                continue
            embed = message.embeds[0]
            try:
                if 'Poll ID: ' not in embed.footer.text:
                    continue
            except Exception:
                continue
            if embed.title.startswith('Results of the poll for "'): continue
            if embed.description != 'Poll ended':
                link = f'[{message.created_at}]({message.jump_url})\n'
                result += link
                result2.append(embed.title)
                pollID.append(message.id)
        if result == '':
            await msg.edit(content='No unended polls detected.')
            return
        rs = result.split('\n')
        embed = discord.Embed(title='Running polls')
        loopCount = 0
        for r in rs:
            if loopCount == len(result2):
                break
            embed.add_field(name=result2[loopCount], value=r)
            loopCount += 1
        await msg.edit(content='Results: ' + str(len(result2)), embed=embed)
        return pollID


    @vote.command(name='end')
    async def end(self, ctx, *, pollID='0'):
        """
        End a poll
        start a poll with `/poll create`
        the id of a poll is either the 64 based encoded form of message id or the original message id
        you can right click to get the message id if you have developer option enabled
        If one voted for multiple choices, only the first choice counts, others will be ignored
        """
        # pre processing: checks
        if pollID == 'all':
            ctx = await self.bot.get_context(ctx.message)
            ids = await self.check(num=None, ctx=ctx)
            if not any(ids):
                return 0
            for msgid in ids:
                channel = ctx.message.channel
                try:
                    ctx = await self.bot.get_context(await channel.fetch_message(msgid))
                    await self.end(ctx=ctx, pollID=msgid)
                except discord.NotFound: continue
            return 0
        if pollID == '0':       return await ctx.send('bruh i need da poll id')
        msg = await ctx.send('deleting `system32`...')

        # get the message
        try: poll_message = await discord.TextChannel.fetch_message(ctx.message.channel, int(pollID))
        except ValueError:
            try:
                poll_message = await discord.TextChannel.fetch_message(ctx.message.channel, base_encoding.IntEncoder.decode_base64(pollID))
            except Exception:
                return await ctx.send(":x: Failed to get message with the given id :L")
        if not poll_message.embeds:
            await msg.edit(content=':question: No embeds have been found')
            return 2
        embed = poll_message.embeds[0]
        if poll_message.author != ctx.message.guild.me: return 2

        # process the content
        try: embed.description.split('\n')
        except Exception: return 1
        unformatted_options = [x.strip() for x in embed.description.split('\n')]
        opt_dict = {x[:2]: x[3:] for x in unformatted_options} if unformatted_options[0][0] == '1' \
            else {x[:1]: x[2:] for x in unformatted_options}
        # check if we're using numbers for the poll, or x/checkmark, parse accordingly
        voters = [ctx.message.guild.me.id]  # add the bot's ID to the list of voters to exclude it's votes

        tally = {x: 0 for x in opt_dict.keys()}
        for reaction in poll_message.reactions:
            if reaction.emoji in opt_dict.keys():
                reactions = poll_message.reactions
                for reaction in reactions:
                    async for reactor in reaction.users():
                        if reactor.id not in voters:
                            try:
                                tally[reaction.emoji] += 1
                            except KeyError:
                                continue
                            voters.append(reactor.id)

        # make result
        output = discord.Embed(title='Results of the poll for "{}":\n'.format(embed.title), color=0xb6ff00)
        output.timestamp = datetime.utcnow()
        for key in tally.keys():
            output.add_field(name=opt_dict[key], value=tally[key])
            output.set_footer(text=pollID)
        await msg.edit(embed=output, content='')
        edited = discord.Embed(title=embed.title, description='Poll ended', color=0xFFC300)
        edited.set_footer(text=f"Result id: {msg.id}")
        await poll_message.edit(embed=edited)
        return 0

    @commands.group(name='mc', help="MINECRAFT", aliases=['minecraft'])
    async def mc(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send(":octagonal_sign: 2 bed idk wat u r toking 'bout, but wut?")
            return

    @mc.command(name='srv', help='list servers', aliases=['server'])
    async def srv(self, ctx, *, args: str = None):
        global embed
        global rtc
        embed = discord.Embed(title='Spinning \'round...', description='Gift me a sec')
        msg = await ctx.send(embed=embed)
        await msg.add_reaction(self.bot.get_emoji(687495401661661324))
        rtc = 0
        try:
            embed = minecraft.mcsrv(embed, args)
        except minecraft.InvalidArgument as e:
            rtrn = "<:err:740034702743830549> Panic 2: InvalidArgument. Send gud args!!!!!!!?\n""Details:  " + str(e) + "\n"
            rtrn += "2 get da usage, invoke da \"help\" cmd, aka `/help mc`"
            rtc = 2
        except minecraft.OfflineServer as e:
            rtrn = "<:err:740034702743830549> Panic 4: OfflineServer.  Details: {}\n".format(str(e))
            rtc = 3
        except Exception as e:
            rtrn = "<:err:740034702743830549> Panic 1: Unknun Era.  Program kthxbai.\nDetails:  " + str(e) + "\n"
            rtc = 1
        if rtc != 0:
            embed = discord.Embed(title="ERROR", description=str(rtrn), color=0xFF0000)
        embed.set_footer(text="kthxbai code: {}.".format(rtc))
        await msg.edit(embed=embed)
        await msg.remove_reaction(self.bot.get_emoji(687495401661661324), self.bot.user)

    @mc.command(name='addsrv', help='add a shortcut looking for a server', aliases=['asv'])
    async def addsrv(self, ctx, link: str = None, name: str = None, note: str = None):
        if not link or not name or not note:
            return await ctx.send('Missing required arguments :/')
        with open('data/mcsrvs.csv', mode='w') as csv_f:
            w = csv.writer(csv_f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            w.writerow([link, name, note])
            return await ctx.send('Operation completed successfully.')

    @mc.command(name='kill', help='cmd /kill')
    async def kill(self, ctx, *, member=None):
        try:
            if member == '@a' or member == '@e':
                a = ""
                for member in ctx.guild.members:
                    a += f'{member.display_name} fell out of the world\n'
                    a += f'Killed {member.display_name}\n'
                    await ctx.send(a)
                    a = ""
                return
            if member == '@r':
                r = random.choice(ctx.guild.members).display_name
                await ctx.send(f'{r} fell out fo the world.\nKilled {r}')
                return
            if member == '@p' or member == '@s':
                await ctx.send(f'{ctx.message.author.display_name} fell out of the world.\nKilled {ctx.message.author.display_name}')
                return
            if not member:
                await ctx.send(f'{ctx.message.author.display_name} fell out of the world.\nKilled {ctx.message.author.display_name}')
                return
            rs = ''
            for char in member:
                if char in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
                    rs += char
            member = self.bot.get_user(int(rs))
            member = member or ctx.message.author
            await ctx.send(f'{member.display_name} fell out of the world.\nKilled {member.display_name}')
            return 0
        except Exception as e:
            await ctx.send('No entity was found')
            print(e)

    @mc.command(name='crash')
    async def crash(self, ctx, *, args=None):
        await ctx.send("""```css
╔══════════════════════════════════════════════════════════════════════════════════╗
║                                    GAME CRASH                                    ║
║                                                                                  ║
║    An unexpected issue occurred and the game has crashed. We're sorry for the    ║
║                                  inconvenience.                                  ║
║                                   ╔═══════════╗                                  ║
║                                   ║   CLOSE   ║                                  ║
║                                   ╚═══════════╝                                  ║
║                                                                                  ║
╚══════════════════════════════════════════════════════════════════════════════════╝
```""")

    @commands.command(name='invite', help='get server invite link')
    @commands.guild_only()
    async def invite(self, ctx: discord.Invite):
        e = discord.Embed(title=f'{len(await ctx.guild.invites())} invite(s) found')
        for invite in await ctx.guild.invites():
            e.add_field(name=str(invite.inviter), value=f"[{invite.id}]({invite.url}): {invite.uses}")
        await ctx.send(embed=e)
        # await ctx.send((await ctx.guild.invites())[0].url)

    class ImageFormat(commands.Converter):
        """return image format (str), intended to be a function argument converter (function annotation)"""
        formats = ('webp', 'jpeg', 'jpg', 'png', 'gif')

        async def convert(self, ctx, arg: str):
            if arg not in self.formats:
                return None
            return arg

    @commands.command(name='avatar', help='show user avatar', aliases=['pfp', 'icon'])
    async def pfp(self, ctx, size: typing.Optional[int] = 1024, imageFormat: typing.Optional[ImageFormat] = 'png', user: discord.User = None):
        user = user or ctx.message.author
        formats = ('webp', 'jpeg', 'jpg', 'png')
        if user.is_avatar_animated():
            formats = ('gif', 'webp', 'jpeg', 'jpg', 'png')
        else:
            if imageFormat == 'gif':
                await ctx.send("I will not **gif**t you discord nitro!")
                return 2
        e = discord.Embed(
            title=f'Avatar of {str(user)}',
            description=' '.join([f"[{f}]({user.avatar_url_as(size=size, format=f)} \"size: {size}\" )" for f in formats])
        )
        e.set_image(url=user.avatar_url_as(format=imageFormat, size=size))
        e.timestamp = datetime.utcnow()
        await ctx.send(embed=e)
        return 0
    
    @commands.command()
    async def search(self, ctx, *, question: str):
        """
        give ya search results from the internet
        Using duckduckgo API
        `python3 -m pip install duckduckgo3`
        """
        if question.startswith("!!"):
            await ctx.send(duckduckgo.get_zci(question[2:]))
            return 0
        res = duckduckgo.query(question)
        e = discord.Embed(title=f"{len(res.results)} results and {len(res.related)} related", description=f'Answers about {question}')
        e.add_field(name='answer', value=f"{res.answer.type}: {res.answer.text}", inline=False)
        e.add_field(name='type', value=res.type, inline=False)
        if len(res.results) > 0:
            e.add_field(name='best result', value=f'[{res.results[0].text}]({res.results[0].url} "1st result")')
        if len(res.related) > 0:
            e.add_field(name='best related', value=f'[{res.related[0].text}]({res.related[0].url} "1st related")')
        e.add_field(name='Abstract', value=f'[{res.abstract.text}]({res.abstract.url} "{res.abstract.source}")')
        e.timestamp = datetime.utcnow()
        e.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
        e.set_footer(text="Results from DuckDuckGo", icon_url='https://cdn.discordapp.com/emojis/739863899674902578.png')
        await ctx.send(embed=e)

    def get_matching_emote(self, guild, emote_name):
        """
        Gets a matching emote from the given guild.
        :param guild: The guild to search.
        :type guild: discord.Guild
        :param emote: The full emote string to look for.
        :type emote: str
        :return:
        :rtype: discord.Emoji
        """
        matching_emote = []
        for emote in guild.emojis:
            if emote_name in emote.name:
                matching_emote.append(emote)
        return matching_emote

    @commands.command(name="emoji", aliases=["emojis"])
    async def emoji(self, ctx, name: str):
        """peek emoji from other servers"""
        emotes = []
        for guild in self.bot.guilds:
            emotes.extend(self.get_matching_emote(guild, name))
        if any(emotes):
            await ctx.send("\n".join([f"{emote} `{emote}` {emote.id}" for emote in emotes]))
        else:
            await ctx.send("broke my :mag:, maybe you should rephrase it?")
        return 0
    
    @commands.group(name="tutorial", aliases=['tut'])
    async def tutorial(self, ctx):
        """How to use merlin?????"""
        if ctx.invoked_subcommand is None:
            await ctx.send("This command helps you to understand how to use this bot correctly. get the usage of this command with `/help tut`.")
            return 0

    @tutorial.command(name='help', aliases=['?'])
    async def tutorial_help(self, ctx):
        await ctx.send(stringTable['tut']['help'])
        return 0
    
    @tutorial.command(name='embed', aliases=['e'])
    async def tutorial_embed(self, ctx):
        await ctx.send(stringTable['tut']['embed'])
        return 0

async def ranking_enabled(guild):
    global BOT
    gset = BOT.db['sets'][f'g{guild.id}']
    with contextlib.suppress(KeyError):
        if not gset['ranking']:
            return False
    return True
def cEnabled():
    async def predicate(ctx):
        return ranking_enabled(ctx.guild)
    return commands.check(predicate)
class Ranking(commands.Cog):
    """\
    Type: discord.ext.commands.Cog  
    A ranking system just like MEE6  
    Load this extension as an external file with `client.load_extension('cogs.utils')`
    ---
    This cog contains:  
    ## Commands  
    - rank
    - levels
    - setlvl
    """
    description = "Ranking system ;)"
    cooldown = {}
    bar = (' ', '▏', '▎', '▍', '▌', '▋', '▊', '▉', '█')
    logger = gLogr('Merlin.ranking')
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    @cEnabled()
    async def on_member_join(self, member: discord.Member):
        await self.init_member(member)

    @commands.Cog.listener()
    @cEnabled()
    async def on_guild_join(self, guild: discord.Guild):
        return await self.init_table(guild)

    @commands.Cog.listener()
    @cEnabled()
    async def on_guild_leave(self, guild: discord.Guild):
        return await self.deinit_table(guild)

    @commands.Cog.listener()
    @cEnabled()
    async def on_message(self, message):
        if message.author.bot:
            return
        with contextlib.suppress(KeyError):
            if message.author.id in self.cooldown[message.guild.id]:
                return
        with contextlib.suppress(KeyError, aiosqlite.OperationalError):
            await self.addxp(message.author, random.randint(2, 7))
            try:
                self.cooldown[message.guild.id].append(message.author.id)
            except KeyError:
                self.cooldown[message.guild.id] = [message.author.id]
            await asyncio.sleep(20)
            self.cooldown[message.guild.id].remove(message.author.id)


    async def addxp(self, member: discord.Member, count):
        lvl, xp = await self.getlvl(member)
        xp += count
        total = (2 ** (lvl))
        if xp >= total:
            lvl += 1
            xp -= total
            channel = await self.get_announcement_channel(member.guild)
            await channel.send(f"Hurray, {member}! You are now level {lvl}!")
        await self.setlvl(member, lvl, xp)
        return
        
    async def init_member(self, member: discord.Member):
        self.logger.info(f"Adding m{member.id} to g{member.guild.id}")
        cur = await self.bot.db['ranks'].execute(f"INSERT INTO g{member.guild.id} (ID, LVL, XP) VALUES (?, ?, ?);", (member.id, 1, 0))
        await cur.close()

    async def init_table(self, guild: discord.Guild):
        self.logger.info(f"Creating table g{guild.id} ({guild.name})")
        cur = await self.bot.db['ranks'].execute(
            f"""CREATE TABLE IF NOT EXISTS g{guild.id} (
                ID int,
                LVL int,
                XP int
            );""")
        await cur.close()

    async def deinit_table(self, guild: discord.Guild):
        self.logger.info(f"Dropping table IF EXISTS g{guild.id} ({guild.name})")
        cur = await self.bot.db['ranks'].execute(f"DROP TABLE g{guild.id};")
        await cur.close()

    async def setlvl(self, member: discord.Member, lvl, xp):
        db = self.bot.db['ranks']
        db.row_factory = aiosqlite.Row
        cur = await db.execute(f"""
            UPDATE g{member.guild.id}
            SET XP=?, LVL=?
            WHERE ID=?;""", (xp, lvl, member.id))
        await cur.close()

    async def getlvl(self, member: discord.Member):
        db = self.bot.db['ranks']
        db.row_factory = aiosqlite.Row
        cur = await db.execute(f"SELECT LVL, XP FROM g{member.guild.id} WHERE ID={member.id};")
        row = await cur.fetchone()
        if row is None:
            await self.init_member(member)
            return 1, 0
        lvl = row['LVL']
        xp = row['XP']
        await cur.close()
        return lvl, xp

    @commands.command()
    @commands.guild_only()
    @cEnabled()
    async def rank(self, ctx, member: discord.Member = None):
        """Show your xp and level."""
        member = member or ctx.author
        # self.logger.info(f"Loading rank for {member}")
        member = member or ctx.author
        lvl, xp = await self.getlvl(member)

        # format them, beautiful bar lol
        msgstr = f"Level **{lvl}** -- |`"
        fraction = xp / (2 ** (lvl))  # cur xp / full xp to lvl up
        fullToShow = int(30 * fraction)
        msgstr += self.bar[-1] * fullToShow
        msgstr += self.bar[int(len(self.bar) * (fraction - int(fraction)))]
        msgstr += self.bar[0] * (30 - fullToShow)
        msgstr += f"`| **{xp}**/{(2 ** (lvl))} xp {100*fraction:0.2f}%"
        await ctx.send(f"Rank for *{member}* in __{ctx.message.guild.name}__:\n{msgstr}")
        return
    
    @rank.error
    async def rank_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CommandInvokeError):
            if isinstance(error.original, aiosqlite.OperationalError):
                self.logger.warn("Caught OperationalError")
                if " no such table: g" in str(error):
                    await self.init_table(ctx.guild)
                    return await ctx.reinvoke()
        return await self.bot.errhdl_g(ctx, error)

    async def get_announcement_channel(self, guild: discord.Guild):
        try:
            channel_id = self.bot.db['sets'][f'g{guild.id}']['announcementChannel']
            assert channel_id is not None
            return guild.get_channel(channel_id)
        except (ValueError, AssertionError):
            await self.bot.netLogger("**Announcement Channel not set!!!**\nTo set the announcement channel, do `/id #TheChannelToSet`, then copy the id to `/settings set announcementChannel 123456789`")
            raise excepts.HaltInvoke()
    
    @commands.command(name='setlvl')
    @commands.guild_only()
    @cEnabled()
    @chk_sudo()
    async def cmd_setlvl(self, ctx, member: typing.Optional[discord.Member], lvl: int, xp: int = 0):
        """
        Manually set the lvl / xp of a member.
        
        Set your own level to 1:
        `/setlvl 1`
        Set @Bob's own level to 5:
        `/setlvl @Bob 5`
        Set your own level and xp to 99, 51:
        `/setlvl 99 51`
        Set @Bob's own level to 23, 12:
        `/setlvl @Bob 23 12`
        """
        member = member or ctx.author
        await self.setlvl(member, lvl, xp)
        await ctx.message.add_reaction("✅")
        return

    @commands.command()
    @cEnabled()
    async def levels(self, ctx):
        """List the ranks."""
        db = ctx.bot.db['ranks']
        db.row_factory = aiosqlite.Row
        cur = await db.execute(f'SELECT ID, LVL, XP FROM g{ctx.guild.id} ORDER BY LVL DESC, XP DESC;')
        rows = await cur.fetchall()
        table = pyTableMaker.OnelineTable()
        col_rank = table.new_column("Rank")
        col_member = table.new_column("Member")
        col_lvl = table.new_column("Level")
        col_xp = table.new_column("XP/Total")
        for i, row in enumerate(rows):
            table.insert(i+1, ctx.guild.get_member(row['ID']), row['LVL'], f"{row['XP']}/{2 ** row['LVL']}")
        tosend = tools.msgsep(table.get())
        for m in tosend:
            ctx.bot.loop.create_task(ctx.send(f"```css\n{m}\n```"))


def setup(bot):
    global BOT
    bot.add_cog(Utils(bot))
    bot.add_cog(Ranking(bot))
    BOT = bot
