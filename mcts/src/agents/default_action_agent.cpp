#include "default_action_agent.h"

#include <stdlib.h>
#include <string>


void start_default_action_agent(ShowdownClient& client, std::string const battle_room_name) {
    while (true) {
        // do default action
        client.send_message("/choose default", battle_room_name);
        sleep(2);
    }
}
