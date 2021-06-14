def position(line, column):
    """Move cursor to specified position"""
    print(f"\033[{line};{column}f")


def up(lines):
    """Move cursor up specified number of lines"""
    print(f"\033[{lines}A")


def down(lines):
    """Move cursor down specified number of lines"""
    print(f"\033[{lines}B")


def left(columns):
    """Move cursor left specified number of columns"""
    print(f"\033[{columns}C")


def right(columns):
    """Move cursor right specified number of columns"""
    print(f"\033[{columns}D")


def cls():
    """Clears the screen, and move cursor to 0,0"""
    print("\033[2J")


def eraseline():
    """Erase the whole line (till the end of line)"""
    print("\033[2K")


def savepos():
    """Save current cursor position"""
    print("\033[s")


def restorepos():
    """Restore the saved cursor position"""
    print("\033[u")


def get_fg_color(r, g, b):
    return f"\033[38;2;{r};{g};{b}m"

class style:
    reset      = '\33[0m'
    end        = '\33[0m'
    bold       = '\33[1m'
    italic     = '\33[3m'
    url        = '\33[4m'
    underline  = '\33[4m'
    blink      = '\33[5m'
    blink2     = '\33[6m'
    selected   = '\33[7m'

    black      = '\33[30m'
    red        = '\33[31m'
    green      = '\33[32m'
    yellow     = '\33[33m'
    blue       = '\33[34m'
    violet     = '\33[35m'
    magenta    = '\33[35m'
    cyan       = '\33[36m'
    white      = '\33[37m'

    blackbg    = '\33[40m'
    redbg      = '\33[41m'
    greenbg    = '\33[42m'
    yellowbg   = '\33[43m'
    bluebg     = '\33[44m'
    violetbg   = '\33[45m'
    beigebg    = '\33[46m'
    whitebg    = '\33[47m'

    grey       = '\33[90m'
    red2       = '\33[91m'
    green2     = '\33[92m'
    yellow2    = '\33[93m'
    blue2      = '\33[94m'
    violet2    = '\33[95m'
    beige2     = '\33[96m'
    white2     = '\33[97m'

    greybg     = '\33[100m'
    redbg2     = '\33[101m'
    greenbg2   = '\33[102m'
    yellowbg2  = '\33[103m'
    bluebg2    = '\33[104m'
    violetbg2  = '\33[105m'
    beigebg2   = '\33[106m'
    whitebg2   = '\33[107m'

    orange     = '\33[38;2;255;135;0m'
