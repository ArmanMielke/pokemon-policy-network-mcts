#ifndef POKEMON_MCTS_SHOWDOWN_WEBSOCKET_H
#define POKEMON_MCTS_SHOWDOWN_WEBSOCKET_H

#include <boost/beast/websocket.hpp>
#include <boost/asio/ip/tcp.hpp>

#include <string>

namespace beast = boost::beast;   // for  <boost/beast/websocket.hpp>
namespace net = boost::asio;      // from <boost/asio.hpp>
using tcp = boost::asio::ip::tcp; // from <boost/asio/ip/tcp.hpp>


class WebSocket {
public:
    /// Establishes a WebSocket connection.
    explicit WebSocket(std::string const host, std::string const port, std::string const target);
    /// Sends a message via the WebSocket.
    void send_message(std::string const message);
    /// Receives a message from the WebSocket.
    std::string receive_message();
    /// Closes the WebSocket connection.
    ~WebSocket();

private:
    // The io_context is required for all I/O
    net::io_context io_context;
    // Performs I/O
    beast::websocket::stream<tcp::socket> ws;
};


#endif //POKEMON_MCTS_SHOWDOWN_WEBSOCKET_H
