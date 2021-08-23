#include "mcts_agent.h"
#include "mcts/mcts.h"
#include "../policies/policy.h"
#include "../showdown_client/showdown_client.h"

#include <iostream>
#include <optional>
#include <stdlib.h>
#include <string>
#include <chrono>

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
    sleep(10);

    std::optional<bool> battle_won = std::nullopt;
    int turn_counter = 0;
    int acc_turn_time = 0;

    do {
        std::string const input_log = client.request_input_log(battle_room_name);

        auto start = std::chrono::high_resolution_clock::now();

        std::string action = run_mcts(input_log, policy);
        auto stop = std::chrono::high_resolution_clock::now();
        auto duration = duration_cast<std::chrono::seconds>(stop - start);

        std::cout << "[MCTS Agent] Selected action: " << action << std::endl;

        client.send_message("/choose " + action, battle_room_name);

        // TODO properly wait until it's the agent's turn to do something again
        sleep(5);
        turn_counter++;
        acc_turn_time += duration.count();

        battle_won = client.check_battle_over(battle_room_name);
    } while (!battle_won.has_value());

    std::fstream file_stream;
    file_stream.open("log.txt", std::ios::app);
    file_stream << std::to_string((int)acc_turn_time/turn_counter) << std::endl;
    file_stream.close();

    return battle_won.value();
}
