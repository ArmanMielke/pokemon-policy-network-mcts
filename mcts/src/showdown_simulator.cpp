#include "showdown_simulator.h"

#include <iostream>
#include <limits>
#include <optional>
#include <string>
#include <vector>

#include <boost/algorithm/string.hpp>
#include <boost/process.hpp>
#include <nlohmann/json.hpp>

namespace bp = boost::process;


// TODO insert path to showdown executable
std::string const SHOWDOWN_EXECUTABLE = "";
std::string const ARGUMENT = "simulate-battle";

std::string const MARK_STRING = "#*0-mark-*0#";


// Helper Functions
// //////////////// //

/// For each Pokémon index, this creates an action that switches in that Pokémon.
/// @return the created actions.
std::vector<std::string> pokemon_indices_to_switch_actions(std::vector<int> const pokemon_indices) {
    std::vector<std::string> actions{pokemon_indices.size()};
    std::transform(
        pokemon_indices.begin(), pokemon_indices.end(), actions.begin(),
        // need to add 1 to pokemon, since pokemon indices start at one when the player makes a switch
        [](int pokemon){ return "switch " + std::to_string(pokemon + 1); }
    );
    return actions;
}

// End Helper Functions
// //////////////////// //


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

std::vector<std::string> ShowdownSimulator::get_actions(Player const player) {
    switch(this->get_request_state(player)) {
        case RequestState::MOVE: {
            // switch actions: the player can switch in any Pokémon other than the active one
            std::vector<int> available_pokemon = this->get_remaining_pokemon(player);
            // cannot switch in the first pokemon, since it's already active
            available_pokemon.erase(available_pokemon.begin());
            std::vector<std::string> actions = pokemon_indices_to_switch_actions(available_pokemon);

            // move actions: the player can attack with any move of the active pokemon
            // move indices start at 1
            // TODO implement this properly instead of assuming that the Pokémon has two moves
            actions.push_back("move 1");
            actions.push_back("move 2");
            return actions;
        }
        case RequestState::SWITCH: {
            // there is one action for each available Pokémon (to switch in that Pokémon)
            return pokemon_indices_to_switch_actions(this->get_remaining_pokemon(player));
        }
        case RequestState::TEAM_PREVIEW:
        case RequestState::NONE:
        default:
            return std::vector<std::string>{};
    }
}

std::vector<int> ShowdownSimulator::get_remaining_pokemon(Player const player) {
    std::vector<bool> const pokemon_fainted = this->get_pokemon_fainted(player);
    std::vector<int> remaining_pokemon;

    // Pokémon indices start at 0 in the simulator
    for (int i = 0; i < pokemon_fainted.size(); i++) {
        // add a Pokémon's index to the list if it hasn't fainted
        if (!pokemon_fainted[i]) {
            remaining_pokemon.push_back(i);
        }
    }

    return remaining_pokemon;
}

void ShowdownSimulator::skip_output() {
    // set a mark so that we can skip everything up to the mark
    this->execute_commands(">chat " + MARK_STRING);

    // read output lines until the line where the mark was set appears, or we find out that the game has ended
    std::string out_line;
    do {
        out_line = this->read_output_line();
    } while (out_line != "|chat|" + MARK_STRING && out_line != "end");

    // there is one empty line in the output immediately after the mark
    this->read_output_line();  // skip
}

bool ShowdownSimulator::is_finished() const {
    return this->finished;
}

std::optional<Player> ShowdownSimulator::get_winner() const {
    return this->winner;
}

std::string ShowdownSimulator::read_output_line() {
    // read line from stdout of the child process
    std::string out_line;
    std::getline(this->child_output, out_line);

    // check if the game has ended
    if (out_line == "end") {
        this->finished = true;

        // find out who won
        std::getline(this->child_output, out_line);
        nlohmann::json game_result = nlohmann::json::parse(out_line);
        // for each player, this holds how many Pokémon they have left
        std::array<int, 2> scores = game_result["score"];

        if (scores[0] > 0 && scores[1] == 0) {
            this->winner = 1;
        } else if (scores[0] == 0 && scores[1] > 0) {
            this->winner = 2;
        } else {
            std::cout << "[ShowdownSimulator] ERROR: Game has ended, but no winner could be determined. "
                      << "Scores: [p1: " << scores[0] << ", p2: " << scores[2] << "]" << std::endl;
        }

        return "end";
    }

    return out_line;
}

RequestState ShowdownSimulator::get_request_state(Player const player) {
    this->execute_commands(">eval p" + std::to_string(player) + ".requestState");

    // the command outputs 4 lines, the third of which contains the info we need
    this->read_output_line();  // skip
    this->read_output_line();  // skip
    std::string out_line = this->read_output_line();
    this->read_output_line();  // skip

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

std::vector<bool> ShowdownSimulator::get_pokemon_fainted(const Player player) {
    this->execute_commands(">eval p" + std::to_string(player) + ".pokemon.map(p => p.fainted)");

    // the command outputs 4 lines, the third of which contains the info we need
    this->read_output_line();  // skip
    this->read_output_line();  // skip
    std::string out_line = this->read_output_line();
    this->read_output_line();  // skip

    // out_line looks something like this: "||<<< [false, true, true, false, false, false]"
    // only keep what's inside the brackets so that we have this: "false, true, true, false, false, false"
    out_line = out_line.substr(7, out_line.size() - 8);

    // split into separate strings
    std::vector<std::string> fainted_string;
    boost::split(fainted_string, out_line, boost::is_any_of(","));

    // convert to bool
    std::vector<bool> fainted_bool(fainted_string.size());
    std::transform(
        fainted_string.begin(), fainted_string.end(), fainted_bool.begin(),
        [](std::string fainted){ return boost::trim_copy(fainted) == "true"; }
    );

    return fainted_bool;
}
