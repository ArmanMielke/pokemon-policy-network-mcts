#ifndef POKEMON_MCTS_SHOWDOWN_SIMULATOR_H
#define POKEMON_MCTS_SHOWDOWN_SIMULATOR_H

#include <array>
#include <string>
#include <vector>
#include <optional>

#include <boost/process.hpp>
#include <nlohmann/json.hpp>

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


// TODO move all of this somewhere else?
const int NUM_POKEMON = 3;
const int NUM_STATS = 6;
const int NUM_TYPES = 18;
const int NUM_MOVES = 4;

struct PokemonData {
public:
    /// 1 if the Pokémon is active, 0 otherwise.
    float is_active;
    /// The current HP of the Pokémon.
    float hp;
    /// The Pokémon's stats in the order attack, defense, special attack, special defense, speed, maximum HP.
    std::array<float, NUM_STATS> stats = { 0 };
    /// An array representing the Pokémon's types.
    /// The types that the Pokémon has are 1, all other types are 0.
    std::array<float, NUM_TYPES> types = { 0 };
    /// The IDs of each of the Pokémon's moves.
    std::array<float, NUM_MOVES> moves = { 0 };
    /// For each move, the one-hot encoded type.
    std::array<std::array<float, NUM_TYPES>, NUM_MOVES> move_types = { 0 };
    /// The base power of each move.
    std::array<float, NUM_MOVES> move_damages = { 0 };
    /// The category of each move.
    /// 0 for status, 1 for special, 2 for physical.
    std::array<float, NUM_MOVES> move_categories = { 0 };
};

typedef std::array<PokemonData, NUM_POKEMON> PlayerData;


class ShowdownSimulator {
public:
    explicit ShowdownSimulator();
    /// Executes one or multiple commands on the battle simulator.
    /// Each command must be preceded by a `>`, with no space between the `>` and the command.
    /// If there are multiple commands, commands must be separated by line breaks.
    /// The outputs of the commands are discarded.
    /// Assumes that the game has not ended.
    void execute_commands(std::string const commands);
    /// @return all actions available to the given player.
    ///         Each action is given as a command that can be executed with execute_commands() by prepending ">p",
    ///         then the number of the player followed by a space.
    ///         E.g. if `player` is 1 and one of the actions is "move 2", then the corresponding command would
    ///         be ">p1 move 2".
    std::vector<std::string> get_actions(Player const player);
    /// Assumes that the game has not ended.
    /// @return the number of remaining Pokémon for each player.
    std::array<int, 2> get_num_remaining_pokemon();
    /// Bundles information that can be used for an action selection heuristic.
    /// @return Information about given player's Pokémon.
    PlayerData get_player_info(Player const player);
    /// @return `true`, iff the game has ended.
    bool is_finished() const;
    /// @return `std::nullopt` as long as `is_finished()` returns false.
    ///         After the game has ended, this returns the winner, if a winner could be determined.
    std::optional<Player> get_winner() const;

private:
    /// The child process that runs the battle simulator.
    bp::child child_process;
    /// std_in of the child process.
    bp::opstream child_input;
    /// std_out of the child process.
    /// Output should not be read from `child_output` directly.
    /// Instead, `read_output_line()` should be used.
    ///
    /// All methods should ensure that there are no unread lines in `child_output` after they complete,
    /// since methods implicitly assume that there is no unread output.
    bp::ipstream child_output;
    /// `true` iff the game has ended.
    bool finished = false;
    /// This is `std::nullopt` before the game ends.
    /// It is set at the end of the game if a winner could be determined.
    std::optional<Player> winner = std::nullopt;
    nlohmann::json types_json;
    nlohmann::json moves_json;

    /// Reads a line from the output of the child process.
    /// This also checks whether the game has ended during that line and updates `this.finished` and `this.winner`
    /// accordingly.
    std::string read_output_line();
    /// Discards any output of the child process that hasn't been read yet.
    /// If a command is run after skip_output(), the next output line will be from that command.
    void skip_output();
    /// Runs a JavaScript command on the simulator in the child process using ">eval".
    /// Assumes that the command's output is one line.
    /// Assumes that the game has not ended.
    /// @return the output of the command.
    std::string eval(std::string const command);
    /// Assumes that the game has not ended.
    /// @return for the given player, the indices of the Pokémon that haven't fainted.
    ///         Indices are in ascending order.
    std::vector<int> get_remaining_pokemon(Player const player);
    /// Assumes that the game has not ended.
    /// @return the request state for the given player.
    RequestState get_request_state(Player const player);
    /// Assumes that the game has not ended.
    /// @return a vector indicating for each pokemon whether it has fainted.
    std::vector<bool> get_pokemon_fainted(Player const player);
    /// Bundles information that can be used for an action selection heuristic.
    /// @return Information about the given Pokémon from the given player.
    PokemonData get_pokemon_info(Player const player, int const pokemon);
};


#endif //POKEMON_MCTS_SHOWDOWN_SIMULATOR_H
