#ifndef POKEMON_MCTS_SHOWDOWN_LOGIN_REQUEST_H
#define POKEMON_MCTS_SHOWDOWN_LOGIN_REQUEST_H

#include <string>


/// Sends a HTTP POST request in order to log in to Pokémon Showdown.
///
/// @param username
/// @param challstr: A string sent earlier by the server.
/// @return Assertion required to finalise the login process.
std::string send_login_request(std::string const username, std::string const challstr);


#endif //POKEMON_MCTS_SHOWDOWN_LOGIN_REQUEST_H
