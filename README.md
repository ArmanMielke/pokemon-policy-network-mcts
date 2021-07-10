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

First we need to create the configuration files for the agents. In
the project root directory run:
```
python3 pmariglia/envs/create_envs.py --teamdir physical_special --dest pmariglia/envs
```
(NOTE: you can change `--teamdir` to any of the folder names in the folder `teams`)

Next we need to setup the docker-compose file. Run in the root dir of the project:
```
python3 create_compose.py
```
This will create a correctly configured `docker-compose.yml`. Finally the 
collection process can be started with:
```
docker-compose up --build
```
This will build the showdown server and 32 agents 
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
