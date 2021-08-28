"""Types used in Merlin."""
import sys
import types
import traceback
import dataclasses
import discord
from discord.ext import commands as cmds
from modules import excepts


class HashableDict(dict):
    def __hash__(self):
        return hash(tuple(self.items()))


class HashableList(list):
    def __hash__(self):
        return hash(tuple(self))


@dataclasses.dataclass(frozen=True)
class CmdRes:
    cmd: discord.ext.commands.Command
    query: str
    candidates: set = dataclasses.field(default_factory=set)


class Tools:
    get = discord.utils.get
    find = discord.utils.find
    MethType = types.MethodType

    @staticmethod
    def get_exc(err):
        return "".join(
            traceback.format_exception(err.__class__, err, err.__traceback__)
        )

    @staticmethod
    def wrdssep(string, count):
        return [string[i : i + count] for i in range(0, len(string), count)]


class Context(cmds.Context):
    pipe: bool

    def __init__(self, **attrs):
        super().__init__(**attrs)
        self.errors = excepts
        self.tools = Tools


class TestMessage(discord.Message):
    def __init__(self, **attrs):
        pass


class MerlinCommand(cmds.Command):
    def __init__(self, **attrs):
        super().__init__(**attrs)

    @classmethod
    def convert(cls, cmd, **newattrs):
        return cls(**cmd.attrs, **newattrs)
