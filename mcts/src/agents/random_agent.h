#ifndef POKEMON_MCTS_RANDOM_AGENT_H
#define POKEMON_MCTS_RANDOM_AGENT_H

#include "../showdown_client/showdown_client.h"

#include <string>


bool start_random_agent(ShowdownClient& client, std::string const battle_room_name);


#endif //POKEMON_MCTS_RANDOM_AGENT_H
