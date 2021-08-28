import sys
import types
import logging
from datetime import datetime
from modules.consolemod import style
HINT = 15
logging.addLevelName(HINT, "HINT")
def hint(self, message, *args, **kws):
    """Hint logging level"""
    if self.isEnabledFor(HINT):
        # Yes, logger takes its '*args' as 'args'.
        self._log(HINT, message, args, **kws)
c_handler = logging.StreamHandler(sys.stdout)
f_handler = logging.FileHandler(datetime.utcnow().strftime("../logs/%Y-%m-%d_%H-%M.log"), 'a', 'utf-8')
c_handler.setLevel(15)
f_handler.setLevel(5)

def fFilter(record: logging.LogRecord):
    if record.levelno is logging.DEBUG and record.getMessage().startswith("Dispatching event "):
        return False
    return True

class cFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord):
        record.message = record.getMessage()
        colour = style.grey  # HINT
        if record.levelno is logging.INFO:
            colour = style.blue2
        elif record.levelno is logging.WARN:
            colour = style.yellow
        elif record.levelno is logging.ERROR:
            colour = style.orange
        elif record.levelno is logging.CRITICAL:
            colour = style.red2
        startchar = "\r==> " if record.levelno is logging.INFO else " >> " if record.levelno is HINT else None
        s = f"{style.cyan}{startchar or record.levelname.replace('CRITICAL', 'FATAL')}\t{style.white}{record.name}: {colour}{record.message}"
        if record.exc_info:
            # Cache the traceback text to avoid converting it multiple times
            # (it's constant anyway)
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)
        if record.exc_text:
            if s[-1:] != "\n":
                s = s + "\n"
            s = s + record.exc_text
        if record.stack_info:
            if s[-1:] != "\n":
                s = s + "\n"
            s = s + self.formatStack(record.stack_info)
        return s + style.end


c_format = cFormatter()
f_format = logging.Formatter('%(asctime)s\t%(name)s\t%(levelname)s: %(message)s')
c_handler.setFormatter(c_format)
f_handler.setFormatter(f_format)
f_handler.addFilter(fFilter)


def gLogr(*names: str):
    res = []
    for name in names:
        new_logger = logging.getLogger(name)
        if len(new_logger.handlers) < 2:
            new_logger.setLevel(1)
            new_logger.addHandler(f_handler)
            new_logger.addHandler(c_handler)
            new_logger.hint = types.MethodType(hint, new_logger)
        res.append(new_logger)
    if len(res) == 1:
        return res[0]
    return res

get_logger = gLogr
discord_client_logger = gLogr('discord.client')  # hidden by default?

__all__ = ["gLogr", "HINT", "get_logger"]
