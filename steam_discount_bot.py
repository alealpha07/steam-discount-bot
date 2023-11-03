import discord
import requests
import datetime
import asyncio
from discord.ext import commands
from config import TOKEN, LANGUAGE
from translations import languages

# Get language translations
language = languages.get(LANGUAGE)

# Create Discord bot with all intents
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# Initialize variables
working_channel = None
delay_interval = 3600

# Function to periodically fetch games
async def run_command():
    while True:
        global delay_interval, working_channel
        if working_channel is not None:
            channel = bot.get_channel(working_channel)
            await channel.purge(limit=99)
        await get_games()
        await asyncio.sleep(delay_interval)

# Bot initialization event
@bot.event
async def on_ready():
    loop = asyncio.get_event_loop()
    loop.create_task(run_command())
    print(f'Bot is ready as {bot.user.name}')

# Command to set the working channel
@bot.command()
async def init(ctx):
    global working_channel
    working_channel = ctx.channel.id
    await ctx.send(language.get('command_init_message'))

# Command to set the delay interval
@bot.command()
async def delay(ctx, seconds: int):
    global delay_interval
    delay_interval = seconds
    await ctx.send(f"{language.get('command_delay_message')} {delay_interval} {language.get('general_seconds')}")

# Command to manually reload games
@bot.command()
async def reload(ctx):
    global working_channel
    if working_channel is not None:
        channel = bot.get_channel(working_channel)
        await channel.purge(limit=99)
    await get_games()

# Function to fetch games from Steam API
async def get_games():
    response = requests.get(f"https://store.steampowered.com/api/featuredcategories/?l={LANGUAGE}")
    for category in [x for x in response.json().values() if
                     x != None and isinstance(x, dict) and x.get("id") != None and (
                             x.get("id") == "cat_dailydeal" or x.get("id") == "cat_specials")]:
        for item in category.get("items"):
            image_url = item.get("header_image")
            game_title = item.get("name")
            full_price = item.get("original_price") / 100
            final_price = item.get("final_price") / 100
            id = item.get("id")
            store_url = "https://store.steampowered.com/app/" + str(id)
            expire_date = datetime.datetime.today() + datetime.timedelta(days=1) if category.get(
                "id") == "cat_dailydeal" else datetime.datetime.fromtimestamp(item.get("discount_expiration"))
            global working_channel
            if working_channel is not None:
                channel = bot.get_channel(working_channel)
                embed = discord.Embed(
                    title=game_title,
                    description=f'~~{full_price}€~~ -> **{final_price}€**\t\t '
                                f'{language.get("embed_description_end_offer")} '
                                f'`{expire_date.strftime("%d/%m/%y")}`\n'
                                f'[{language.get("embed_description_open_in_browser")} ↗]({store_url})',
                    color=0x3498db
                )
                embed.set_image(url=image_url)
                await channel.send(embed=embed)

# Command to display help information
@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title=language.get("command_help_title"),
        description=language.get("command_help_description"),
        color=0x3498db
    )
    embed.add_field(name="!init", value=language.get("command_help_init"), inline=False)
    embed.add_field(name=f"!delay [{language.get('general_seconds')}]", value=language.get("command_help_delay"),
                    inline=False)
    embed.add_field(name="!reload", value=language.get("command_help_reload"), inline=False)

    await ctx.send(embed=embed)

# Start the bot
bot.run(f'{TOKEN}')
