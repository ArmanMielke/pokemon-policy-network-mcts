#include "showdown_websocket.h"

#include <iostream>


int main() {
    ShowdownWebsocket websocket{"echo.websocket.org", "80"};
    std::cout << websocket.send_message("message 1 part 1\nmessage 1 part 2") << std::endl;
    std::cout << "----------------" << std::endl;
    std::cout << websocket.send_message("message 2") << std::endl;
}
