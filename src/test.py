"""Testing stuff."""
import proc

print(proc.test_fn(a="abc"))

#from modules import tools
#import requests, asyncio
#
#
#pool = tools.AsyncPool()
#
#@pool.set_worker()
#async def get_page(url: str):
#    requests.get("https://" + url)
#
#
#async def main():
#    await pool.add_task_nowait("google.com")
#    await pool.add_task_nowait("duckduckgo.com")
#    await pool.add_task_nowait("python.org")
#    await pool.add_task_nowait("discord.com")
#    await pool.add_task_nowait("github.com")
#    await pool.add_task_nowait("windowsboy111.github.io")
#    await pool.add_task_nowait("youtube.com")
#    await pool.add_task_nowait("twitter.com")
#    print("working")
#    await pool.start(get_page)
#    print("joining")
#    await pool.join()
#
#if __name__ == "__main__":
#    asyncio.run(main())
