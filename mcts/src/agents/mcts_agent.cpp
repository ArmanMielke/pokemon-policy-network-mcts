#include "mcts_agent.h"
#include "../showdown_client/showdown_client.h"
#include "mcts/vanilla.h"

#include <iostream>
#include <optional>
#include <stdlib.h>
#include <string>

#include <thread>
#include <chrono>

std::string const ACTION_FILE = "action.txt";

void log_action(std::string const action) {
    std::fstream file_stream;
    file_stream.open(ACTION_FILE, std::ios::app);
    file_stream << action << std::endl;
    file_stream.close();
}


// TODO the MCTS agent assumes that it is player 1, i.e. the one who challenged the other player. doesn't work otherwise
bool start_mcts_agent(ShowdownClient& client, std::string const battle_room_name) {
    // team preview
    // TODO implement properly
    sleep(5);
    client.send_message("/choose default", battle_room_name);
    sleep(5);

    std::optional<bool> battle_won = std::nullopt;
    do {
        std::string const input_log = client.request_input_log(battle_room_name);

        std::string action = vanilla::run_mcts(input_log);
        log_action(action);
        std::cout << "[MCTS Agent] Selected action: " << action << std::endl;

        client.send_message("/choose " + action, battle_room_name);

        // TODO properly wait until it's the agent's turn to do something again
        sleep(5);

        battle_won = client.check_battle_over(battle_room_name);
    } while (!battle_won.has_value());

    return battle_won.value();
}
