#include "random_agent.h"

#include <iostream>
#include <optional>
#include <stdlib.h>
#include <string>
#include <vector>


// TODO properly determine available actions
std::vector<std::string> const ACTIONS = {"move 1", "move 2", "switch 2", "switch 3"};


bool start_random_agent(ShowdownClient& client, std::string const battle_room_name) {
    std::random_device r;
    std::default_random_engine generator{r()};
    std::uniform_int_distribution<> action_distribution{0, ACTIONS.size() - 1};

    // team preview
    // TODO implement properly
    sleep(5);
    client.send_message("/choose default", battle_room_name);
    sleep(5);

    std::optional<bool> battle_won = std::nullopt;

    do {
        int const action_index = action_distribution(generator);
        std::string const action = ACTIONS[action_index];

        std::cout << "[Random Agent] Chose action: " << action << std::endl;
        client.send_message("/choose " + action, battle_room_name);

        // TODO properly wait until it's the agent's turn to do something again
        sleep(30);

        battle_won = client.check_battle_over(battle_room_name);
    } while (!battle_won.has_value());

    return battle_won.value();
}
