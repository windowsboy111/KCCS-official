import warnings
class NoMutedRole(Exception):
    """Muted role not found in the guild"""
    def __init__(self, msg):
        super.__init__(super(str, msg))
        self.message = msg
        self.msg = msg

    def __str__(self):
        return self.msg

    def __repr__(self):
        return {'error': NoMutedRole, 'msg': self.msg}

class NotMod(Exception):
    """You are not moderator / administrator of a guild"""
    def __init__(self, msg):
        super.__init__(super(str, msg))
        self.message = msg
        self.msg = msg

    def __str__(self):
        return self.msg

    def __repr__(self):
        return {'error': NotMod, 'msg': self.msg}

class CmdSearchWarning(Warning):
    """Base class for warnings in command searching."""
    pass
class AmbiguousSearchQuery(CmdSearchWarning):
    """Search is ambiguous."""
    pass
class BadSubcommand(CmdSearchWarning):
    """Cannot find the corresponding subcommand for the query."""
    pass

class HaltInvoke(Exception):
    """Stop a command from invoking. No error messages will be displayed."""
    def __init__(self, msg):
        super().__init__()
        self.msg = msg
