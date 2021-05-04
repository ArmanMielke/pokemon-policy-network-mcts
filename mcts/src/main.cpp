#include "showdown_websocket.h"

#include <iostream>


int main() {
    ShowdownWebsocket websocket{"echo.websocket.org", "80"};
    websocket.send_message("message 1 part 1\nmessage 1 part 2");
    std::cout << websocket.receive_message() << std::endl;
    std::cout << "----------------" << std::endl;
    websocket.send_message("message 2");
    std::cout << websocket.receive_message() << std::endl;
}
