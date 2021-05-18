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
};


#endif //POKEMON_MCTS_SHOWDOWN_SIMULATOR_H
