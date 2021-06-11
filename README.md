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