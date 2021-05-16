#include "showdown_client.h"
#include "showdown_login_request.h"

#include <iostream>
#include <string>
#include <vector>

#include <boost/algorithm/string.hpp>


std::string const SHOWDOWN_HOST = "localhost";
std::string const SHOWDOWN_PORT = "8808";
std::string const SHOWDOWN_TARGET = "/showdown/websocket";


ShowdownClient::ShowdownClient(std::string const username) : websocket{SHOWDOWN_HOST, SHOWDOWN_PORT, SHOWDOWN_TARGET} {
    // the first message after connecting only contains some unimportant info
    this->websocket.receive_message();

    // the second message contains some information required to log in
    std::vector<std::string> challstr_message;
    boost::split(challstr_message, this->websocket.receive_message(), boost::is_any_of("|"));
    // challstr_message[0] is ignored
    if (challstr_message[1] != "challstr") {
        std::cout << "[ShowdownClient] WARN: Expected message type \"challstr\", received \"" << challstr_message[1]
                  << "\"" << std::endl;
    }
    std::string const challstr = challstr_message[2] + "|" + challstr_message[3];

    // choose username (= log in to a new, temporary account without password)
    std::string const assertion = send_login_request(username, challstr);
    this->send_message("/trn " + username + ",0," + assertion);

    // the next two messages have no useful information
    this->websocket.receive_message();
    this->websocket.receive_message();
}

void ShowdownClient::send_message(std::string const message, std::string const room_name) {
    std::string const assembled_message = room_name + "|" + message;
    this->websocket.send_message(assembled_message);
}

void ShowdownClient::join_room(std::string const room_name) {
    this->send_message("/join " + room_name);
    // the next message has no useful information
    this->websocket.receive_message();
}

std::string ShowdownClient::challenge_user(std::string const user, std::string const battle_format) {
    this->send_message("/challenge " + user + "," + battle_format);

    // skip 7 messages
    // this also waits until the challenge was accepted
    for (int i = 0; i < 7; i++) {
        this->websocket.receive_message();
    }

    // any message in the battle room starts with the name of the room
    std::vector<std::string> battle_room_message;
    boost::split(battle_room_message, this->websocket.receive_message(), boost::is_any_of("|"));
    // there is a ">" before and a "\n" after the room name
    std::string battle_room_name = battle_room_message[0].substr(1, battle_room_message[0].length() - 2);
    std::cout << "[ShowdownClient] Started battle in room " << battle_room_name << std::endl;
    return battle_room_name;
}
