"""Moderation stuff."""
import json
import random
import asyncio
from datetime import datetime
import discord
from discord.utils import get
from discord.ext import commands
import aiosqlite
import pyTableMaker
from ext.excepts import NoMutedRole
from ext.const import WARNFILE, SETFILE, STRFILE, chk_sudo
muted = dict()
stringTable = json.load(open(STRFILE, 'r'))
settings = json.load(open(SETFILE, 'r'))


class Mod(commands.Cog):
    description = "Commands for moderation."
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name='role', aliases=['roles'], help='Get your role rolling automatically.  Possible sub-commands: assign, remove, create, delete')
    @chk_sudo()
    @commands.guild_only()
    async def role(self, ctx):
        if ctx.invoked_subcommand is None:
            return await ctx.send("2 bed idk wat u r toking 'bout, but wut?")

    @role.command(name='assign', aliases=['give', 'set', 'grant', 'add'], help='Possible rolename: 2a, 1b, friends, etc.', pass_context=True)
    async def assign(self, ctx, role: discord.Role, member: discord.Member = None):
        member = member or ctx.message.author
        if role is None:
            await ctx.send(f':x: Failed to get the role. {ctx.message.author.mention}, please make sure you got it right.')
            return 2
        await member.add_roles(role)
        await ctx.send(f':u6709: Role {role.mention} has been added to {member.mention} by {ctx.message.author.mention}.')

    @role.command(name='remove', aliases=['rm', 'revoke'], help='Possible rolename: 2a, 1b, friends, etc.', pass_context=True)
    async def remove(self, ctx, role: discord.Role, member: discord.Member = None):
        member = member or ctx.message.author
        if role is None:
            await ctx.send(f':x: Failed to get the role. {ctx.message.author.mention}, please make sure you got it right.')
            return 2
        await member.remove_roles(role)
        await ctx.send(f':u7981: Role {role.mention} has been removed from {member.mention} by {ctx.message.author.mention}.')

    @role.command(name='create', aliases=['make', 'mk'], help='Create a new role.')
    async def create(self, ctx, *, rolename):
        role = await ctx.guild.create_role(name=rolename)
        await ctx.send(f':new: :white_check_mark: {role.mention} created successfully. (Requested by {ctx.message.author.mention})')
        return 0

    @role.command(name='delete', aliases=['del'], help='Delete a role (remove from all users)')
    async def delete(self, ctx, *, role: discord.Role):
        if role:
            name = role.name
            await role.delete()
            await ctx.send(f'Role {name} deleted successfully. (Requested by {ctx.message.author.mention})')
            return 0
        await ctx.send(f'Failed to get the role. {ctx.message.author.mention}, please make sure you got it right.')
        return 2

    @commands.command(name='warn', help='Warn a person: /warn @person reason', aliases=['warning'])
    @chk_sudo()
    @commands.guild_only()
    async def warn(self, ctx, person: discord.Member = None, *, reason: str = 'Not specified'):
        if not person:
            return await ctx.send('No member has been specified.')
        db = ctx.bot.db['warns']
        db.row_factory = aiosqlite.Row
        cursor = await db.cursor()
        rc = cursor.rowcount
        cursor = await cursor.execute(f"SELECT MAX(ID) AS len FROM g{ctx.guild.id} WHERE Person=?;", (str(person.id), ))
        rows = await cursor.fetchall()
        if rows == [] or not rows[0]['len']:
            await cursor.execute(
                f"INSERT INTO g{ctx.guild.id} (ID,Person,Reason,Moderator,WarnedDate) VALUES (1,?,?,?,?);",
                (str(person.id), reason.replace('\\', '\\\\').replace('"', '\\"'), str(ctx.message.author.id), datetime.now())
            )
        else:
            await cursor.execute(
                f"INSERT INTO g{ctx.guild.id} (ID,Person,Reason,Moderator,WarnedDate) VALUES (?,?,?,?,?);",
                (str(rows[0][0] + 1), str(person.id), reason.replace('\\', '\\\\').replace('"', '\\"'), str(ctx.message.author.id), datetime.now())
            )
        await cursor.close()
        if rc == cursor.rowcount:
            return await ctx.send(
                'Failed to warn that bad guy. Unexpected catched error happened '
                '(no modification has been made to the db, which is unintended...)'
            )
        await db.commit()
        await ctx.send(f'{ctx.message.author.mention} warned {person.mention}.\nReason: {reason}.')
        await self.bot.netLogger(f'{ctx.message.author} warned {person}.\nReason: {reason}.', guild=ctx.guild)

    @commands.command(name='rmwn', help='Remove a warning: /rmwn @person warnNumber')
    @chk_sudo()
    @commands.guild_only()
    async def rmwn(self, ctx, person: discord.Member = None, *, num: int = 0):
        if not person:
            return await ctx.send(':octagonal_sign: No member has been specified.')
        db = ctx.bot.db['warns']
        cur = None
        if num == 0:
            cur = await db.execute(f"DELETE FROM g{ctx.guild.id} WHERE Person=?;", (str(person.id), ))
        else:
            cur = await db.execute(f"DELETE FROM g{ctx.guild.id} WHERE Person=? AND ID=?;", (str(person.id), str(num)))
        await cur.close()
        await db.commit()
        return await ctx.send(f'Removed warning(s) from {person.mention}.')

    @commands.command(name='chkwrn', aliases=['checkwarn', 'checkwarns', 'checkwarnings', 'ckwn', "chkwn"], help='Show warnings of member')
    @commands.guild_only()
    async def chkwrn(self, ctx, member: discord.Member = None, raw=''):
        member = member or ctx.message.author
        db = ctx.bot.db['warns']
        db.row_factory = aiosqlite.Row
        cur = await db.execute(f"SELECT ID,Moderator,Reason,WarnedDate FROM g{ctx.guild.id} WHERE Person=?;", (str(member.id), ))
        rows = await cur.fetchall()
        if rows == []:
            return await ctx.send(f":octagonal_sign: Member {member.mention} does not have any warnings.")
        if raw == 'raw':
            t = pyTableMaker.OnelineTable(cellwrap=25)
            t.new_column('Warn No.')
            t.new_column('Reason')
            t.new_column('Moderator')
            t.new_column('Date')
            loopCount = 1
            for warning in rows:
                user = await self.bot.fetch_user(warning[1])
                t.insert(loopCount, warning[2], user.display_name, warning[3])
                loopCount += 1
            embed = discord.Embed(title="Warnings", description='```css\n' + t.get() + '\n```', color=0x00FFBB)
            embed.set_author(name=member, icon_url=ctx.message.author.avatar_url)
            embed.timestamp = datetime.utcnow()
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="Warnings", description=f'list of warnings for {member.mention}', color=0x00FFBB)
            embed.timestamp = datetime.utcnow()
            embed.set_author(name=member, icon_url=member.avatar_url)
            loopCount = 1
            for warning in rows:
                user = await self.bot.fetch_user(warning[1])
                embed.add_field(name=user.display_name, value=str(loopCount) + '. ' + warning[2], inline=True)
                loopCount += 1
            await ctx.send(embed=embed)

    @commands.command(name='kick', help='/kick @someone [reason]', aliases=['sb', 'softban', 'k'])
    @chk_sudo()
    @commands.guild_only()
    async def kick(self, ctx, member: discord.Member = None, reason: str = 'Not specified'):
        try:
            if not member:
                await ctx.send(':octagonal_sign: Please specify a member.')
                return
            await member.send(f':wave: You have been kicked.\nReason: {reason}')
            await member.kick(reason=reason)
            return await ctx.send(
                f':wave: {ctx.message.author.mention} has kicked {member.mention}.\nReason: {reason}\n'
                + random.choice([
                    'https://tenor.com/view/kung-fu-panda-karate-kick-gif-15261593',
                    'https://tenor.com/view/strong-kick-hammer-down-fatal-blow-scarlet-johnny-cage-gif-13863296'])
            )
        except Exception as e:
            await ctx.send(f'Wut happened? {e}')

    @commands.command(name='ban', aliases=["b"], help='/ban @someone [reason]')
    @chk_sudo()
    @commands.guild_only()
    async def ban(self, ctx, member: discord.Member = None, reason: str = 'Not specified'):
        global oldID
        if not member:
            return await ctx.send(':octagonal_sign: Please specify a member.')
        await member.send(f'<:banhammer:743429852279079023> You have been banned.\nReason: {reason}')
        await member.ban(reason=reason)
        oldID = member.id
        await ctx.send(f'<:banhammer:743429852279079023> {ctx.message.author.mention} has banned {member.mention}.\nReason: {reason}\n' + random.choice([
            'https://imgur.com/V4TVpbC',
            'https://tenor.com/view/thor-banhammer-discord-banned-banned-by-admin-gif-12646581',
            'https://tenor.com/view/cat-red-hammer-bongo-cat-bang-hammer-gif-15733820'
        ]))

    @commands.command(name='unban', help='/unban userID')
    @chk_sudo()
    @commands.guild_only()
    async def unban(self, ctx, userID: int = 0):
        global oldID
        if userID == 0:
            if oldID == 0:
                return await ctx.send(f':octagonal_sign: {ctx.message.author.mention} please specify an user id.')
            userID = oldID
        user = await self.bot.fetch_user(userID)
        await ctx.guild.unban(user)
        await ctx.send("Fine. There you go.")

    @commands.command(name='mute', help='mute a member')
    @chk_sudo()
    @commands.guild_only()
    async def mute(self, ctx, member: discord.Member, mute_time: str, *, reason=None):
        global muted

        if mute_time.endswith('m'):
            t = int(mute_time[:-1]) * 60
        elif mute_time.endswith('h'):
            t = int(mute_time[:-1]) * 3600
        elif mute_time.endswith('d'):
            t = int(mute_time[:-1]) * 3600 * 24
        elif mute_time.endswith('w'):
            t = int(mute_time[:-1]) * 3600 * 24 * 7
        else:
            try:
                t = int(mute_time)
            except ValueError:
                await ctx.send(":octagonal_sign: time should ends with `m`, `h`, `d`, `w`, or no postfix.")
                return 2

        role = ctx.guild.get_role(ctx.bot.db['sets'][f'g{ctx.guild.id}']["mutedRole"])
        if role is None:
            raise NoMutedRole
        await member.add_roles(role)
        await ctx.send(f'**Muted** {member.mention}\n**Reason: **{reason}\n**Duration:** {mute_time}')

        await member.send(embed=
            discord.Embed(color=discord.Color.orange())
                .add_field(
                    name=f"You've been **Muted** in {ctx.guild.name}.", 
                    value=f"**Action By: **{ctx.author.mention}\n**Reason: **{reason}\n**Duration:** {mute_time}"
                )
        )
        try:
            muted[str(member.id)] += 1
        except KeyError:
            muted[str(member.id)] = 1
        await asyncio.sleep(t)

        if muted[str(member.id)] > 1:
            muted[str(member.id)] -= 1
            return
        try:
            await member.remove_roles(role)
        except discord.HTTPException:  # failed to rm the role (probably doesn't have the role)
            muted[str(member.id)] -= 1
            return
        await ctx.send(f"**Unmuted {member.mention}**")
        muted[str(member.id)] -= 1

    @mute.error
    async def mute_error(self, ctx, error):
        if isinstance(error, NoMutedRole):
            try:
                perm = discord.Permissions(speak=False, stream=False, send_messages=False, add_reactions=False)
                role = await ctx.guild.create_role(reason="For muting", name="Muted", colour=discord.Colour.darker_grey(), permissions=perm)
                for channel in ctx.guild.channels:
                    await channel.set_permissions(role, reason="For muting")
                ctx.bot.db['sets'][f'g{ctx.guild.id}']['mutedRole'] = role.id
                return await ctx.reinvoke()
            except (discord.Forbidden, discord.HTTPException, discord.NotFound, discord.InvalidArgument):
                return await ctx.send("<:qus:740035076250664982> That command requires creating a @Muted role inside this guild that does not allow members to send messages.")
        if isinstance(error, discord.Forbidden):
            return await ctx.send("Uh oh, I do not have permissions to add / remove roles!")
        await self.bot.errhdl_g(ctx, error)

    @classmethod
    async def set_warn_error(cls):
        async def warn_error(self, ctx, error):
            if isinstance(error, aiosqlite.OperationalError):
                db = ctx.bot.db['warns']
                await db.execute(
                    f"""
                    CREATE TABLE g{ctx.guild.id} (
                        ID int,
                        Person int,
                        Reason varchar(255),
                        Moderator varchar(255),
                        WarnedDate DATE
                    );
                    """
                )
                await db.commit()
                return await self.bot.invoke(ctx)
            await ctx.bot.errhdl_g(ctx, error)
        cls.warn.error(warn_error)
        cls.rmwn.error(warn_error)
        cls.chkwrn.error(warn_error)

def setup(bot: commands.Bot):
    cog = Mod(bot)
    bot.loop.create_task(cog.set_warn_error())
    bot.add_cog(cog)
