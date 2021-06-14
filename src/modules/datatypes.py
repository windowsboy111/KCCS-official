"""Types used in Merlin."""
import sys
import types
import traceback
import dataclasses
import discord
from ext import excepts

class Context(discord.ext.commands.Context):
    pipe: bool
    def __init__(self, **attrs):
        super().__init__(**attrs)
        self.errors = excepts
        self.tools = Tools

class CmdDict(dict):
    def __hash__(self):
        return hash(frozenset(self.items()))

@dataclasses.dataclass(frozen=True)
class CmdRes:
    cmd: discord.ext.commands.Command
    query: str
    candidates: set = dataclasses.field(default_factory=set)

class Tools:
    get = discord.utils.get
    find = discord.utils.find
    MethType = types.MethodType
    get_exc = lambda err: "".join(traceback.format_exception(err.__class__, err, sys.exc_info()[2]))
    wrdssep = lambda string, count: [string[i:i+count] for i in range(0, len(string), count)]
