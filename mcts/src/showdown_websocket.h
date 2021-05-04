#ifndef POKEMON_MCTS_SHOWDOWN_WEBSOCKET_H
#define POKEMON_MCTS_SHOWDOWN_WEBSOCKET_H

#include <string>


class ShowdownWebsocket {
public:
    explicit ShowdownWebsocket(std::string const host, std::string const port, std::string const message);
};


#endif //POKEMON_MCTS_SHOWDOWN_WEBSOCKET_H
