#include "showdown_websocket.h"

#include <boost/beast/core.hpp>
#include <boost/beast/websocket.hpp>
#include <boost/asio/connect.hpp>
#include <boost/asio/ip/tcp.hpp>

#include <cstdlib>
#include <iostream>
#include <string>

namespace beast = boost::beast;         // from <boost/beast.hpp>
namespace http = beast::http;           // from <boost/beast/http.hpp>
namespace websocket = beast::websocket; // from <boost/beast/websocket.hpp>
namespace net = boost::asio;            // from <boost/asio.hpp>
using tcp = boost::asio::ip::tcp;       // from <boost/asio/ip/tcp.hpp>


// Adapted from https://www.boost.org/doc/libs/develop/libs/beast/doc/html/beast/quick_start/websocket_client.html


ShowdownWebsocket::ShowdownWebsocket(std::string const host, std::string const port) : ws{io_context} {
    // These objects perform our I/O
    tcp::resolver resolver{io_context};

    // Look up the domain name
    auto const results = resolver.resolve(host, port);
    // Make the connection on the IP address we get from a lookup
    auto ep = net::connect(ws.next_layer(), results);

    // Update the host_ string. This will provide the value of the Host HTTP header during the WebSocket handshake.
    // See https://tools.ietf.org/html/rfc7230#section-5.4
    std::string const host_with_port = host + ':' + std::to_string(ep.port());

    // Set a decorator to change the User-Agent of the handshake
    this->ws.set_option(websocket::stream_base::decorator(
        [](websocket::request_type& req) {
            req.set(http::field::user_agent, std::string(BOOST_BEAST_VERSION_STRING) + " websocket-client-coro");
        }
    ));

    // Perform the websocket handshake
    this->ws.handshake(host_with_port, "/");
}

void ShowdownWebsocket::send_message(std::string const message) {
    // Send the message
    this->ws.write(net::buffer(message));
}

std::string ShowdownWebsocket::receive_message() {
    // This buffer will hold the incoming message
    beast::flat_buffer buffer;
    // Read a message into our buffer
    this->ws.read(buffer);

    // Convert the ConstBufferSequence to a string
    return beast::buffers_to_string(buffer.data());
}

ShowdownWebsocket::~ShowdownWebsocket() {
    // Close the WebSocket connection
    this->ws.close(websocket::close_code::normal);
    // If we get here then the connection is closed gracefully
    std::cout << "[ShowdownWebsocket] Connection closed." << std::endl;
}
