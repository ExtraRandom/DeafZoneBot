```json
{
    "keys": {
        "token": "discord-bot-token"
    },
    "cogs": {
        "fun": true,
        "general": true
    },
    "testing": {
        "debug": true,
        "ids": [
            123456789101112131415
        ]
    }
}
```

### Keys
Token is the Token from discord dev platform that the bot uses to connect

### Cogs
Controls whether certain cogs should be loaded at launch 
(mostly a hold over from old version of bot)

Format is `"cog_name_string": boolean` 

### Testing
Used to control some testing specific functions.

If debug is set to true, and IDs has one or more discord server (guild) id's 
then the bot will only register its commands in those servers. This allows for quicker
registering of commands, great for testing as otherwise 
it is a wait of usually over an hour.
