from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer, ChatterBotCorpusTrainer
import chatterbot
import chatterbot.response_selection
import os, threading, asyncio
import time
import multiprocessing as mp
doTrain = False
reTrain = False
stop = False
from chatterbot.conversation import Statement
# more_label = None
# more_data = None
# if an error occurred try this: https://blog.csdn.net/qq_41185868/article/details/83758376

manager = mp.Manager()
queue = mp.Queue()

def make_bot():
    bot = ChatBot(
        'Merlin',
        storage_adapter='chatterbot.storage.SQLStorageAdapter',
        logic_adapters=[
            {
                "import_path":                  "chatterbot.logic.BestMatch",
                "statement_comparison_function":"chatterbot.comparisons.levenshtein_distance",
                "response_selection_method":    chatterbot.response_selection.get_random_response,
                'default_response':             'I am sorry, but I do not understand.',
                'maximum_similarity_threshold': 0.10
            },
            'chatterbot.logic.MathematicalEvaluation',
            {
                "import_path":  "chatterbot.logic.SpecificResponseAdapter",
                "input_text":   "print('Merlin is the best!')",
                "output_text":  "print('Congratulations! You found an Easter egg!')"
            }
        ],
        preprocessors=[
            'chatterbot.preprocessors.clean_whitespace'
        ],
        database_uri=f'sqlite:///{os.path.dirname(__file__)}/chats.sqlite3'
    )
    return bot


def train(bot: ChatBot):
    bot.set_trainer(ListTrainer)
    conversation = open(f'{os.path.dirname(__file__)}/chats.txt','r').readlines()
    bot.train(conversation)

    bot.set_trainer(ChatterBotCorpusTrainer)
    bot.train('chatterbot.corpus.english')
    return 0

bot = make_bot()
try:
    open(f'{os.path.dirname(__file__)}/chats.sqlite3').close()
except Exception:
    train(bot)


def proc_resp(bot, msg, res:dict):
    res['response'] = bot.get_response(msg.content)

async def response(discord_bot, msg):
    global doTrain, reTrain
    async with msg.channel.typing():
        if msg.content.startswith('merlin::'):
            if msg.content == 'merlin::train':
                doTrain = True
                return await msg.channel.send("bot is training, please wait for around a minute.")
            if msg.content.startswith('merlin::retrain'):
                reTrain = True
                return await msg.channel.send("Please wait...")
            return await msg.channel.send("`merlin::`?")
        res = manager.dict()
        p = mp.Process(target=proc_resp, args=(bot, msg, res), name='merlin-chat-response')
        p.start()
        while p.is_alive():
            await asyncio.sleep(0.2)
        p.join()
    await msg.channel.send(res['response'])


async def save(msg: str, prev: str):
    global saveBot
    msg = Statement(msg)
    prev = Statement(prev)
    try:
        saveBot.learn_response(msg, prev)
    except:
        saveBot = make_bot()
        saveBot.learn_response(msg, prev)


def init_train(bot: ChatBot):
    os.remove(f'{os.path.dirname(__file__)}/chats.sqlite3')
    bot = make_bot()
    p = mp.Process(target=train, args=(bot, ), name='Merlin chat retrain / reinit')
    p.start()


def loop():
    global doTrain, reTrain, bot, stop
    try:
        while not stop:
            if stop:
                return
            if doTrain:
                doTrain = False
                p = mp.Process(target=train, args=(bot, ), name='Merlin chat train')
                p.start()
            if reTrain:
                reTrain = False
                init_train(bot)
            time.sleep(0.5)
    except (KeyboardInterrupt, SystemExit):
        return

t = threading.Thread(target=loop)

def stopChatTh():
    global stop
    print("CLOSING chat Th")
    stop = True
    t.join()

class Chatting:
    response = response
    save = save
    th = t
    stopChatTh = stopChatTh

def setup(bot):
    bot.stopChatTh = stopChatTh
    bot.chatting = Chatting
    t.start()
