#ifndef POKEMON_MCTS_SHOWDOWN_SIMULATOR_H
#define POKEMON_MCTS_SHOWDOWN_SIMULATOR_H

#include <string>
#include <vector>

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
    /// Assumes that there is no unread output.
    /// @return for the given player, the indices of the Pokémon that haven't fainted.
    ///         Indices are in ascending order.
    std::vector<int> get_remaining_pokemon(Player const player);

private:
    /// The child process that runs the battle simulator.
    bp::child child_process;
    /// std_in of the child process.
    bp::opstream child_input;
    /// std_out of the child process.
    bp::ipstream child_output;

    /// Discards any output of the child process that hasn't been read yet.
    /// If a command is run after skip_output(), the next output line will be from that command.
    void skip_output();
    /// Skips the given number of lines in the output of the child process.
    void skip_output_lines(int const number_of_lines);
    /// Assumes that there is no unread output.
    /// @return the request state for the given player.
    RequestState get_request_state(Player const player);
    /// Assumes that there is no unread output.
    /// @return a vector indicating for each pokemon whether it has fainted.
    std::vector<bool> get_pokemon_fainted(Player const player);
};


#endif //POKEMON_MCTS_SHOWDOWN_SIMULATOR_H
