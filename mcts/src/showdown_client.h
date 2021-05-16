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
    /// Challenges the given user to a battle, waits until they accept, then returns the name of the room.
    /// May not work if this client's user has another battle in progress.
    std::string challenge_user(std::string const user, std::string const battle_format);

private:
    WebSocket websocket;
};


#endif //POKEMON_MCTS_SHOWDOWN_CLIENT_H
