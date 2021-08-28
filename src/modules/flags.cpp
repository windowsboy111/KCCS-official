#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <map>
#include <string>
#include <algorithm>
#include <iostream>
#include <boost/program_options/options_description.hpp>
#include <boost/any.hpp>

namespace py = pybind11;
using namespace py::literals;

std::map<std::string, boost::any> process_flags(std::string content)
{
}

PYBIND11_MODULE(proc, m)
{
    m.doc() = "Merlin flags"; // Optional module docstring
    py::object bye = py::cast("bye");
    m.attr("hello") = bye;
    m.def("process_flags", &process_flags, "get command by lists of commands and query");
}
