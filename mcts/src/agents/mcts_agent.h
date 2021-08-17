#ifndef POKEMON_MCTS_MCTS_AGENT_H
#define POKEMON_MCTS_MCTS_AGENT_H

#include "../showdown_client/showdown_client.h"
#include "../policies/policy.h"

#include <string>

#include <boost/optional.hpp>


bool start_mcts_agent(
    ShowdownClient& client,
    std::string const battle_room_name,
    boost::optional<Policy&> policy = std::nullopt
);


#endif //POKEMON_MCTS_MCTS_AGENT_H
