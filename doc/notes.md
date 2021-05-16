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


## Getting Info

These commands are for use by an admin in a battle room.
You can type them in the chat when using the web interface, or send `<battle room name>|<command>` when connected via a WebSocket.
The battle room name is something like `battle-gen8randombattle-45`.
When running the battle simulator on the command line, replace `/evalbattle` with `>eval`.

- Use command `/evalbattle [javascript command]`
    - Can probably get any information we need
- `/evalbattle battle.toJSON()` gives battle state
    - Might not be valid JSON
    - Might not have complete information
- Weather: `/evalbattle battle.field.getWeather()` or `/evalbattle battle.field.weather`
- Details for active pokemon: `/evalbattle p1active` or `/evalbattle p2active`
    - Boosts: `/evalbattle p1active.boosts`
