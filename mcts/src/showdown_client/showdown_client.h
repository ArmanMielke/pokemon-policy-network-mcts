#ifndef POKEMON_MCTS_SHOWDOWN_CLIENT_H
#define POKEMON_MCTS_SHOWDOWN_CLIENT_H

#include "websocket.h"

#include <optional>
#include <string>


class ShowdownClient {
public:
    /// Logs in to Pokémon Showdown with the given username and password.
    /// If no password is given, this logs in with a temporary username.
    explicit ShowdownClient(std::string const username, std::optional<std::string> const password = std::nullopt);
    void send_message(std::string const message, std::string const room_name = "");
    void join_room(std::string const room_name);
    /// Specifies the team for the upcoming battle.
    /// @param team: Team specification in packed format.
    void set_team(std::string const team);
    /// Challenges the given user to a battle, waits until they accept, then returns the name of the room.
    /// May not work if this client's user has another battle in progress.
    std::string challenge_user(std::string const user, std::string const battle_format);
    std::string accept_challenge();
    /// Requests the list of inputs that have been made in the given battle room so far.
    /// The list is returned as one string, with inputs separated by line breaks.
    /// This string can be used to reproduce the current state of the battle using Pokémon Showdown's command line
    /// battle simulator, `pokemon-showdown simulate-battle`.
    std::string request_input_log(std::string const battle_room_name);
    /// @return `std::nullopt`, if the battle is still ongoing,
    ///         `true`, if the battle is won,
    ///         `false`, if the battle is lost.
    std::optional<bool> check_battle_over(std::string const battle_room_name);

private:
    WebSocket websocket;
    std::string const username;

    std::string get_battle_room_name(std::string const battle_format);
};


#endif //POKEMON_MCTS_SHOWDOWN_CLIENT_H
