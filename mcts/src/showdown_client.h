#ifndef POKEMON_MCTS_SHOWDOWN_CLIENT_H
#define POKEMON_MCTS_SHOWDOWN_CLIENT_H

#include "websocket.h"

#include <string>


class ShowdownClient {
public:
    /// Logs in to Pokémon Showdown under the given username.
    explicit ShowdownClient(std::string const username);
    void send_message(std::string const message, std::string const room_name = "");
    void join_room(std::string const room_name);
    /// Challenges the given user to a battle, waits until they accept (or 7 messages have been received),
    /// then returns the name of the room.
    std::string challenge_user(std::string const user, std::string const battle_format);

    void do_default_action(std::string const room_name);

private:
    WebSocket websocket;
};


#endif //POKEMON_MCTS_SHOWDOWN_CLIENT_H
