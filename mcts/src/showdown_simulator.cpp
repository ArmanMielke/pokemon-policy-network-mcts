#include "showdown_simulator.h"

#include <iostream>

#include <boost/process.hpp>

namespace bp = boost::process;


// TODO insert path to showdown executable
std::string const SHOWDOWN_EXECUTABLE = "";
std::string const ARGUMENT = "simulate-battle";

std::string const MARK_STRING = "#*mark*#";


ShowdownSimulator::ShowdownSimulator() {
    this->child_process = bp::child{
        SHOWDOWN_EXECUTABLE,
        ARGUMENT,
        bp::std_in < this->child_input,
        bp::std_out > this->child_output
    };
}

void ShowdownSimulator::execute_commands(std::string const commands) {
    this->child_input << commands << std::endl;
}

int ShowdownSimulator::set_mark() {
    int mark = this->next_mark;
    this->next_mark++;
    this->execute_commands(">chat " + MARK_STRING + std::to_string(mark) + MARK_STRING);
    return mark;
}

void ShowdownSimulator::skip_to_mark(int const mark) {
    std::string out_line;

    // read output lines until the line where the mark was set appears
    std::string const mark_line = "|chat|" + MARK_STRING + std::to_string(mark) + MARK_STRING;
    do {
        std::getline(this->child_output, out_line);
    } while (out_line != mark_line);

    // there is one empty line in the output immediately after the mark. skip that, too
    std::getline(this->child_output, out_line);
}
