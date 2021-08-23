
## Collection pipeline

Our collection pipeline consists of multiple pmariglia agents
in different docker container handled with docker-compose. To create
a correct and useable setup please use the `create-data-pipeline.sh`
script. Most of the configuration options are not important to change
and can be ignored for first test situations. <br><br>

Some options that may be of interest are: <br>
* `BATTLE_BOT`: the battle option used by pmariglia. Some options here can
be `random`, `most_damage` or `most_base_damage`. For further information 
have a look at the pmariglia github page or the directory `pmariglia/shodown/battle_bots`.

* `GAME_MODE`: the game mode which will be played. In theory every mode
supported by Pokemon showdown can be used here but we only tested and support
`gen8randombattle`, `gen8randombattle@@@Dynamax Clause` (game mode where
the dynamaxing is not allowed) and `gen8customgame@@@Dynamax Clause` (for custom
teams, see the `teams` folder).

* `COUNT`: the amount of agent pairs created. A pair consists of a challenger
agent and a accepter agent.

* `RUN_COUNT`: how many games are played before the agents shutdown.

## Dataloader

Our dataloader is a custom implementation of the PyTorch dataloader taking
the collected game data from our collection pipeline and converting it
into single-turn samples. To speedup the startup time we cache the
conversion the first time the training is started so future training
processes don't need to convert the data again. This leads to a small overhead
the first time training is started on a new dataset. The converted
data can be found in the same directory as the original data in the subfolder
`converted`. <br><br>

The dataloader and dataconverter are located in
```
policynet/dataloader/dataset.py
policynet/dataloader/dataconverter.py
```

### Current supported features

Our configuration allows the change of features used for training. 
The features can be separately for player 1 (`p1`; our agent) and
player 2 (`p2`; the opponent). Current supported features are:

 * `is_active`  Is the Pokemon the active Pokemon
 * `hp` The health points of the Pokemon
 * `stats` The attack, defense etc. of the Pokemon 
 * `type` The element type (e.g. Water, Fire ...) of the Pokemon
 * `move` The move ids of the Pokemon
 * `move_type` The move elements of the Pokemon
 * `move_damage` The move damages of the Pokemon
 * `move_category` The move categories (physical or special) 
