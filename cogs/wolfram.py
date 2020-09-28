import discord
from discord.ext import commands
from discord.ext.commands import Bot
import asyncio
import wolframalpha, os


wolframclient = wolframalpha.Client(os.environ.get('wolframid'))
#----------------------------------------------+
#                 Functions                    |
#----------------------------------------------+

class wolfram(commands.Cog):
    def __init__(self, client):
        self.client = client

    #----------------------------------------------+
    #                   Events                     |
    #----------------------------------------------+
    @commands.Cog.listener()
    async def on_ready(self):
        print(f">> wolfram cog is loaded")

    #----------------------------------------------+
    #                  Commands                    |
    #----------------------------------------------+
    @commands.cooldown(1, 2, commands.BucketType.member)
    @commands.command(
        aliases=["query"],
        help="магия вольфрама",
        description="воспользоваться Wolfram|Alpha",
        usage="Запрос",
        brief="All roots x^2 - 1 = 0" )
    async def solve(self, ctx, *, query):
        answer = ""
        async with ctx.channel.typing():
            res = wolframclient.query(query)
            try:
                answer = next(res.results).text
            except (AttributeError, StopIteration):
                reply = discord.Embed(
                    title="❌ | Чё за приколы",
                    description="Если честно - запрос не слишком классный, я ничего не понял.",
                    color=discord.Color.dark_red()
                )
                reply.set_footer(text=str(ctx.author), icon_url=ctx.author.avatar_url)
                await ctx.send(embed=reply)
                
        if answer != "":
            reply = discord.Embed(
                title=f":gear: | Запрос: `{query}`",
                description=f"**Wolfram|Alpha**\n\n{answer}"[:2048],
                color=discord.Color.orange()
            )
            reply.set_footer(text=str(ctx.author), icon_url=ctx.author.avatar_url)
            await ctx.send(embed=reply)


    #----------------------------------------------+
    #                   Errors                     |
    #----------------------------------------------+


def setup(client):
    client.add_cog(wolfram(client))