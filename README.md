# Deep Pokemon MCTS

## Data collection pipeline

In ```pmariglia/envs``` you can find the configuration
files for the challenger and challenge accepter agent. 
For the challenger you need to use a registered user account
with password to get the admin rights. You also need to
add this username to ```showdown/usergroups.csv```. <br><br>
The team configurations are located in ```teams``` where
for the simple setting currently ```only_damage_two_pokemon```
is used. For now the teams are randomily selected at startup.

### With Docker and Docker compose

You can use docker compose to automatically setup the
data collection pipeline and start collecting data
```
docker-compose up --build
```
starts the showdown server and two agents 
challenging each other.

## Dataloader

### Current supported features

* `active_moves` : The move ids of the players active pokemon
* `chosen_move`  : The chosen move by pmariglia
* `moves_damage` : The base damage for each move
* `hp_active`    : The health points of players active pokemon
* `hp_all` : The health points of players whole team
* `stats_active` : The attack, defense, etc. for players active pokemon
* `stats_all` : The attack, defense, etc. for players whole team
* `type_active` : The pokemon type of the active pokemon
* `type_all` : The types of all pokemon in the team
* `move_type_active` : The move types of the active pokemon
* `move_type_all` : The move types of all moves in the team