#include "mcts_agent.h"
#include "mcts/mcts.h"
#include "../policies/policy.h"
#include "../showdown_client/showdown_client.h"

#include <iostream>
#include <optional>
#include <stdlib.h>
#include <string>

#include <boost/optional.hpp>


// TODO the MCTS agent assumes that it is player 1, i.e. the one who challenged the other player. doesn't work otherwise
bool start_mcts_agent(
    ShowdownClient& client,
    std::string const battle_room_name,
    boost::optional<Policy&> policy
) {
    // team preview
    // TODO implement properly
    sleep(5);
    client.send_message("/choose default", battle_room_name);
    sleep(5);

    std::optional<bool> battle_won = std::nullopt;
    do {
        std::string const input_log = client.request_input_log(battle_room_name);

        std::string action = run_mcts(input_log, policy);
        std::cout << "[MCTS Agent] Selected action: " << action << std::endl;


        // TODO properly wait until it's the agent's turn to do something again
        sleep(5);

        battle_won = client.check_battle_over(battle_room_name);
    } while (!battle_won.has_value());

    return battle_won.value();
}
