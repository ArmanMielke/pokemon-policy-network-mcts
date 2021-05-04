#ifndef POKEMON_MCTS_SHOWDOWN_CLIENT_H
#define POKEMON_MCTS_SHOWDOWN_CLIENT_H

#include "websocket.h"

#include <string>


class ShowdownClient {
public:
    /// Logs in to Pokémon Showdown under the given username.
    explicit ShowdownClient(std::string const username);
    void send_message(std::string const message, std::string const room_name = "");

private:
    WebSocket websocket;
};


#endif //POKEMON_MCTS_SHOWDOWN_CLIENT_H
