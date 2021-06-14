"""Invoker tasks."""
import invoke


@invoke.task
def build(c, docs=False):
    for file in ("modules/proc", "modules/flags"):
        print(end=f"building {file}.cpp...\r", flush=True)
        invoke.run(f"g++ -O3 -Wall -shared -std=c++20 -fPIC $(python3.8-config --includes) -Iextern/pybind11/include src/{file}.cpp -o src/{file}$(python3.8-config --extension-suffix)")
        print(f"built {file}.cpp      ")
