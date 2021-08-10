#ifndef POKEMON_MCTS_MCTS_AGENT_MCTS_H
#define POKEMON_MCTS_MCTS_AGENT_MCTS_H

#include "node.h"

#include <string>

namespace vanilla{
    Action run_mcts(std::string const input_log);
}



#endif //POKEMON_MCTS_MCTS_AGENT_MCTS_H