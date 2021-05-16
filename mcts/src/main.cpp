#include "showdown_client.h"
#include "agents/default_action_agent.h"

#include <string>


int main() {
    ShowdownClient client{"cpp-djcoaisjdcoai"};
    std::string battle_room_name = client.challenge_user("pmariglia-sidudhc", "gen8randombattle");

    start_default_action_agent(client, battle_room_name);
}
