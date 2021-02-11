# Merlin discord.py bot
> windowsboy111


## [Unreleased]
### Fixed
- non-sodoers can change settings

## [3.0-b1]
### Changed
- Are you in the sudoers file?
### Fixed
- failed to load cogs/utils
- failed netLogger
- settings sometimes does not update after modification

## [3.0-b] - 2020-02-01
### Added
- subcls bot
- ranking system
- `/id` command
- optimized response generating for the chat module (multiprocessing)
- optimized messages processing in `on_message()` (async parallel)
- optimized merlin-py logging (async parallel)
- optimized cmderrhdl (async nowait / tasks)
- SAP (smart abbreviating prompt)
- optimized db accessing (async and auto commit)
- settings for chat channel, muted role, announcement channel, ranking toggle, sudoers are in snowflake (some are new)
### Changed
- `/res` now looks much better
- using aiosqlite
- better logging system
- better help commands
- moved some core stuff to GLOBAL
- better `/settings` (`/configure`)
### Removed
- `log()` no longer supports `guild_id` param
- startup script
### Fixed
- #30: Broken `/poll check`
- `/info member` fails when member has no roles
- chat system doesn't work
- broken `/mc srv`
- polls with less than 20 options can now also be tallied
- will now fill settings for missing guild
- chat system couldn't learn prev msg correctly
- `/info channel` wouldn't work when there are invites

## [3.0-a] - 2020-09-11
### Added
- better chat system by allowing the bot to read other chats from other channels when `/settings cmdhdl improveExp` is 1
- fs organization
- chatterbot-corpus is a requirement
- setup script
- added customization for `on_message`
- error messages when user is not a mod and the user runs commands that requires being a mod
- warnings are now stored for each server
- added choice for enabling deleting issue cmd `/settings cmdhdl delIssue`
### Changed
- `/reload` now requires full path and can access `ext`
- when add moderators embed will now be outputed instead
### Removed
- update command
### Fixed
- core cog settings not updated (might fix a bug where running `/settings` will keep "fixing" it)
- can force terminate now
- settings didn't work when there are no prefix except mentioning
- `/settings cmdhdl` now works
- typos

## [2.2.1] - 2020-09-01
### Added
- code organization
- games
- diagnose script in ext/init
- emoji command to peek emojis from other servers
- tutorial command
### Removed
- since removing issue command affect specific features, issue command will be left
### Fixed
- help command now identifies optional params correctly

## [2.2.0] - 2020-08-16
### Added
- some commands now contains multi-line help messages
- help command now supports multi-line help messages
- bot now tries to stop webserver if start with main script
- search command
- error messages when one don't have perms to issue a command
### Changed
- help command now gets more features
### Removed
- `/msgstats`
### Fixed
- if exit not properly, will try to restart
- lastword didn't work when join new server

## [2.2-b1] - 2020-08-08
### Added
- if options for `/poll create` is less than 2 then it will fall back to yes and no
### Removed
- spamming detection system
- member welcoming and bot setup, cuz they are annoying tbh with you, and they are optional for the bot to work
### Fixed
- `/poll create` now shows mentions properly
- Pypi upload is now markdown
- `/quote` command

## [2.2-b] - 2020-08-04
### Added
- more visual changes
### Fixed
- will use 1 space after a full stop as microsoft word now treats 2 spaces after a full stop as an error

## [2.2-a] - 2020-07-29
### Added
- detailed invite command
- ping command using embed
- little lock :x: emoji for notOwner handle
- better handling for CommandDisabled
### Changed
- command handling command invoke error now uses embed and added link to github new bug issue
### Fixed
- removed print message content

## [2.1.5] - 2020-08-04
### Added
- now using setuptools in `setup.py` and added install requires
- when restart / shutdown it will auto-save changes
- now by default it will not say that command not found
### Optimized
- compressed bot.py
### Fixed
- the bot mention prefix is now dynamic
- auto create lastmsg file when it does not exist

