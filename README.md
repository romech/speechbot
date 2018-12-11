# speechbot
[![Build status](https://ci.appveyor.com/api/projects/status/l53ap673knq8q4hi/branch/master?svg=true)](https://ci.appveyor.com/project/romech/speechbot/branch/master)

*Written fully at First Line Software Hackaton.*

Telegram bot that transforms voice recordings. Not by itself, but using an API.


### How to adopt
1. Set up a server with some http endpoints that accepts .ogg files in request and reply with modified audio.
2. `pip install -r requirements.txt`
3. Create a Telegram bot
4. Build a config file like this one:
```buildoutcfg
connect-keys.yaml

connection:
  token: 'TELEGRAM-T0KEN'
  proxy:
    https: 'socks5://uid:pwd@host:port'

endpoints:
  Male: 'http://host/voice1'
  Female: 'http://host/voice2'
  ...
  
duration-limit: 300
``` 

5. Do anything you need with dialogues.yaml 
