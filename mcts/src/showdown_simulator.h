#ifndef POKEMON_MCTS_SHOWDOWN_SIMULATOR_H
#define POKEMON_MCTS_SHOWDOWN_SIMULATOR_H

#include <string>

#include <boost/process.hpp>

namespace bp = boost::process;


class ShowdownSimulator {
public:
    explicit ShowdownSimulator();
    /// Executes one or multiple commands on the battle simulator.
    /// Each command must be preceded by a `>`, with no space between the `>` and the command.
    /// If there are multiple commands, commands must be separated by line breaks.
    void execute_commands(std::string const commands);

private:
    /// The child process that runs the battle simulator.
    bp::child child_process;
    /// std_in of the child process.
    bp::opstream child_input;
    /// std_out of the child process.
    bp::ipstream child_output;
    /// The number of the next mark that will be set.
    int next_mark = 0;

    /// Sets a mark in the battle simulator's output so that everything up to that mark can easily be skipped.
    /// This is useful when executing many commands at once and reading the output of the final command.
    /// Before the last command, set a mark, then skip to that mark.
    /// The output of the commands before the mark will be skipped, so that the next output is that of the last command.
    /// @return a number identifying the mark.
    int set_mark();
    /// Skips the output up to the given mark.
    void skip_to_mark(int const mark);
};


#endif //POKEMON_MCTS_SHOWDOWN_SIMULATOR_H
