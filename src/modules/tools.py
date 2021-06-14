"""
This module contains tools that are neither related to discord.py nor Merlin
"""
import sys
import asyncio
import functools
import traceback
from modules import proc
from modules import datatypes as dt

class AsyncPool:
    def __init__(self, queue: asyncio.Queue = None):
        self.queue = queue or asyncio.Queue()
        self.tasks = []

    def make_worker(self, timeout: int = 10):
        """decorate functions that represents workers"""
        def inner(fn):
            async def wrap_wrk():
                slept = 0
                try:
                    while True:
                        if slept >= timeout:
                            return  # timeout
                        if self.queue.empty():
                            slept += 0.1
                            await asyncio.sleep(0.1)
                            continue
                        try:
                            await fn(await self.queue.get())  # execute original function
                        except asyncio.CancelledError:  # task cancelled
                            return
                        except Exception:  # print exc and continue
                            print(f"Ignoring exception in worker:\n{traceback.format_exc()}", file=sys.stderr)
                        finally:  # mark as done
                            self.queue.task_done()
                            slept = 0
                except asyncio.CancelledError:
                    return
            return wrap_wrk
        return inner

    async def start(self, worker, num_workers: int = 5):
        """starts executing"""
        self.workers = []
        for i in range(num_workers):
            self.workers.append(asyncio.create_task(worker()))

    async def add_task(self, *args):
        """workers in the pool will get the args"""
        self.queue.put(*args)

    async def add_task_nowait(self, *args):
        """same as add_task() but not blocking"""
        self.queue.put_nowait(args)

    async def join(self, timeout: int = 0):
        """
        wait for workers to finish
        returns false if timed out, true otherwise
        """
        slept = 0
        while not self.queue.empty():
            if timeout and slept > timeout:
                return False
            await asyncio.sleep(0.1)
        return True

    async def kill(self):
        """force terminate the workers"""
        for task in self.tasks:
            task.cancel()

    async def kill_nowait(self):
        """force terminate the workers without blocking"""
        asyncio.create_task(self.kill())

    async def __call__(self, worker, num_workers: int = 5, timeout: int = 0):
        """
        same as start() but blocking,
        wait for tasks to finish
        """
        await self.start(worker, num_workers)
        await self.join(timeout)

def msgsep(msg: str):
    results = []
    result = ""
    lines = msg.split("\n")
    for line in lines:
        if len(line) + len(result) > 1999:
            results.append(result)
            result = line + "\n"
            continue
        result += line + "\n"
    if result != "":
        results.append(result)
    return results


@functools.lru_cache()
def get_cmd(name: str, cmdlist: dt.CmdDict) -> dt.CmdRes:
    outcmdname, outcandidates = proc.get_cmd(name, set(cmdlist.keys()))
    return dt.CmdRes(cmdlist[outcmdname] if outcmdname else None, name, outcandidates if any(outcandidates) else None)
