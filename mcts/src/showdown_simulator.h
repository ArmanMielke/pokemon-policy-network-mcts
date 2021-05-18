#ifndef POKEMON_MCTS_SHOWDOWN_SIMULATOR_H
#define POKEMON_MCTS_SHOWDOWN_SIMULATOR_H

#include <string>

#include <boost/process.hpp>

namespace bp = boost::process;

/// Must be either 1 or 2.
typedef int Player;

/// Determines what actions a player has available.
enum RequestState {
    TEAM_PREVIEW,
    /// The player can attack or switch.
    /// Occurs at the beginning of a turn.
    MOVE,
    /// The player must switch in a Pokémon.
    /// Occurs e.g. if a Pokémon has fainted, or if a move that switches in another Pokémon was used.
    SWITCH,
    /// The player can't do anything at the moment.
    NONE,
};

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
    /// Skips the given number of lines in the output.
    void skip_output_lines(int const number_of_lines);
    /// Assumes that there is no unread output.
    /// @return the request state for the given player.
    RequestState get_request_state(Player const player);
};


#endif //POKEMON_MCTS_SHOWDOWN_SIMULATOR_H
