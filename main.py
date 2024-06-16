import json,discord
from discord.ext import commands, tasks
from datetime import *
from cogs import bolletta
import asyncio, LeagueOfLegend

print("Mi sto avviando...")
 

client = commands.Bot(command_prefix=("."), help_command=None, case_insensitive=True,intents=discord.Intents.all())


async def setup(client):
    await client.add_cog(bolletta(client ,utili))

with open("utiliti.json","r") as file:
    utili = json.load(file)


@tasks.loop(seconds=30)
async def Unix_refresh():
    LeagueOfLegend.unix()


@client.event
async def on_ready():
    Unix_refresh.start() #to start the looping task



asyncio.run(setup(client))


client.run(utili["TOKEN"])

