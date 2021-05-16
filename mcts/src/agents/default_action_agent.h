#ifndef POKEMON_MCTS_DEFAULT_ACTION_AGENT_H
#define POKEMON_MCTS_DEFAULT_ACTION_AGENT_H

#include "../showdown_client/showdown_client.h"

#include <string>


/// Repeatedly chooses the default action, regardless of the game state.
void start_default_action_agent(ShowdownClient& client, std::string const battle_room_name);


#endif //POKEMON_MCTS_DEFAULT_ACTION_AGENT_H
