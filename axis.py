import discord
from discord.ext import commands
import asyncio
import os, datetime
from pymongo import MongoClient

#--------------------------------------------+
#                Connections                 |
#--------------------------------------------+
bot_token = str(os.environ.get("bot_token"))
# db_token = str(os.environ.get("db_token"))
prefix = "m!"
client = commands.Bot(command_prefix=prefix)
client.remove_command("help")


#--------------------------------------------+
#                 Variables                  |
#--------------------------------------------+
started_at = datetime.datetime.utcnow()


#--------------------------------------------+
#                 Functions                  |
#--------------------------------------------+
from functions import visual_delta


#--------------------------------------------+
#                   Events                   |
#--------------------------------------------+
@client.event
async def on_ready():
    print(f"Bot: {client.user}")


#--------------------------------------------+
#                  Commands                  |
#--------------------------------------------+
@client.command()
@commands.is_owner()
async def logout(ctx):
    await ctx.send("```>> Logging out...```")
    await client.logout()


@client.command()
async def stats(ctx):
    uptime = datetime.datetime.utcnow() - started_at
    total_members = 0
    total_servers = 0
    
    for guild in client.guilds:
        total_members += guild.member_count
        total_servers += 1
    
    reply = discord.Embed(
        title="🌍 Статистика бота",
        color=discord.Color.blue()
    )
    reply.add_field(name="🗂 Серверов", value=f"> {total_servers}", inline=False)
    reply.add_field(name="👥 Пользователей", value=f"> {total_members}", inline=False)
    reply.add_field(name="🕑 Аптайм", value=f"> {visual_delta(uptime)}")
    reply.add_field(name="🛰 Пинг", value=f"> {client.latency * 1000:.0f}", inline=False)
    reply.set_thumbnail(url=str(client.user.avatar_url))
    await ctx.send(embed=reply)


client.run(bot_token)