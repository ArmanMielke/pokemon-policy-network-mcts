#ifndef POKEMON_MCTS_MCTS_AGENT_MCTS_H
#define POKEMON_MCTS_MCTS_AGENT_MCTS_H

#include "node.h"
#include "../../policy_network.h"

#include <string>

#include <boost/optional.hpp>


Action run_mcts(std::string const input_log, boost::optional<PolicyNetwork&> policy_network = std::nullopt);


#endif //POKEMON_MCTS_MCTS_AGENT_MCTS_H
