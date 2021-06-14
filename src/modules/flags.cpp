#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <maps>
#include <string>
#include <algorithm>
#include <iostream>
#include <boost/program_options/options_description.hpp>
#include <boost/any_cast.hpp>

namespace py = pybind11;
using namespace py::literals;

std::map<std::string, boost::any> process_flags(std::string content)
{
    content.split(" ");
}

PYBIND11_MODULE(proc, m)
{
    m.doc() = "Merlin flags"; // Optional module docstring
    py::object bye = py::cast("bye");
    m.attr("hello") = bye;
    m.def("get_cmd", &get_cmd, "get command by lists of commands and query");
}
