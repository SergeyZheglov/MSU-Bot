import discord
from discord.ext import commands
import asyncio
import os, datetime

#--------------------------------------------+
#                Connections                 |
#--------------------------------------------+
bot_token = str(os.environ.get("bot_token"))
prefix = "m!"
intents = discord.Intents.all()
client = commands.Bot(command_prefix=prefix, intents=intents)
client.remove_command("help")


#--------------------------------------------+
#                 Variables                  |
#--------------------------------------------+
started_at = datetime.datetime.utcnow()


#--------------------------------------------+
#                 Functions                  |
#--------------------------------------------+
from functions import visual_delta, has_instance, display_perms, CooldownResetSignal


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
        title="🌍 Состояние бота",
        color=discord.Color.blue()
    )
    reply.add_field(name="🗂 Серверов", value=f"> {total_servers}", inline=False)
    reply.add_field(name="👥 Пользователей", value=f"> {total_members}", inline=False)
    reply.add_field(name="🕑 Аптайм", value=f"> {visual_delta(uptime)}")
    reply.add_field(name="🛰 Пинг", value=f"> {client.latency * 1000:.0f}", inline=False)
    reply.set_thumbnail(url=str(client.user.avatar_url))
    await ctx.send(embed=reply)


@commands.cooldown(1, 1, commands.BucketType.member)
@client.command(aliases=["h"], help="узнать подробнее о каждой команде")
async def help(ctx, *, cmd_s=None):
    p = ctx.prefix
    
    if cmd_s is None:
        cog_desc = f"> `{p}cmds main`\n"
        for _cog in client.cogs:
            cog_desc += f"> `{p}cmds {_cog}`\n"
        reply = discord.Embed(
            title="📖 Категории команд",
            description=(
                f"Просмотреть каждую категорию:\n{cog_desc}\n"
                f"Подробнее о команде: `{p}help нужная команда`"
            ),
            color=discord.Color.blurple()
        )
        reply.set_footer(text=str(ctx.author), icon_url=ctx.author.avatar_url)
        await ctx.send(embed=reply)

    else:
        cmd = None
        for c in client.commands:
            if cmd_s in [c.name, *c.aliases]:
                cmd = c
                break
        
        if cmd is None:
            reply = discord.Embed(
                title="🔎 | Не нашёл команду, увы",
                description=f"У меня нет команды `{p}{cmd_s}`, может, Вы ошиблись?",
                color=discord.Color.blurple()
            )
            reply.set_footer(text=str(ctx.author), icon_url=ctx.author.avatar_url)
            await ctx.send(embed=reply)
        
        else:
            description = "`-`"; usage = "`-`"; brief = "`-`"; aliases = "-"
            if cmd.description != "":
                description = cmd.description
            if cmd.usage is not None:
                usage = "\n> ".join( [f"`{p}{cmd} {u}`" for u in cmd.usage.split("\n")] )
            if cmd.brief is not None:
                brief = "\n> ".join( [f"`{p}{cmd} {u}`" for u in cmd.brief.split("\n")] )
            if len(cmd.aliases) > 0:
                aliases = ", ".join(cmd.aliases)
            
            reply = discord.Embed(
                title = f"❓ Об аргументах `{p}{cmd}`",
                description = (
                    f"**Описание:** {description}\n"
                    f"**Использование:** {usage}\n"
                    f"**Примеры:** {brief}\n\n"
                    f"**Синонимы:** `{aliases}`"
                )
            )
            reply.set_footer(text=str(ctx.author), icon_url=ctx.author.avatar_url)
            await ctx.send(embed=reply)

            try:
                ctx.command.reset_cooldown(ctx)
            except Exception:
                pass


