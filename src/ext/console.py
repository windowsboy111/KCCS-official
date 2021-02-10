import sys
from modules.consolemod import style
import asyncio
from merlin import Bot, get_exc
import traceback
from concurrent.futures import ThreadPoolExecutor

async def ainput(prompt: str = "") -> str:
    with ThreadPoolExecutor(1, "AsyncInput") as executor:
        return await asyncio.get_event_loop().run_in_executor(executor, input, prompt)

commands = {}

async def console(bot):
    ret = ""
    while True:
        if ret:
            if ret == -1:
                break
            print(end=style.yellow + str(ret) + style.reset + " ")
        input_cmd = await ainput("> ") + ' '
        cmd = input_cmd.split()[0]
        args = input_cmd.split()[1:]
        if cmd in commands:
            try:
                if args == ['']:
                    ret = await commands[cmd](bot)
                ret = await commands[cmd](bot, *args)
            except Exception as error:
                print(f"{style.red}{get_exc(error)}{style.reset}", file=sys.stderr)
        else:
            print("Command not found.")
            ret = -2

def setc(name="", *, aliases=[]):
    def decorate(coro):
        commands[name or coro.__name__] = coro
        for alias in aliases:
            commands[alias] = coro
    return decorate

def setup(bot: Bot):
    bot.loop.create_task(console(bot))


@setc()
async def test(bot: Bot, *args):
    print(args)
    return 0

@setc(aliases=['shutdown', 'bye'])
async def halt(bot: Bot, *args):
    if '--now' not in args:
        print("Prompting servers (10 secs)")
        await asyncio.gather(bot.netLogger("Bot will shutdown in 10 secs!"),asyncio.sleep(10))
        bot.chatting.stopChatTh()
    await bot.netLogger("Logging out...")
    print("Bye bye.")
    await bot.close()
    return -1

@setc(name="exec")
async def _exec(bot: Bot, *args):
    try:
        exec(" ".join(args), globals(), locals())
    except Exception as error:
        print(f"{style.red}{get_exc(error)}{style.reset}", file=sys.stderr)
        return 2
    return 0

@setc(name="log")
async def cmd_log(bot: Bot, *args):
    if not bot.is_ready():
        print("Bot is not ready. (gotta wait for the internal cache!)")
        return 2
    if args[0] == "--guild":
        g_id = args[1]
        await bot.netLogger(" ".join(args[2:]), guild=bot.get_guild(g_id))
        return 0
    await bot.netLogger(" ".join(args))
    print("Okay")
    return 0
