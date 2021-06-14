#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <set>
#include <string>
#include <algorithm>
#include <iostream>

namespace py = pybind11;
using namespace py::literals;

std::string test_fn(std::string a)
{
    return "Hello, World!\n" + a;
}

std::pair<std::string, std::set<std::string>> get_cmd(std::string name, std::set<std::string> cmds)
{
    // turn name to lowercase
    transform(name.begin(), name.end(), name.begin(), ::tolower);

    if (cmds.contains(name))
        return std::make_pair(name, std::set<std::string>());

    // check for cmds starting with the name
    std::set<std::string> res;
    int len = name.length();
    for (auto cmd : cmds) if (cmd.substr(0, len) == name) res.insert(cmd);
    if (res.size() == 1)
    {
        return std::make_pair(*res.cbegin(), std::set<std::string>());
    }
    if (res.size()) // which means res.size() > 1
        return std::make_pair("", res);

    res.clear();
    for (auto cmd : cmds) if (int(cmd.size()) < len) res.insert(cmd);
    if (res.size() == 1)
        return std::make_pair(*res.cbegin(), std::set<std::string>());
    if (res.size())
        return std::make_pair("", res);

    return std::make_pair("", std::set<std::string>());
}

PYBIND11_MODULE(proc, m)
{
    m.doc() = "Merlin but C++"; // Optional module docstring
    m.def("test", &test_fn, "should give hello world", "a"_a);
    py::object bye = py::cast("bye");
    m.attr("hello") = bye;
    m.def("get_cmd", &get_cmd, "get command by lists of commands and query");
}
