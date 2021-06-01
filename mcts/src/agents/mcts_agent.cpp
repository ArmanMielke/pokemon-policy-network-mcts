#include "mcts_agent.h"
#include "../showdown_client/showdown_client.h"
#include "mcts/mcts.h"

#include <iostream>
#include <optional>
#include <stdlib.h>
#include <string>


bool start_mcts_agent(ShowdownClient& client, std::string const battle_room_name) {
    std::optional<bool> battle_won = std::nullopt;

    do {
        std::string const input_log = client.request_input_log(battle_room_name);

        std::string action = run_mcts(input_log);
        std::cout << "[MCTS Agent] Selected action: " << action << std::endl;

        client.send_message("/choose " + action, battle_room_name);

        // TODO properly wait until it's the agent's turn to do something again
        sleep(5);

        battle_won = client.check_battle_over(battle_room_name);
    } while (!battle_won.has_value());

    return battle_won.value();
}
