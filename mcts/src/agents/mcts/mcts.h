#ifndef POKEMON_MCTS_MCTS_AGENT_MCTS_H
#define POKEMON_MCTS_MCTS_AGENT_MCTS_H

#include "node.h"
#include "../../policy_network.h"

#include <string>


Action run_mcts(std::string const input_log, PolicyNetwork& policy_network);


#endif //POKEMON_MCTS_MCTS_AGENT_MCTS_H
