#ifndef POKEMON_MCTS_SHOWDOWN_WEBSOCKET_H
#define POKEMON_MCTS_SHOWDOWN_WEBSOCKET_H

#include <boost/beast/websocket.hpp>
#include <boost/asio/ip/tcp.hpp>

#include <string>

namespace websocket = boost::beast::websocket; // from <boost/beast/websocket.hpp>
namespace net = boost::asio;                   // from <boost/asio.hpp>
using tcp = boost::asio::ip::tcp;              // from <boost/asio/ip/tcp.hpp>


class ShowdownWebsocket {
public:
    /// Establishes a WebSocket connection.
    ///
    /// @param host
    /// @param port
    explicit ShowdownWebsocket(std::string const host, std::string const port);

    /// Sends a message via the WebSocket and receives the response.
    ///
    /// @param message
    /// @return The response.
    std::string send_message(std::string const message);

    /// Closes the WebSocket connection.
    ~ShowdownWebsocket();

private:
    // The io_context is required for all I/O
    net::io_context io_context;
    // Performs I/O
    websocket::stream<tcp::socket> ws;
};


#endif //POKEMON_MCTS_SHOWDOWN_WEBSOCKET_H
