#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <set>
#include <string>
#include <algorithm>
#include <cmath>
#include <math.h>
#include <map>
#include <iostream>
#include <functional>
#include "jwdistance.h"

#define AP 0.6
namespace py = pybind11;
using namespace py::literals;


int levenshtein_distance(const std::string str1, const std::string str2)
{  //? https://www.tutorialspoint.com/cplusplus-program-to-implement-levenshtein-distance-computing-algorithm
    int i, j, l1, l2, t, track;
    int dist[50][50];
    // take the strings as input
    const char *s1 { str1.c_str() };
    const char *s2 { str2.c_str() };
    // stores the length of strings s1 and s2
    l1 = strlen(s1);
    l2 = strlen(s2);
    for (i = 0;i <= l1;i++)
    {
        dist[0][i] = i;
    }
    for (j = 0;j <= l2;j++)
    {
        dist[j][0] = j;
    }
    for (j = 1;j <= l1;j++)
    {
        for (i = 1;i <= l2;i++)
        {
            track = (s1[i - 1] == s2[j - 1]) ? 0 : 1;
            t = std::min((dist[i - 1][j] + 1), (dist[i][j - 1] + 1));
            dist[i][j] = std::min(t, (dist[i - 1][j - 1] + track));
        }
    }
    return dist[l2][l1];
}

std::vector<std::string> get_cmd(std::string name, const std::vector<std::string> cmds)
{
    // turn name to lowercase
    transform(name.begin(), name.end(), name.begin(), ::tolower);

    // check for equalities
    for (auto &cmd : cmds)
        if (name == cmd)
            return { name, };

    // check "if length is same, then is same?"
    std::multimap<double, std::string, std::greater<double>> res {};
    const int len = name.length();  // length of `name` + 1, for substr
    for (auto cmd : cmds)
        res.insert({ jw_distance(cmd.substr(0, len), name), cmd });

    if (res.size())
    {
        int count { 0 };
        std::vector<std::string> ret;
        for (auto &[key, val] : res)
        {
            if (key == 1.0)
                ++count;
            else
                if (count == 1)
                    return ret;
            if (key)
                ret.emplace_back(val);
        }
        return ret;
    }

    res.clear();
    for (auto &cmd : cmds)
        if (cmd.length() >= len)
            res.insert({ jw_distance(name.substr(0, cmd.length()), cmd), cmd });

    if (res.size())
    {
        int count { 0 };
        std::vector<std::string> ret;
        for (auto &[key, val] : res)
        {
            if (key == 1.0)
                ++count;
            else
                if (count == 1)
                    return ret;
            if (key)
                ret.emplace_back(val);
        }
        return ret;
    }

    res.clear();
    for (auto &cmd : cmds)
        res.insert({ jw_distance(name, cmd), cmd });

    std::vector<std::string> ret;
    int count { 0 };
    for (auto &[key, val] : res)
    {
        if (key == 1.0)
            ++count;
        else
            if (count == 1)
                return ret;
        if (key)
            ret.emplace_back(val);
    }
    return ret;
}

PYBIND11_MODULE(proc, m)
{
    m.doc() = "Merlin special progs, submodules and procedures";
    // m.def("test", &test_fn, "should give hello world", "a"_a);
    // py::object bye = py::cast("bye");
    // m.attr("hello") = bye;
    m.def("get_cmd", &get_cmd, "get command by lists of commands and query");
    m.def("jws", &jw_distance, "Calculate the Jaro-Winkler Distance");
}
