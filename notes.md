# Pokemon Showdown Notes

## Getting Info

- Use command `>eval [javascript command]`
    - Can probably get any information we need
- `>eval battle.toJSON()` gives battle state
    - Might not be valid JSON
    - Might not have complete information
- Weather: `>eval battle.field.getWeather()` or `>eval battle.field.weather`
- Details for active pokemon: `>eval p1active` or `>eval p2active`
    - Boosts: `>eval p1active.boosts`


### Example output of `>eval battle.toJSON()` (formatted)

```JSON
{
debugMode: false,
strictChoices: false,
formatData: {id: "gen7randombattle"},
gameType: "singles",
activePerHalf: 1,
prngSeed: [30530, 9422, 14025, 43603],
rated: false,
reportExactHP: false,
reportPercentages: true,
supportCancel: true,
faintQueue: [],
inputLog: [
    ">start {"formatid":"gen7randombattle","seed":[30530,9422,14025,43603]}",
    ">player p1 {"name":"Alice","seed":[42902,12192,59693,35989]}",
    ">player p2 {"name":"Bob","seed":[6311,6150,25902,7464]}",
    ">p1 switch 3", ">p2 switch 4", ">p1 move nastyplot",
    ">p2 move swordsdance", ">eval battle.format",
    ">eval battle.toString()", ">eval battle.toJSON()"
],
messageLog: [],
sentLogPos: 49,
sentEnd: false,
requestState: "move",
turn: 3,
midTurn: false,
started: true,
ended: false,
effect: {id: ""},
effectData: {id: ""},
event: {id: ""},
events: null,
eventDepth: 0,
activeMove: null,
activePokemon: null,
activeTarget: null,
lastMove: {hit: 1, totalDamage: 0, move: "[Move:swordsdance]"},
lastMoveLine: 39,
lastSuccessfulMoveThisTurn: null,
lastDamage: 0,
abilityOrder: 5,
field: {
    weather: "desolateland",
    weatherData: {
        id: "desolateland",
        source: "[Pokemon:p2a]",
        sourceSlot: "p2a",
        target: "[Field]"
    },
    terrain: "",
    terrainData: {id: ""},
    pseudoWeather: {sleepclausemod: {...}}
},
sides: [
    {
        foe: "[Side:p2]",
        allySide: null,
        lastSelectedMove: "nastyplot",
        id: "p1",
        n: 0,
        name: "Alice",
        avatar: "",
        maxTeamSize: 6,
        active: ["[Pokemon:p1a]"],
        pokemonLeft: 6,
        faintedLastTurn: null,
        faintedThisTurn: null,
        zMoveUsed: false,
        dynamaxUsed: true,
        sideConditions: {},
        slotConditions: [{}],
        lastMove: null,
        pokemon: [{...}, {...}, {...}, {...}, {...}, {...}],
        team: "321456",
        choice: {...}
    },
    {
        foe: "[Side:p1]",
        allySide: null,
        lastSelectedMove: "swordsdance",
        id: "p2",
        n: 1,
        name: "Bob",
        avatar: "",
        maxTeamSize: 6,
        active: ["[Pokemon:p2a]"],
        pokemonLeft: 6,
        faintedLastTurn: null,
        faintedThisTurn: null,
        zMoveUsed: false,
        dynamaxUsed: true,
        sideConditions: {},
        slotConditions: [{}],
        lastMove: null,
        pokemon: [{...}, {...}, {...}, {...}, {...}, {...}],
        team: "423156",
        choice: {...}
    }
],
prng: [55873, 62506, 35988, 37585],
hints: [],
log: [
    "|t:|1619011430",
    "|gametype|singles",
    "|player|p1|Alice||",
    "|player|p2|Bob||",
    "|teamsize|p1|6",
    "|teamsize|p2|6",
    "|gen|7",
    "|tier|[Gen 7] Random Battle",
    "|rule|Sleep Clause Mod: Limit one foe put to sleep",
    "|rule|HP Percentage Mod: HP is shown in percentages",
    "|",
    "|t:|1619011439",
    "|start",
    "|split|p1",
    "|switch|p1a: Illumise|Illumise, L88, F|258/258",
    "|switch|p1a: Illumise|Illumise, L88, F|100/100",
    "|split|p2",
    "|switch|p2a: Klinklang|Klinklang, L86|243/243",
    "|switch|p2a: Klinklang|Klinklang, L86|100/100",
    "|turn|1",
    "|",
    "|t:|1619011676",
    "|split|p2",
    "|switch|p2a: Groudon|Groudon, L76|277/277",
    "|switch|p2a: Groudon|Groudon, L76|100/100",
    "|detailschange|p2a: Groudon|Groudon-Primal, L76",
    "|-primal|p2a: Groudon",
    "|-weather|DesolateLand|[from] ability: Desolate Land|[of] p2a: Groudon",
    "|split|p1",
    "|switch|p1a: Persian|Persian-Alola, L88, M|258/258",
    "|switch|p1a: Persian|Persian-Alola, L88, M|100/100",
    "|",
    "|-weather|DesolateLand|[upkeep]",
    "|upkeep",
    "|turn|2",
    "|",
    "|t:|1619011861",
    "|move|p1a: Persian|Nasty Plot|p1a: Persian",
    "|-boost|p1a: Persian|spa|2",
    "|move|p2a: Groudon|Swords Dance|p2a: Groudon",
    "|-boost|p2a: Groudon|atk|2",
    "|",
    "|-weather|DesolateLand|[upkeep]",
    "|upkeep",
    "|turn|3",
    "||>>> battle.format",
    "||<<< Format([Gen 7] Random Battle)",
    "||>>> battle.toString()",
    "||<<< "Battle: [Gen 7] Random Battle"",
    "||>>> battle.toJSON()"
],
queue: [],
formatid: "gen7randombattle"
}
```


# From Daniel

In battle.py we have the classes Battle, Battler and Pokemon.
Battle holds the complete battle info with the two users (as Battler classes).
In run_battle.py the function pokemon_battle creates a battle and runs it until the end

# New Month

On July 1 the custom game (own teams) did not work anymore.
This is because it tries to get game stats from the previous
month but somehow this data is not available at that point. 
I changed in ```pmariglia/data/parse_smogon_stats.py``` the ```month```
variable in the function ```get_smogon_stats_file_name```. Need
to see if this now happens every month.