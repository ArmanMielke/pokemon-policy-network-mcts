#include "showdown_simulator.h"

#include <iostream>
#include <limits>
#include <string>

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

    // there is one empty line in the output immediately after the mark
    this->skip_output_lines(1);
}

void ShowdownSimulator::skip_output_lines(int const number_of_lines) {
    for (int i = 0; i < number_of_lines; i++) {
        this->child_output.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
    }
}

RequestState ShowdownSimulator::get_request_state(Player const player) {
    this->execute_commands(">eval p" + std::to_string(player) + ".requestState");

    // the command outputs 4 lines, the third of which contains our output
    skip_output_lines(2);
    std::string out_line;
    std::getline(this->child_output, out_line);
    skip_output_lines(1);

    if (out_line == "||<<< \"teampreview\"") {
        return RequestState::TEAM_PREVIEW;
    } else if (out_line == "||<<< \"move\"") {
        return RequestState::MOVE;
    } else if (out_line == "||<<< \"switch\"") {
        return RequestState::SWITCH;
    } else {
        return RequestState::NONE;
    }
}
