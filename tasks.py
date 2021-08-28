"""Invoker tasks."""
import invoke
COMPILER = "g++"


@invoke.task
def build(c, docs=False):
    for file in ("modules/proc", "modules/flags"):
        print(end=f"building {file}.cpp...\r", flush=True)
        invoke.run(f"{COMPILER} -O3 -Wall -shared -std=c++20 -fPIC $(python-config --includes) -Iextern/pybind11/include src/{file}.cpp -o src/{file}$(python-config --extension-suffix)")
        print(f"built {file}.cpp      ")
