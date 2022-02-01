# Christina Network 2.x
 A tiny project that hopes to bring u convenience & happiness :D

*DO NOT TRY to understand any part of the code cuz its all a piece of sht but i have no time at all to maintain it*

## How?
A QQ bot powered by [mirai](https://github.com/mamoe/mirai) and [mirai-api-http](https://github.com/project-mirai/mirai-api-http), using `Python` to process messages and events.

### Why 2.x?

Christina 1.x can only fit `mirai-api-http` 1.x and has a terrible code style that I really would like to change that as soon as I can :D

## Usage

First run `pip install -r requirements.txt` or `pip3 install -r requirements.txt` to install the requirements.

### config.json

Create a `config.json` in the same directory with `main.py`.

```json5
{
    // MiraiApiHttp host
    "host": "localhost:8080",
    
    // Your bot's QQ account
    "account": 1234567890,
    
    // MiraiApiHttp's verifyKey that you configured
    "verifyKey": "YOURVERIFYKEY",
    
    // The port of the HTTP API that you want
    "httpapi_port": 8000,

    "mcservers": {
        "1234567890": ["foo", "bar"],
        "9876543210": ["foo"]
    },

    "mcaddrs": {
        "foo": "srv.mc.example.org",
        "bar": "mc.example.org:23333"
    }
}
```

Then start `main.py` and `httpapi.py` separately. Done!
