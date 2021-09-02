# Merlin
### discord bot coded with discord.py

(discord.py is unsupported, will be ported to guilded.py)
Discord: (to be changed)
Invite using [this link](https://discord.com/api/oauth2/authorize?client_id=690839099648638977&permissions=8&scope=bot).

LICENSE: MIT

---

## Setup
1. Optional: Make a venv and activate it
2. Execute `pip install -r requirements.txt`
3. Execute `inv build`
    - C++ compiler by default is g++
    - feel free to change stuff in `tasks.py`
    - you might need to build `extern/pybind11/`, run `setup.py install` there
4. Edit `src/special.py`, make sure
    - coroutine `pre_on_message(message: discord.Message)`
    - coroutine `post_on_message(message: discord.Message)`

    are both defined
5. Edit `src/.env` according to `src/.example.env`
    - `MERLIN_EMAIL` and `MERLIN_PASSWORD` should be apparent
    - `MODE` is either `NORMAL`, `DEBUG` or `FIX`
    - quotes are not needed
    - you may use `#` to create comments

## Start
- make sure the current directory is `src/`
- execute `python bot.py`
