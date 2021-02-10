"""Core part, inheritance."""
import os
import sys
import copy
import json
import types
import random
import asyncio
import warnings
import traceback
import contextlib
from functools import wraps
# additional libs
import discord
import aiosqlite
from discord.ext import tasks
from discord.ext import commands
# python external files
from ext import excepts
from ext.logcfg import gLogr
from ext.const import STATUSES, style, Log, BOTSETFILE, LASTWRDFILE, SETFILE, WARNFILE, STRFILE, TAGFILE, RANKFILE, get_prefix
__all__ = ["Bot"]
exts = ['ext.tasks', 'ext.cmdhdl', 'ext.errhdl', 'ext.console', 'modules.chat.chat']
root_logger = gLogr('Merlin.root')


def get_exc(err):
    return "".join(traceback.format_exception(err.__class__, err, sys.exc_info()[2]))


# scan the cogs folder
for cog in os.listdir('cogs/'):
    if cog.endswith('.py'):
        exts.append("cogs." + cog[:-3])


class Tools:
    get = discord.utils.get
    find = discord.utils.find
    MethType = types.MethodType
    get_exc = get_exc


class Context(commands.Context):
    def __init__(self, **attrs):
        super().__init__(**attrs)
        self.errors = excepts
        self.tools = Tools


class BotMeta(type):
    def __new__(cls, name, bases, dict_, **kwargs):
        bot = super().__new__(cls, name, bases, dict_)
        bot.__inline_commands__ = []

        for name in dir(bot):
            value = getattr(bot, name)
            if isinstance(value, commands.Command):

                value.callback = cls.wrapper(bot, value)
                value.params.popitem(last=False)

                setattr(bot, name, value)
                bot.__inline_commands__.append(value)

        bot.__inline_kwargs__ = kwargs
        return bot

    def wrapper(self, value):
        callback = copy.copy(value.callback)

        @wraps(value.callback)
        def custom_callback(*args, **kwargs):
            return callback(self, *args, **kwargs)
        return custom_callback


class BotMixin(commands.Bot, metaclass=BotMeta):
    initialize = True
    MODE = os.getenv('MODE')
    FILES = {BOTSETFILE: "botsets", LASTWRDFILE: "lastwrds", SETFILE: "sets", WARNFILE: "warns", STRFILE: "strs", TAGFILE: "tags", RANKFILE: "ranks"}
    db = {}

    def __init__(self):
        super().__init__(**self.__inline_kwargs__)
        self.remove_command('help')
        self._inject()

    def _inject(self):
        for command in self.__inline_commands__:
            self.add_command(command)

    async def fsync(self, file, name):
        """Sync configs/db to file."""
        if self.initialize:
            if file.endswith(".json"):
                self.db[name] = json.load(open(file, 'r'))
            if file.endswith(".db"):
                self.db[name] = await aiosqlite.connect(file)
            return
        if file.endswith(".json"):
            db_new = json.load(open(file, 'r'))
            db_new.update(self.db[name])
            self.db[name] = db_new
            json.dump(self.db[name], open(file, 'w'))
        if file.endswith(".db"):
            await self.db[name].commit()

    @tasks.loop(minutes=1)
    async def fsyncs(self):
        """Task: Sync all files."""
        to_do_coro = []
        for file in self.FILES:
            name = self.FILES[file]
            to_do_coro.append(self.fsync(file, name))
        await asyncio.gather(*to_do_coro)

    @staticmethod
    def get_cmd_patch(name, cmd_list):
        name = name.lower()
        char_cor = 0  # number of right chars
        last_gud_cmd = None
        ambiguous = []
        for cmd_name, cmd in cmd_list.items():
            if name == cmd_name:  # exact match after all...
                return cmd
            if len(name) > len(cmd_name):
                continue
            cor_count = 0
            for i, c in enumerate(name):
                valid = False  # not valid means end of loop or unmatch
                try:
                    if c == cmd_name[i]:
                        cor_count += 1
                        valid = True
                except IndexError:
                    break  # search query longer than command name
                # unmatch
                if len(name) == i + 1:  # end of loop
                    valid = False
                if (cor_count < char_cor or cor_count == 0) and not valid:
                    break  # smaller than the record bai
                if cor_count == char_cor and cor_count != 0 and not valid:
                    # the trip ended here, we got two matching commands
                    if any(ambiguous):  # the list is not blank
                        ambiguous.append(cmd_name)
                        continue
                    ambiguous = [last_gud_cmd.name, cmd_name]
                if cor_count > char_cor:
                    # why both valid and not valid: if this is end of loop the cmd will be recorded
                    last_gud_cmd = cmd
                    char_cor = cor_count
                    ambiguous = []  # longer than the old record, the ambiguous ones are shorter kara reset
                if not valid:
                    continue
        if any(ambiguous):
            warnings.warn(f"Ambiguous command search '{name}' -- {', '.join(ambiguous)}", excepts.CmdSearchWarning)
            return None
        return last_gud_cmd

    def get_command(self, name_s, last_gud=False):  # allow shorterned commands (SAP)
        if ' ' not in name_s:
            return self.get_cmd_patch(name_s, self.all_commands)

        names = name_s.split()
        if not names:
            return None
        obj = self.get_cmd_patch(names[0], self.all_commands)
        if not isinstance(obj, commands.GroupMixin):
            return obj

        for name in names[1:]:
            new = None
            try:
                new = self.get_cmd_patch(name, obj.all_commands)
            except AttributeError:
                return obj
            if new is None:
                if not last_gud:
                    warnings.warn(f"{name} is not in {obj.name}.", excepts.BadSubcommand)
                    return None
                return obj
            obj = new
        return obj

    async def get_context(self, message: discord.Message, *, cls=Context):
        view = commands.view.StringView(message.content)
        ctx = cls(prefix=None, view=view, bot=self, message=message)

        if self._skip_check(message.author.id, self.user.id):
            return ctx

        prefix = await self.get_prefix(message)
        invoked_prefix = prefix

        if isinstance(prefix, str):
            if not view.skip_string(prefix):
                return ctx
        else:
            # if the context class' __init__ consumes something from the view this
            # will be wrong.  That seems unreasonable though.
            if message.content.startswith(tuple(prefix)):
                invoked_prefix = discord.utils.find(view.skip_string, prefix)
            else:
                return ctx

        # invoker = self.get_command(view.get_word())
        # if invoker is not None:
            # invoker = invoker.qualified_name
        invoker = view.get_word()
        ctx.invoked_with = invoker
        ctx.prefix = invoked_prefix
        # ctx.command = self.get_command(message.content[len(ctx.prefix):], last_gud=True)
        ctx.command = self.get_command(invoker, last_gud=True)
        return ctx


