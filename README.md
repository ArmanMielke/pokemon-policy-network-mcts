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

* `active_hp` : the hp of the active pokemon
* `all_hp` : hp of all pokemon in a team
* `active_move` : the move ids of active pokemon
* `all_move` : all moves of the team
* `active_move_damage` : move damages of active pokemon
* `all_move_damage` : move damages of complete team
* `active_move_type` : move element type of active pokemon
* `all_move_type` : move element types of team
* `active_move_category` : indicator if physical or special attack
* `all_move_category` : physical/special indicator complete team
* `active_stats` : attack, defense, etc. of active pokemon
* `all_stats` : attack, defense, etc. of team
* `chosen_move` : the move id chosen by pmariglia
* `pokemon` : list of all pokemon in a team with following features
 * `is_active`
 * `hp`
 * `stats`
 * `type`
 * `move`
 * `move_type`
 * `move_damage`
 * `move_category`