@commands.cooldown(1, 1, commands.BucketType.member)
@client.command(aliases=["commands"], help="список всех команд из категории")
async def cmds(ctx, *, section=None):
    p = ctx.prefix
    if section is None:
        cog_desc = f"> `{p}cmds main`\n"
        for _cog in client.cogs:
            cog_desc += f"> `{p}cmds {_cog}`\n"
            
        reply = discord.Embed(
            title="📖 Категории команд",
            description=(
                f"Просмотреть каждую категорию:\n{cog_desc}\n"
                f"Подробнее о команде: `{p}help нужная команда`"
            ),
            color=discord.Color.blurple()
        )
        reply.set_footer(text=str(ctx.author), icon_url=ctx.author.avatar_url)
        await ctx.send(embed=reply)
    
    else:
        cog_found = None
        sec = section.lower()
        if "main".startswith(sec):
            cog_found = "main"
            cog_commands = [c for c in client.commands if c.cog is None]
        else:
            for _cog in client.cogs:
                if str(_cog).lower().startswith(sec):
                    cog_found = _cog
                    cog_commands = client.get_cog(_cog).get_commands()
                    break
        
        if cog_found is None:
            reply = discord.Embed(
                title="🔎 | Не нашёл категорию, увы",
                description=f"У меня нет категории `{section}`, может стоит проверить написание?",
                color=discord.Color.blurple()
            )
            reply.set_footer(text=str(ctx.author), icon_url=ctx.author.avatar_url)
            await ctx.send(embed=reply)
        
        else:
            desc = ""
            for cmd in cog_commands:
                if cmd.help is None:
                    cmdhelp = "[-]"
                else:
                    cmdhelp = cmd.help
                desc += f"`{p}{cmd}` - {cmdhelp}\n"
            reply = discord.Embed(
                title=f"📁 | Категория команд `{cog_found}`",
                description=f"Подробнее о команде: `{p}help нужная команда`\n\n{desc}",
                color=discord.Color.blurple()
            )
            reply.set_footer(text=str(ctx.author), icon_url=ctx.author.avatar_url)
            await ctx.send(embed=reply)


@client.command()
@commands.has_permissions(administrator=True)
async def say(ctx, *, text):
    reply = discord.Embed(
        description=text,
        color=ctx.guild.me.color
    )
    await ctx.send(embed=reply)
    await ctx.message.delete()

#----------------------------------------------+
#                   Errors                     |
#----------------------------------------------+
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        
        def TimeExpand(time):
            if time//60 > 0:
                return str(time//60)+'мин '+str(time%60)+' сек'
            elif time > 0:
                return str(time)+' сек'
            else:
                return f"0.1 сек"
        
        cool_notify = discord.Embed(
                title='⏳ Подождите немного',
                description = f"Осталось {TimeExpand(int(error.retry_after))}"
            )
        await ctx.send(embed=cool_notify)
    
    elif isinstance(error, commands.MissingPermissions):
        if ctx.author.id != 0:
            reply = discord.Embed(
                title="❌ Недостаточно прав",
                description=f"Необходимые права:\n{display_perms(error.missing_perms)}",
                color=discord.Color.dark_red()
            )
            reply.set_footer(text=str(ctx.author), icon_url=ctx.author.avatar_url)
            await ctx.send(embed=reply)
        else:
            try:
                await ctx.reinvoke()
            except Exception as e:
                await on_command_error(ctx, e)
    
    elif isinstance(error, commands.MissingRequiredArgument):
        p = ctx.prefix
        cmd = ctx.command
        reply = discord.Embed(
            title=f"🗃 `{cmd.name}`: недостаточно аргументов",
            description=(
                "Как правильно?\n"
                f"**Использование:** `{p}{cmd.name} {cmd.brief}`\n"
                f"**Пример:** `{p}{cmd.name} {cmd.usage}`\n\n"
                f"**Подробнее об этой команде:** `{p}help {cmd}`"
            ),
            color=discord.Color.dark_red()
        )
        reply.set_footer(text=str(ctx.author), icon_url=ctx.author.avatar_url)
        await ctx.send(embed=reply)

        ctx.command.reset_cooldown(ctx)

    elif isinstance(error, commands.BadArgument):
        start, middle, rest = str(error).split(maxsplit=2)
        if '"' in middle:
            arg = middle
            _type = start.lower()
            ru_msgs = {
                "role": f"Роль {arg} не была найдена на сервере.",
                "member": f"Участник {arg} не был найден на сервере.",
                "user": f"Пользователь {arg} не был найден, возможно, у меня с ним нет общих серверов."
            }
            desc = ru_msgs.get(_type, "Кажется, введённые аргументы не соответствуют требуемому формату.")
        else:
            if rest.split(maxsplit=1)[0] == '"int"':
                desc = "Укажите целое число, например `5`."
            else:
                desc = "Кажется, введённые аргументы не соответствуют требуемому формату."
        reply = discord.Embed(
            title=f"📍 | Что-то введено неправильно",
            description=desc,
            color=discord.Color.dark_red()
        )
        reply.set_footer(text=str(ctx.author), icon_url=ctx.author.avatar_url)
        await ctx.send(embed=reply)

        ctx.command.reset_cooldown(ctx)

    elif isinstance(error, commands.CommandNotFound):
        pass

    elif isinstance(error, CooldownResetSignal):
        ctx.command.reset_cooldown(ctx)

    else:
        print(error)

#----------------------------------------------+
#                  Loading Cogs                |
#----------------------------------------------+
for file_name in os.listdir("./cogs"):
    if file_name.endswith(".py"):
        client.load_extension(f"cogs.{file_name[:-3]}")


client.run(bot_token)
