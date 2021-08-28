import json
import aiosqlite


BOTSETFILE = "ext/bot_settings.json"
LASTWRDFILE = "data/lastword.json"
WARNFILE = "data/warnings.db"
STRFILE = "ext/wrds.json"
BOTSETFILE = "ext/bot_settings.json"
TAGFILE = "data/tags.db"
RANKFILE = "data/rank.db"
STATFILE = "data/statuses.txt"


class BaseDB:
    name: str
    path: str
    desc: str


class DynDB(BaseDB):
    data: dict

    def __init__(self, storage):
        self.data = storage

    def _at_get(self, keys, sep: str, fill_blank=False):
        default = self.data["default"] if fill_blank else {}
        with contextlib.suppress(KeyError):
            keys = keys.split(sep)
            obj = self.data[keys.pop()]
            for key in keys:
                try:
                    default = default[int(key)]
                    obj = obj.get(int(key), default)
                except (ValueError, KeyError, IndexError):
                    default = default[key]
                    obj = obj.get(key, default)
            return obj
        return None

    def default(self, keys: str = "", separator: str = "."):
        """
        Get the default configurations.
        """
        return self._at_get(keys, separator)

    def get(
        self,
        guild: typing.Union[discord.Guild, int],
        keys: str = "",
        separator: str = ".",
    ):
        """
        Get the data of a guild configurations.

        Examples
        ---
        ```py
        ret = sett.get(ctx.guild.id)
        ret = sett.get(ctx.guild)
        ret = sett.get(ctx.guild, "cmdHdl.quiet")
        ret = sett.get(ctx.guild, "prefix/0", separator="/")
        ```
        """
        return self._at_get(keys, separator, True)

    def assign(
        self,
        guild: typing.Union[discord.Guild, int],
        keys: str,
        value: typing.Union[
            discord.Guild,
            discord.User,
            discord.ChannelType,
            int,
            str,
            list,
            dict,
        ],
        separator: str = ".",
    ):
        base = self.get(guild, separator=separator)
        keys = keys.split(separator)
        base = self._assign(base, keys, value)

    def _assign(self, base, keys: list, val):
        if any(keys):
            key = keys.pop()
            base[key] = self._assign(base[key], keys, val)
            return base
        return val


class JsonDB(DynDB):
    def __init__(self, path: str, desc: str):
        self.name = path.split("/")[-1].split(".")[0]
        self.path = path
        self.desc = desc
        super().__init__(json.load(open(path, 'r')))

class Databases:
    settings = JsonDB("data/settings.json")
