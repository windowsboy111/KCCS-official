"""
Copyright 2020 windowsboy111  
LICENSE: MIT  
This file / script is part of the Merlin-bot project,  
you can check it out at both [pypi](https://pypi.org/project/Merlin-bot) and [github](https://github.com/windowsboy111/Merlin-py).
---
This library is responsible for fetching minecraft info. in Merlin, it is equivilant to the `/mc srv` command.  
This is neither a discord.py cog or a discord.py extension. It is only a normal python module.
"""
from mcstatus import MinecraftServer
import discord, csv
from ext.logcfg import get_logger
from pyTableMaker import ModernTable


# constant variables!!!
mcserverarglist = ["srv", "server"]  # The args you type in order to indicate you wanna get minecraft servers info
logger = get_logger('MCraft')


# user-defined exceptions
class Error(Exception):
    """Base class for other exceptions"""
    pass


class InvalidArgument(Error):
    """Argument passed from the command line is invalid"""
    pass


class OfflineServer(Error):
    """The specified minecraft server has been detected as offline"""
    pass


def mcsrv(embed, args):
    logger.info("Started botmc.mcsrv()")
    rtrn = ""
    global mcserverarglist  # chk srv arg
    global tmp
    if args:
        logger.info("2nd argument detected, searching for same srv_id for override...")
        link = name = note = ''
        with open('data/mcsrvs.csv', mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file, fieldnames=['link', 'name', 'note'])
            for row in csv_reader:
                if args in (row['name'], row['link']):
                    link = row['link']
                    name = row['name']
                    note = row['note']
                    break
        if link == '':
            logger.info("Not a defined server, will treat 2nd argument as a server link and name.")
            link = args
            name = args
            note = "unknown server :/"
        try:
            tmp = MinecraftServer.lookup(link).status()
            status = "online"
            players = str(tmp.players.online) + "/" + str(tmp.players.max)
            ping = tmp.latency
        except OSError as e:
            status = 'offline'
            logger.warn('Getting error "{}" while trying to detect if server is online, treat server as an offline server.'.format(str(e)))
            raise OfflineServer("Server {} (link {}) has been detected as offline.".format(name, link)) from e
        try:
            if tmp.players.sample:
                playerls = ', '.join(p.name for p in tmp.players.sample)
            else:
                playerls = 'Unknown'
        except OSError as e:
            playerls = [str(e)]
            if status == "online":
                logger.warn('Getting error "{}" while trying to get ping even server is online, error ignored.'.format(str(e)))
        if tmp.description:
            dscrp = tmp.description
        else:
            dscrp = "No description / Unknown"
        if tmp.version.name:
            ver = tmp.version.name
        else:
            ver = "Unknown"
        embed = discord.Embed(title="Minecraft Servers", description="Here's da info", color=0x00b9ff)
        embed.add_field(name="Server name:",         value=name,         inline=True)
        embed.add_field(name="Server link:",         value=link,         inline=True)
        embed.add_field(name="Server status:",       value=status,       inline=True)
        embed.add_field(name="Server version:",      value=ver,          inline=True)
        embed.add_field(name="Note:",                value=note,         inline=True)
        embed.add_field(name="Latency (Ping):",      value=ping,         inline=True)
        embed.add_field(name="Number of players:",   value=players,      inline=True)
        embed.add_field(name="Players Online:",      value=playerls,     inline=True)
        embed.add_field(name="Description:",         value=dscrp,        inline=True)
        logger.info('Attempting to return obj "embed" from srv <id/link>')
        return embed
    return discord.Embed(title="Usage: /mc srv mc.hypixel.net", description="`/help mc srv` for more info ;3")