class Bot(BotMixin, command_prefix=get_prefix, description="an awesome open source discord bot coded in python", owner_id=653086042752286730, case_insensitive=True, intents=discord.Intents.all()):
    """
    Class for Merlin Bot client.

    subset of commands.Bot
    Commands included.
    """
    netLogger: Log
    chatting: None
    async def __aenter__(self):
        """Basically    `async with bot:`."""
        root_logger.info("Starting tasks")
        self.fsyncs.start()  # pylint: disable=no-member
        self.netLogger = Log(self)

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        with contextlib.suppress(BaseException):
            print("Merlin is cleaning up...")
            for file, name in self.FILES.items():
                if file.endswith(".json"):
                    db_new = json.load(open(file, 'r'))
                    self.db[name].update(db_new)
                    json.dump(self.db[name], open(file, 'w'))
                if file.endswith(".db"):
                    asyncio.get_event_loop().create_task(self.db[name].close())
        self.chatting.stopChatTh()

    async def on_ready(self):
        """Bot is (back) online."""
        root_logger.info(f'Logged in as {style.cyan}{self.user.name}{style.reset} - {style.italic}{self.user.id}{style.reset} in {style.magenta}{self.MODE} mode')
        self.initialize = False
        root_logger.info('Loading Extensions...')
        for extension in exts:
            print(end=f' >> \tLoading {extension}...\r')
            try:
                self.load_extension(extension)
                root_logger.hint(style.green2 + f"Loaded: {extension}" + style.reset + "   ")
            except commands.errors.ExtensionAlreadyLoaded:
                return root_logger.hint("Loaded tasks already, continue execution.")
            except Exception as err:
                root_logger.error(f"FAILED: {extension}{style.grey} - {style.yellow}{traceback.format_exception_only(err.__class__, err)[0]}")
                root_logger.debug('Stack: ', exc_info=True)
        root_logger.hint('Telling guilds...')
        if not self.MODE or self.MODE == 'NORMAL':
            await self.change_presence(status=discord.Status.online, activity=discord.Game(name=random.choice(STATUSES)))
            await self.netLogger('Logged in!')
        elif self.MODE == 'DEBUG':
            await self.change_presence(status=discord.Status.idle)
            await self.netLogger('RUNNING IN **DEBUG** MODE!')
        elif self.MODE == 'FIX':
            await self.change_presence(status=discord.Status.dnd)
            await self.netLogger('*RUNNING IN EMERGENCY **FIX** MODE!')
        root_logger.info(style.bold + "Ready!")
        return 0

    @commands.command(name='eval', help='it is eval', hidden=True)
    @commands.is_owner()
    async def _eval(self, ctx, *, code='"bruh wat to eval"'):
        try:
            bot = ctx.bot
            await ctx.send(eval(code))
            await ctx.message.add_reaction('✅')
        except Exception:
            await asyncio.gather(
                ctx.message.add_reaction(ctx.bot.get_emoji(740034702743830549)),
                ctx.send(':x: uh oh. there\'s an error in your code:\n```\n' + traceback.format_exc() + '\n```')
            )

    @commands.command(name='exec', help='Execute python', hidden=True)
    @commands.is_owner()
    async def _exec(self, ctx, *, code='return "???????"'):
        try:
            bot = ctx.bot
            exec(code, globals(), locals())
            await ctx.message.add_reaction("✅")
        except Exception:
            await asyncio.gather(
                ctx.message.add_reaction(ctx.bot.get_emoji(740034702743830549)),
                ctx.send(':x: uh oh. there\'s an error in your code:\n```\n' + traceback.format_exc() + '\n```')
            )

    @commands.command(name='reload', help='reload a cog', hidden=True)
    @commands.is_owner()
    async def _reload(self, ctx, module: str):
        ctx.bot.reload_extension(module)
        await ctx.message.add_reaction("✅")

    @commands.command(name='unload', help='unload a cog', hidden=True)
    @commands.is_owner()
    async def _unload(self, ctx, module: str):
        ctx.bot.unload_extension(module)
        await ctx.message.add_reaction("✅")

    @commands.command(name='load', help='load a cog', hidden=True)
    @commands.is_owner()
    async def _load(self, ctx, module: str):
        ctx.bot.load_extension(module)
        await ctx.message.add_reaction("✅")