## [2.1.4] - 2020-08-02
### Added
- better discord status
- .gitignore added user data stuff
### Optimized
- chat system now uses multiprocessing
- startup on_ready now omit "loaded extension" double logging
### Removed
- poetry.lock
- pyproject.toml
### Fixed
- dm commands now work
- #22: `/poll end all` will not crash when there are no unended polls
- #23
- mention of Merlin was not prefix

## [2.1.3] - 2020-07-31
### Added
- chat system
- `__init__.py` (as a package)
- print statements in `bot_imports.py` (prevent PEP8 violation)
- updated packages

## [2.1.2] - 2020-07-29
### Added
- README.md badges
- nightly branch
### Changed
- in detailed `/ping` command
### Fixed
- `/help` command did not work with commands that does not have aliases
- removed print message content
- `/unban` command now will unban the last member banned if no argument is inputted

## [2.1.1] - 2020-07-29
### Added
- `/avatar` command
- `/res` command to see CPU / RAM usages
- `/info user`, `/info member`, `/info channel`
- `/help` command now shows command aliases
### Changed
- `/sandbox` command now belongs to cog debug
### Fixed
- now only can use invite in guild
- no attribute hint
- stage is now stable
- member dm welcome
- spam detecion system now won't crash randomly cannot delete the message
- `@Merlin` prefix now works

## [2.1.0] - 2020-07-26
### Added
- hint logging level
- added description for bot_settings, also changed the description for imports_share
- sandbox command
- more pypi classifiers
### Changed
- consolemod styles are now str, not function
- help command now if have sub-command will have details

## [2.1-b3] - 2020-07-26
### Added
- error message will split out if restarting the bot failed
- if fail to import extension when bot starts, bot treat start as a reconnect
- build number for bot info
- better look for `/info bot`
- `/kick`, `/ban` will now put reason into discord.py
- `/mute` command now checks if a Muted role exists
- owner is always "sudoers" in guild
- owner check is now handled
- it now checks if it can run inside DMs / PMs
- stdout now logs user issuing commands with prefix `[CMDHDL]\t`
- track last message from a user with `/quote`
- `is_sudoers()` moved to imports_share and new `@chk_sudo()`
### Changed
- Dynamic welcome message
- group `/mc` is now cog `utils`
- `invite me` command now moved to `/invite`
### Removed
- `/nickname` command
### Fixed
- kick commands, those kinds of things do not work
- keep alive func [FATAL]
- a lot of bugs when merging git :/ [FATAL]
- help command will not show hidden commands when wd is `<GLOBAL>`
- couldn't use commands via dm
- it shows that it is in loop with stdout even the loop does not exist in the first place

## [2.1-b2] - 2020-07-20
### Added
- descriptions for many things (see them with `help()`)
- now a module
### Fixed
- mute command might break

## [2.1-b1] - 2020-07-15
### Added
- \*load commands now accept command name as argument
- can run Merlin-py as a module
- message when bot joins a guild (being invited)
- detailed `/msgstats` command
- `/info` command
- `/mute` command
- string table (actually json) `ext/wrds.json`
- can now run `/check` without specifying the amount of messages to read (the feature that has been removed in [2.1-a2])
### Removed
- excessive python syntax, imports, f-strings, etc (code formatting)
### Changed
- `/ping` and `/msgstats` are both now in `Debug` cog instead of `Utils`
- `man` cog has been renamed to `mod`
### Fixed
- `/help` command completed
- failed to import `find()` from `imports_init`
- PEP code formatting
- fs reorganizing
- cannot remove warnings
- some grammar issues

## [2.1-b] - 2020-07-09
### Added
- can now hide commands in `/help`
- logging console
- debug / fix mode
- ability to unload, reload and load commands (owner only)
- new warning system that replace the old one and have less security issues
- command error handler
- `.gitignore`
### Changed
- rearranged the repo fs
### Removed
- not working `/emojis` command
- `easteregg.py` will no longer presents in the repo
### Fixed
- preventing the bot from deleting every messages starting with the prefix (the one in [2.1-a2] does not work)
- Duplicated logging what users have issued (especially in the fun cog)

