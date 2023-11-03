# Steam Discount Bot  
This is a self-hostable discord bot that allows you to have the latest steam discounts or offers in your discord server

-----
## How to use
First of all you need to obtain a token for your discord bot, enable all intents and give read and write permissions to the bot before inviting it to your server, you can use one of the various guides online for that. 
1. Create a file called `config.py` like `config.example.py` and enter your configuration (token and language)
    - Currently supported languages: `english, italian, russian`
2. Install Python3
3. Install virtualenv module
4. Install pm2
5. Setup venv `python3 -m virtualenv venv`
6. Activate venv (in linux: `source venv/bin/activate`)
7. Install requirements: `pip install -r requirements.txt`
8. Start with pm2 `pm2 start steam_discount_bot.py`
    - Future update will provide full docker support
9. Use the command `!help` in a text channel on your discord server for details about how to use the bot

# Custom translation
You can create custom translations by adding entries to the `translations.py` module as did for the already supported languages.
