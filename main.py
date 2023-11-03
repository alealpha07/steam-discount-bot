# https://discord.com/developers/applications
# https://store.steampowered.com/api/featuredcategories/?l=italian
import discord
import requests
import datetime
import json
import asyncio
from discord.ext import commands
from config import TOKEN
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

working_channel = None
delay_interval = 3600


# Funzione per eseguire lo scraping
async def run_command():
    while True:
        global delay_interval, working_channel
        if working_channel is not None:
            channel = bot.get_channel(working_channel)
            await channel.purge(limit=99)
        await scrape_games()
        await asyncio.sleep(delay_interval)


# event bot ready
@bot.event
async def on_ready():
    loop = asyncio.get_event_loop()
    loop.create_task(run_command())
    print(f'Bot is ready as {bot.user.name}')


@bot.command()
async def init(ctx):
    global working_channel
    working_channel = ctx.channel.id
    await ctx.send("Canale corrente impostato per l' invio delle offerte sui giochi")


@bot.command()
async def delay(ctx, seconds: int):
    global delay_interval
    delay_interval = seconds
    await ctx.send(f"Delay di aggiornamento delle offerte impostato a {delay_interval} secondi")


@bot.command()
async def reload(ctx):
    global working_channel
    if working_channel is not None:
        channel = bot.get_channel(working_channel)
        await channel.purge(limit=99)
    await scrape_games()


async def scrape_games():
    response = requests.get("https://store.steampowered.com/api/featuredcategories/?l=italian")
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
                    description=f'~~{full_price}€~~ -> **{final_price}€**\t\tL\' offerta termina il `{expire_date.strftime("%d/%m/%y")}`\n[Apri nel browser ↗]({store_url})',
                    color=0x3498db
                )
                embed.set_image(url=image_url)
                await channel.send(embed=embed)


@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="Comandi del Bot",
        description="Ecco la lista dei comandi disponibili:",
        color=0x3498db
    )
    embed.add_field(name="!init", value="Imposta il canale corrente per l'invio delle offerte sui giochi.", inline=False)
    embed.add_field(name="!delay [secondi]", value="Imposta il delay di aggiornamento delle offerte in secondi.", inline=False)
    embed.add_field(name="!reload", value="Ricarica lista delle offerte e le invia nel canale impostato.", inline=False)

    await ctx.send(embed=embed)

# start the bot
bot.run(f'{TOKEN}')