## [2.1-a2] - 2020-07-05
### Added
- allowing users to end all polls in a channel with `/poll end all` (buggy)
- compressed spamming warning system, boosted performance
- compressed bot.py
- bot owner can now run `/eval` python expressions.
### Changed
- compressed the code for a bit without losing readability and performance
- QuickPoll now have special return code representing different errors
- the python shell will now print out the whole traceback
### Removed
- ability for not specifying the amount of messages to read for `/poll check`
- the `/table` command
### Fixed
- check polls might compare str with int
- ~~preventing the bot from deleting every messages starting with `/` (which is the prefix)~~
- bot might read its own error messages in the python debugging channel

## [2.1-a1] - 2020-07-02
### Added
- allowing users to add custom shortcuts for `/mc srv`
- allowing moderators to add `"`s in warnings reasons
### Changed
- Changelogs
### Removed
- sudo mode (moderating)

## [2.1-a] - 2020-06-22
### Added
- Karma system integrated with [Merlin-js]
- more fun commands
### Fixed
- quick poll has runtime error without error messages for the discord users

## [2.0.0]
### Changed
- bot is finally public on github
- optimized
### Removed
- no more verbose mode :O


[Unreleased]:   https://github.com/windowsboy111/Merlin-py/compare/3.0-b1...HEAD
[3.0.b1]:       https://github.com/windowsboy111/Merlin-py/compare/3.0.b...3.0.b1
[3.0-b]:        https://github.com/windowsboy111/Merlin-py/compare/3.0-a...3.0-b
[3.0-a]:        https://github.com/windowsboy111/Merlin-py/compare/2.2.1...3.0-a
[2.2.1]:        https://github.com/windowsboy111/Merlin-py/compare/2.2.0...2.2.1
[2.2.0]:        https://github.com/windowsboy111/Merlin-py/compare/2.2-b1...2.2.0
[2.2-b1]:       https://github.com/windowsboy111/Merlin-py/compare/2.2-b...2.2-b1
[2.2-b]:        https://github.com/windowsboy111/Merlin-py/compare/2.2.a...2.2-b
[2.2-a]:        https://github.com/windowsboy111/Merlin-py/compare/2.1.5...2.2-a
[2.1.5]:        https://github.com/windowsboy111/Merlin-py/compare/2.1.4...2.1.5
[2.1.4]:        https://github.com/windowsboy111/Merlin-py/compare/2.1.3...2.1.4
[2.1.3]:        https://github.com/windowsboy111/Merlin-py/compare/2.1.2...2.1.3
[2.1.2]:        https://github.com/windowsboy111/Merlin-py/compare/2.1.1...2.1.2
[2.1.1]:        https://github.com/windowsboy111/Merlin-py/compare/r2.1.0...2.1.1
[2.1.0]:        https://github.com/windowsboy111/Merlin-py/compare/2.1-b3...r2.1.0
[2.1-b3]:       https://github.com/windowsboy111/Merlin-py/compare/2.1-b2...2.1-b3
[2.1-b2]:       https://github.com/windowsboy111/Merlin-py/compare/2.1-b1...2.1-b2
[2.1-b1]:       https://github.com/windowsboy111/Merlin-py/compare/2.1-b...2.1-b1
[2.1-b]:        https://github.com/windowsboy111/Merlin-py/compare/2.1-a2...2.1-b
[2.1-a2]:       https://github.com/windowsboy111/Merlin-py/compare/2.1-a1...2.1-a2
[2.1-a1]:       https://github.com/windowsboy111/Merlin-py/compare/2.1a...2.1-a1
[2.1-a]:        https://github.com/windowsboy111/Merlin-py/compare/2.0.0...2.1a
