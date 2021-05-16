#include "showdown_login_request.h"

#include <boost/beast/core.hpp>
#include <boost/beast/http.hpp>
#include <boost/beast/version.hpp>
#include <boost/asio/connect.hpp>
#include <boost/asio/ip/tcp.hpp>
#include <boost/lexical_cast.hpp>
#include <nlohmann/json.hpp>

#include <cstdlib>
#include <iostream>
#include <optional>
#include <string>

namespace beast = boost::beast; // from <boost/beast.hpp>
namespace http = beast::http;   // from <boost/beast/http.hpp>
namespace net = boost::asio;    // from <boost/asio.hpp>
using tcp = net::ip::tcp;       // from <boost/asio/ip/tcp.h


std::string const SHOWDOWN_LOGIN_HOST = "play.pokemonshowdown.com";
std::string const SHOWDOWN_LOGIN_PORT = "80";
std::string const SHOWDOWN_LOGIN_TARGET = "/action.php";

// HTTP version 1.1
int const HTTP_VERSION = 11;


std::string construct_request_body(
        std::string const username,
        std::string const challstr,
        std::optional<std::string> const password
) {
    if (password.has_value()) {
        return "act=login&name=" + username + "&pass=" + *password + "&challstr=" + challstr;
    } else {
        return "act=getassertion&userid=" + username + "&challstr=" + challstr;
    }
}

std::string extract_assertion(std::string const response_body, bool const using_password) {
    if (using_password) {
        // skip the first character. for some reason there is a "]" before the actual json
        nlohmann::json response_json = nlohmann::json::parse(response_body.substr(1));
        return response_json["assertion"];
    } else {
        return response_body;
    }
}

std::string send_login_request(
    std::string const username,
    std::string const challstr,
    std::optional<std::string> const password
) {

    // Establish connection
    // ====================

    // The io_context is required for all I/O
    net::io_context ioc;
    // These objects perform our I/O
    tcp::resolver resolver(ioc);
    beast::tcp_stream stream(ioc);

    // Look up the domain name
    auto const results = resolver.resolve(SHOWDOWN_LOGIN_HOST, SHOWDOWN_LOGIN_PORT);
    // Make the connection on the IP address we get from a lookup
    stream.connect(results);


    // Send request
    // ============

    // Set up an HTTP POST request message
    http::request<http::string_body> req{http::verb::post, SHOWDOWN_LOGIN_TARGET, HTTP_VERSION};
    req.set(http::field::host, SHOWDOWN_LOGIN_HOST);
    req.set(http::field::user_agent, BOOST_BEAST_VERSION_STRING);
    req.set(http::field::content_type, "application/x-www-form-urlencoded");
    // send username and challstr
    req.body() = construct_request_body(username, challstr, password);
    req.prepare_payload();

    // Send the HTTP request to the remote host
    http::write(stream, req);


    // Receive response
    // ================

    // This buffer is used for reading and must be persisted
    beast::flat_buffer buffer;
    // Declare a container to hold the response
    http::response<http::dynamic_body> res;
    // Receive the HTTP response
    http::read(stream, buffer, res);

    // Check whether result was OK
    if (res.result() != http::status::ok) {
        std::cout << "[login request] WARN: HTTP Response was not OK, but "
                  << res.result() << " (" << res.result_int() << ")" << std::endl;
    }

    // Read response body
    std::string response_body;
    for (auto seq : res.body().data()) {
        auto* cbuf = net::buffer_cast<const char*>(seq);
        response_body.append(cbuf, net::buffer_size(seq));
    }


    // Close connection
    // ================

    // Gracefully close the socket
    beast::error_code ec;
    stream.socket().shutdown(tcp::socket::shutdown_both, ec);

    // not_connected happens sometimes, so don't bother reporting it.
    if (ec && ec != beast::errc::not_connected) {
        throw beast::system_error{ec};
    }
    // If we get here then the connection is closed gracefully

    return extract_assertion(response_body, password.has_value());
}
