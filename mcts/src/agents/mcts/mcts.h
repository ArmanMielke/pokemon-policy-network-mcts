#ifndef POKEMON_MCTS_MCTS_AGENT_MCTS_H
#define POKEMON_MCTS_MCTS_AGENT_MCTS_H

#include "node.h"
#include "../../policies/policy.h"

#include <string>

#include <boost/optional.hpp>


Action run_mcts(std::string const input_log, boost::optional<Policy&> policy = std::nullopt);


#endif //POKEMON_MCTS_MCTS_AGENT_MCTS_H
