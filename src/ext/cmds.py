"""Stuff abt commands."""
import merlin


def cli(*, showfmt: int = 0):
    """
    Decorator.
    Makes a command runnable in pipe systems.
    ---
    # kwargs:
    ## showfmt
    **0: no output format**
    1: `output like so`
    2: ```output like so```
    """
    def inner(fn):
        async def decorate(ctx: merlin.tools.dt.Context, *cmdargs, **cmdkws):
            ret = await fn(ctx, *cmdargs, **cmdkws)
            if not showfmt:
                return await ctx.send(ret)
            if showfmt is 1:
                return await ctx.send(f"`{ret}`")
            if showfmt is 2:
                return await ctx.send(f"```{ret}```")
        return decorate
    return inner
