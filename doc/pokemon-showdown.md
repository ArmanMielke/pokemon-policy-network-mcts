# Pokemon Showdown Notes

## Allowing Console Access

This is required for the `/eval`, `/evalbattle`, ... commands, otherwise you would get this error when using them:
```
/eval - Requires console access, please set up `Config.consoleips`.
```

In the Showdown directory, create a file named `config/usergroups.csv`, containing
```
USER,&
```
where `USER` is a registered username.
After re-starting the server, that user will become administrator and will therefore have console access.
If you log in to the web interface and click on your username on the top right, it should say "Global Administrator (&)" in the little window that pops up.

`&` is the symbol Showdown uses for the administrator role.
See the very bottom of `config/config.js` for what admins can do and what other roles there are.


## Getting Info During a Battle

These commands are for use by an admin in a battle room.
You can type them in the chat when using the web interface, or send `<battle room name>|<command>` when connected via a WebSocket.
The battle room name is something like `battle-gen8randombattle-45`.
When running the battle simulator on the command line, replace `/evalbattle` with `>eval`.

- Use command `/evalbattle [javascript command]`
    - Can probably get any information we need
- The `battle` object holds the current game state
    - E.g. weather: `/evalbattle battle.field.getWeather()` or `/evalbattle battle.field.weather`
    - See `battle-to-json-example.json` for what the `battle` object looks like
- Shortcut for details of the active Pokémon: `/evalbattle p1active` or `/evalbattle p2active`
    - E.g. boosts: `/evalbattle p1active.boosts`
- `/evalbattle battle.toJSON()` gives the game state as JSON
    - To print the JSON, use `/evalbattle JSON.stringify(battle.toJSON())`
        - Otherwise anything that is more than 3 or 4 levels deep is replaced with `...`
    - `battle.constructor.fromJSON({...})` can be used to turn JSON back into a `Battle` object
        - Cannot easily be applied to the actual battle :/
    - Relevant GitHub issues
        - [Issue where Battle toJSON/fromJSON was requested](https://github.com/smogon/pokemon-showdown/issues/5270)
        - [PR where Battle toJSON/fromJSON was implemented](https://github.com/smogon/pokemon-showdown/pull/5427)


## Reproducing the Game State

- [Relevant GitHub issue](https://github.com/smogon/pokemon-showdown/issues/8105)
- Use `/evalbattle battle.inputLog.join('\n')` to get a list of previous inputs
    - This also contains the RNG seed, so that everything is deterministic
- This list can be applied to Pokémon Showdown's command line battle simulator
    - Simply feed the entire string to the stdin of `pokemon-showdown simulate-battle`
    - This reproduces the exact state of the original battle
- The same instance of `pokemon-showdown simulate-battle` can be re-used multiple times
