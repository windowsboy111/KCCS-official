"""Extension for importing the core cog containing important commands."""
import types
import asyncio
import traceback
import contextlib
from discord.ext import commands
from discord.utils import get
import discord, traceback, json, datetime
from merlin import Bot
from ext import excepts
from ext.const import chk_sudo, SETFILE, BOTSETFILE, DEFAULT_SETTINGS, is_sudoers
stringTable = json.load(open('ext/wrds.json', 'r'))


class Core(commands.Cog):
    """
    Type: discord.ext.commands.Cog.

    The most important commands of the bot are in this cog / extension.  
    Load this extension as an external file with `client.load_extension('cogs.core')`  
    ---
    This cog contains:  
    ## Commands
    - settings
    - info
    """

    description = "The important / basic commands."
    def __init__(self, bot):
        self.bot: Bot = bot

    async def init_sets(self, guild: discord.Guild):
        settings = self.bot.db['sets']
        try:
            settings[f"g{guild.id}"]['cmdHdl']
        except KeyError:
            settings[f"g{guild.id}"] = DEFAULT_SETTINGS.copy()
            with open(SETFILE, 'w') as outfile:
                json.dump(settings, outfile)
            return
        # fix cmdHdl
        cmdHdl = DEFAULT_SETTINGS['cmdHdl'].copy()          # the following code will leave entrys already
        cmdHdl.update(settings[f'g{guild.id}']['cmdHdl'])   # exists and add the missing entrys so that
        settings[f'g{guild.id}']['cmdHdl'] = cmdHdl         # overwriting can be prevented
        default = DEFAULT_SETTINGS.copy()
        default.update(settings[f'g{guild.id}'])            # we can also do the same thing for the whole settings
        settings[f'g{guild.id}'].update(default)


    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        await self.init_sets(guild)
        for role in guild.roles:
            if role.permissions.administrator:
                self.bot.db['sets'][f'g{guild.id}']['sudoers'].append(role.id)

    async def sett_set_val(self, base, val):
        with contextlib.suppress(ValueError):
            return base.append(bool(val))
        with contextlib.suppress(ValueError):
            return base.append(int(val))
        return base.append(val)

    async def sett_proc(self, ctx, base, entry: str, val: str):  # process settings assignments
        # coro, might be overengineered, but whatever
        try:
            base[entry]
        except KeyError:  # cannot access
            raise excepts.HaltInvoke(":x: Entry does not exist!")
        if not val:  # def'
            raise excepts.HaltInvoke(base[entry])
        if isinstance(base[entry], list):  # process the []s
            if ' ' not in val or not val.startswith(("add", "rm", "remove", "del")):
                raise excepts.HaltInvoke(base[entry])
            op = val.split()[0]
            val = " ".join(val.split()[1:])
            if op == 'add':
                if val in base[entry]:
                    raise excepts.HaltInvoke(":x: Already exists!")
                await self.sett_set_val(base[entry], val)
            if op in ('rm', "remove", "delete", "del"):
                if val not in base[entry]:
                    raise excepts.HaltInvoke(":x: Does not exists!")
                await self.sett_set_val(base[entry], val)
        if isinstance(base[entry], dict):  # proess the {}s, feed back into itself
            if " " not in val:
                raise excepts.HaltInvoke(base[entry])
            entry_ = val.split()
            val_ = " ".join(val.split()[1:])
            return await self.sett_proc(ctx, base[entry], entry_, val_)  # recursion
        try:
            base[entry] = int(val)
        except ValueError:
            base[entry] = val

    @commands.command(name='help', help='Shows this message', aliases=['?', 'cmd', 'cmds', 'commands', 'command'])
    async def cmd_help(self, ctx, *, cmdName: str = ""):
        """The Merlin help command."""
        bot = ctx.bot
        settings = bot.db['sets']
        prefix = ctx.prefix
        # check if user wants help for global cog
        if cmdName.lower() == "global":
            e = discord.Embed(title='Command list', description='wd: `/`', color=0x0000ff)
            for cmd in bot.walk_commands():
                e.add_field(name=cmd.name, value=cmd.short_doc or "<no help>")
            return await ctx.send(embed=e)
        # check if user wants help for a cog
        for cogName, cog in bot.cogs.items():
            if cogName.lower() == cmdName.lower():
                e = discord.Embed(title='Command list', description=f'wd: `/{cog.qualified_name}`')
                for cmd in cog.walk_commands():
                    if any(cmd.parents) or ' ' in cmd.qualified_name:
                        continue
                    e.add_field(name=cmd.name, value=cmd.short_doc or "<no help>")
                return await ctx.send(embed=e)
        # show help for command
        if cmdName:
            command = bot.get_command(cmdName)
            if not command or command.hidden: return await ctx.send(':mag: Command not found, please try again.')
            path = "/" + (command.cog.qualified_name if command.cog else "None") + "/" + "/".join(command.full_parent_name.split(" "))
            e = discord.Embed(title=f'Command `{prefix}' + command.qualified_name + '`', description=(path + '\n' + command.description or "<no description>"),color=0x0000ff)
            usage = prefix + command.qualified_name + ' '
            for key, val in command.clean_params.items():
                if val.default:
                    usage += f'<{val.name}>'
                else:
                    usage += f'<[{val.name}]>'
                usage += ' '
            e.add_field(name='Objective',   value=command.help)
            e.add_field(name='Usage',       value=usage)
            e.add_field(name='Cog',         value="<No cog>" if not command.cog else command.cog.qualified_name)
            e.add_field(name='Aliases',     value=', '.join(command.aliases) or "<No aliases>")
            if hasattr(command, 'commands') and any(command.commands):    # it is a group
                e.add_field(name='Sub-Commands', value=''.join([f"`{prefix}{cmd.qualified_name}`: {cmd.short_doc}\n" for cmd in command.commands]))
            await ctx.send(embed=e)
            return
        # no command name supplied, list all cogs
        e = discord.Embed(title="Cogs list")
        for _, cog in bot.cogs.items():
            e.add_field(name=cog.qualified_name, value=cog.description or "<no description>")
            e.set_footer(text="These are not commands, but groups of commands. `/help core` and stuff")
        await ctx.send(embed=e)

    @commands.guild_only()
    @commands.group(name='settings', aliases=['configure'])
    async def cmd_settings(self, ctx: commands.Context, entry:str="", *, val:str=""):
        """Configure Merlin for this discord server."""
        sets = self.bot.db['sets']
        gset = sets[f'g{ctx.guild.id}']
        if entry.startswith("{"):
            content = entry + ' ' + val
            sets[f'g{ctx.guild.id}'] = json.loads(content)
        if entry == "" or entry not in list(gset.keys()):
            return await ctx.send("```json\n" + json.dumps(gset, sort_keys=True, indent=2) + "\n```")
        await self.sett_proc(ctx, gset, entry, val)
        await ctx.message.add_reaction("✅")

    @cmd_settings.error
    async def settings_error(self, ctx, error):
        if isinstance(error, (KeyError, AssertionError)):
            await self.init_sets(ctx.guild)
            return await ctx.reinvoke()
        await self.bot.errhdl_g(ctx, error)

    @commands.group(name='info', help='info about everything')
    async def info(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            botinfo = self.bot.db['botsets']
            await ctx.send(embed=
                discord.Embed(
                    title="Info",
                    description="You can add subcommand/action after this command group to show specific info!",
                    timestamp=datetime.datetime.utcnow()
                )
                    .add_field(name="Server", value=f"{ctx.guild.id} / `{ctx.guild.name}`")
                    .add_field(name=self.bot.user, value=f"ver `{botinfo['version']}`")
                    .add_field(name="Member count", value=len(ctx.guild.members))
                    .set_footer(text=f"Run {ctx.prefix}`help info` for more info about the info command (Sounds funny)")
            )

    @info.command(name='user', help='info about a user (can be outside of this server!)')
    async def info_user(self, ctx: commands.Context, user: discord.User = None):
        user = user or ctx.author
        other_desc = ""
        if user.discriminator:
            other_desc += f":warning: username has conflict: {user.discriminator}\n"
        await ctx.send(embed=discord.Embed(
                title=f'user {user.display_name}',
                description=f'```{user.id}{" | BOT" if user.bot else ""}```',
                timestamp=user.created_at
            )\
            .add_field(name='Mention', value=f"{user.mention} / `{user.mention}`")\
            .set_author(name=user, icon_url=user.avatar_url)\
            .set_footer(text='Account created at')
        )

    @info.command(name='member', help='info about a member')
    @commands.guild_only()
    async def info_member(self, ctx, member: discord.Member = None):
        def getsStatus(status):
            if status == discord.Status.online:
                return 'online'
            if status == discord.Status.idle:
                return 'idle'
            if status == discord.Status.dnd:
                return 'do not disturb'
            return 'offline / invisible'
        member = member or ctx.author
        other_desc = ""
        if member.discriminator:
            other_desc += f":warning: username has conflict: {member.discriminator}\n"
        embed = discord.Embed(
            title=f'Member {member.display_name}',
            description=f'```{member.status} | {member.id}{" | BOT" if member.bot else ""}```',
            timestamp=member.joined_at
        )\
            .add_field(name='Mention', value=f"{member.mention} / `{member.mention}`")
        if member.is_on_mobile():
            embed.add_field(name='Device', value='Mobile')\
                .add_field(name='Mobile Status', value=getsStatus(member.mobile_status))
        else:
            embed.add_field(name='Device', value='Desktop / Web App')
        embed.add_field(name="Desktop Status", value=getsStatus(member.desktop_status))\
            .add_field(name="Web App Status", value=getsStatus(member.web_status))\
            .set_author(name=member, icon_url=member.avatar_url)\
            .add_field(name='Nickname', value=member.nick or f"<{member.mention} has no nickname>")\
            .add_field(name='Roles', value=', '.join([r.mention for r in member.roles[1:]]) or "<None>")\
            .set_footer(text='Member joined at', icon_url=ctx.guild.icon_url)
        await ctx.send(embed=embed)

    @info.command(name='channel', help='info about a channel')
    @commands.guild_only()
    async def info_channel(self, ctx, channel: discord.TextChannel = None):
        channel = channel or ctx.channel
        other_desc = ""
        if channel.is_nsfw():
            other_desc += ":warning: nsfw channel\n"
        if channel.is_news():
            other_desc += ":newspaper: news channel\n"
        if channel.category is not None:
            if channel.permissions_synced:
                other_desc += ":arrows_counterclockwise: :white_check_mark: Permission synced"
            else:
                other_desc += ":arrows_counterclockwise: :negative_squared_cross_mark: Permission outdated"
        embed = discord.Embed(title=f'Text Channel {channel.name}', description=f"```{channel.id}```{other_desc}", timestamp=channel.created_at)\
            .add_field(name="Category Position", value=channel.position or "<No position>")\
            .add_field(name='Category', value="<GLOBAL>" if channel.category is None else channel.category.name)\
            .add_field(name='Mention', value=f"{channel.mention} / `{channel.mention}`")\
            .add_field(name='Pinned messages', value=len(await channel.pins()))\
            .set_footer(text="Channel created")
        if any(await channel.invites()):
            embed.add_field(name='Invites', value=", ".join(f"[{invite.id}]({invite.url})" async for invite in channel.invites()))
        await ctx.send(embed=embed)

    @info.command(name='server', help='info about the current server', aliases=['guild', 'srv', 'g'])
    @commands.guild_only()
    async def info_server(self, ctx):
        settings = self.bot.db['sets']
        embed = discord.Embed(title='Server info', description=ctx.guild.description or "<description not set>", timestamp=ctx.guild.created_at)\
            .add_field(name="Server", value=f"{ctx.guild.name} - {ctx.guild.id}")\
            .add_field(name='Members count', value=ctx.guild.member_count)\
            .add_field(name='Roles count', value=len(ctx.guild.roles))\
            .add_field(name='Channels count', value=f"{len(ctx.guild.text_channels)} text / {len(ctx.guild.voice_channels)} voice - total {len(ctx.guild.channels)}")\
            .add_field(name='Categories count',value=len(ctx.guild.categories))\
            .add_field(name='Sudoers', value=", ".join([discord.utils.get(ctx.guild.roles, name=r).mention for r in settings[f'g{ctx.guild.id}']["sudoers"]]) or "<None>")\
            .add_field(name='Rules channel', value=ctx.guild.rules_channel.mention if ctx.guild.rules_channel else "Not set")\
            .add_field(name='System channel', value=ctx.guild.system_channel.mention if ctx.guild.system_channel else "Not set")\
            .add_field(name='Region', value=str(ctx.guild.region) or "Not set / found")\
            .add_field(name='afk', value=f"{ctx.guild.afk_timeout or '<no afk timeout>'} sec / {ctx.guild.afk_channel.name if ctx.guild.afk_channel else '<no afk channel>'}")\
            .add_field(name='Public updates channel', value=ctx.guild.public_updates_channel.mention if ctx.guild.public_updates_channel else "Not a public server / not set")\
            .add_field(name='Owner', value=ctx.guild.owner.mention)\
            .set_footer(text="Created at")
        if ctx.guild.icon_url:
            embed.set_image(url=ctx.guild.icon_url)
        await ctx.send(embed=embed)

    @info.command(name='bot', help='info about this discord bot', aliases=['merlin', 'this', 'self'])
    async def info_bot(self, ctx):
        settings = self.bot.db['botsets']
        embed = discord.Embed(title='Merlin info', description='an open-source discord.py bot', timestamp=datetime.datetime.utcnow())
        for key in settings.keys():
            embed.add_field(name=key, value=settings[key])
        await ctx.send(embed=embed)


def setup(bot: discord.ext.commands.Bot):
    bot.add_cog(Core(bot))
    bot.cmd_help = types.MethodType(Core.cmd_help.__call__, bot)
