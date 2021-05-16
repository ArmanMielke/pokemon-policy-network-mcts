#include "showdown_client.h"

#include <stdlib.h>
#include <string>


int main() {
    ShowdownClient client{"cpp-djcoaisjdcoai"};
    std::string battle_room_name = client.challenge_user("pmariglia-sidudhc", "gen8randombattle");

    while (true) {
        client.do_default_action(battle_room_name);
        sleep(5);
    }
}
