import discord
from discord.ext import commands
from discord.ext.commands import Bot
import asyncio

#----------------------------------------------+
#                 Functions                    |
#----------------------------------------------+
from functions import CooldownResetSignal, ReactionRolesConfig


class reaction_roles(commands.Cog):
    def __init__(self, client):
        self.client = client

    #----------------------------------------------+
    #                   Events                     |
    #----------------------------------------------+
    @commands.Cog.listener()
    async def on_ready(self):
        print(f">> reaction_roles cog is loaded")
    

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        server_rr = ReactionRolesConfig(payload.guild_id)
        emojis = server_rr.get_roles(payload.message_id)
        # If emoji is registered
        if str(payload.emoji) in emojis:
            guild = self.client.get_guild(payload.guild_id)
            role = guild.get_role(emojis[str(payload.emoji)])
            # If the role still exists
            if role is not None:
                member = guild.get_member(payload.user_id)
                if role not in member.roles:
                    try:
                        await member.add_roles(role)

                    except Exception:
                        pass

    
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        server_rr = ReactionRolesConfig(payload.guild_id)
        emojis = server_rr.get_roles(payload.message_id)
        # If emoji is registered
        if str(payload.emoji) in emojis:
            guild = self.client.get_guild(payload.guild_id)
            role = guild.get_role(emojis[str(payload.emoji)])
            # If the role still exists
            if role is not None:
                member = guild.get_member(payload.user_id)
                if role in member.roles:
                    try:
                        await member.remove_roles(role)

                    except Exception:
                        pass


    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        rconf = ReactionRolesConfig(payload.guild_id)
        rconf.delete_branch(payload.message_id)

    #----------------------------------------------+
    #                  Commands                    |
    #----------------------------------------------+
    @commands.cooldown(1, 120, commands.BucketType.member)
    @commands.has_permissions(administrator=True)
    @commands.command(
        aliases=["reaction-role", "rr", "reactionrole", "add-reaction-role"],
        help="создать роль за реакцию",
        description="добавляет роль за реакцию под сообщением.",
        usage="Роль",
        brief="Member" )
    async def reaction_role(self, ctx, *, role: discord.Role):
        if role.position >= ctx.author.top_role.position  and ctx.author.id != ctx.guild.owner_id:
            reply = discord.Embed(
                title="❌ Недостаточно прав",
                description=f"Указанная роль **<@&{role.id}>** выше Вашей, поэтому Вы не имеете права предоставлять её за нажатие на реакцию.",
                color=discord.Color.dark_red()
            )
            reply.set_footer(text=str(ctx.author), icon_url=str(ctx.author.avatar_url))
            await ctx.send(embed=reply)

        else:
            server_rr = ReactionRolesConfig(ctx.guild.id)

            reply = discord.Embed(
                title="🧸 | Роль за реакцию",
                description=(
                    f"Вы указали **<@&{role.id}>** в качестве роли за реакцию.\n"
                    "Теперь, пожалуйста, под нужным Вам сообщением добавьте реакцию, за которую будет даваться роль."
                ),
                color=role.color
            )
            reply.set_footer(text=str(ctx.author), icon_url=ctx.author.avatar_url)
            await ctx.send(embed=reply)

            # Waiting for moderator's reaction
            def check(payload):
                return payload.user_id == ctx.author.id and payload.guild_id == ctx.guild.id
            
            cycle = True
            _payload = None
            while cycle:
                try:
                    payload = await self.client.wait_for("raw_reaction_add", check=check, timeout=120)

                except asyncio.TimeoutError:
                    reply = discord.Embed(
                        title="🕑 | Превышено время ожидания",
                        description="Вы не ставили реакцию более 120 секунд",
                        color=discord.Color.blurple()
                    )
                    reply.set_footer(text=str(ctx.author), icon_url=ctx.author.avatar_url)
                    await ctx.send(ctx.author.mention, embed=reply)
                    cycle = False

                else:
                    if server_rr.get_role(payload.message_id, payload.emoji) is not None:
                        reply = discord.Embed(
                            title="⚠ Ошибка",
                            description="За эту реакцию уже даётся роль",
                            color=discord.Color.gold()
                        )
                        reply.set_footer(text=str(ctx.author), icon_url=str(ctx.author.avatar_url))
                        await ctx.send(ctx.author.mention, embed=reply)

                    else:
                        channel = ctx.guild.get_channel(payload.channel_id)
                        message = await channel.fetch_message(payload.message_id)
                        try:
                            await message.add_reaction(payload.emoji)
                            await message.remove_reaction(payload.emoji, ctx.author)
                        except Exception:
                            pass
                        else:
                            cycle = False
                            _payload = payload
            
            # Adding emoji-role pair to database
            if _payload is not None:
                server_rr.add_role(_payload.message_id, _payload.emoji, role.id)

                reply = discord.Embed(
                    title="🧸 | Роль за реакцию",
                    description=f"Теперь в канале <#{_payload.channel_id}> даётся роль **<@&{role.id}>** за реакцию [{_payload.emoji}] под нужным сообщением.",
                    color=role.color
                )
                reply.set_footer(text=str(ctx.author), icon_url=ctx.author.avatar_url)
                await ctx.send(embed=reply)
        
        # Resetting cooldownd
        raise CooldownResetSignal()


    @commands.cooldown(1, 120, commands.BucketType.member)
    @commands.has_permissions(administrator=True)
    @commands.command(
        aliases=["remove-reaction-role", "rrr", "removereactionrole", "reaction-role-remove"],
        help="удалить роль за реакцию",
        description="удаляет роль за реакцию под сообщением.",
        usage="",
        brief="" )
    async def remove_reaction_role(self, ctx):
        server_rr = ReactionRolesConfig(ctx.guild.id)

        reply = discord.Embed(
            title="↩ | Сброс роли за реакцию",
            description="Пожалуйста, под нужным Вам сообщением уберите (или поставьте и уберите) реакцию, за которую даётся роль.",
            color=discord.Color.magenta()
        )
        reply.set_footer(text=str(ctx.author), icon_url=ctx.author.avatar_url)
        await ctx.send(embed=reply)

        # Waiting for moderator's reaction
        def check(payload):
            return payload.user_id == ctx.author.id and payload.guild_id == ctx.guild.id
        
        cycle = True
        _payload = None
        role_id = None
        while cycle:
            try:
                payload = await self.client.wait_for("raw_reaction_remove", check=check, timeout=120)

            except asyncio.TimeoutError:
                reply = discord.Embed(
                    title="🕑 | Превышено время ожидания",
                    description="Вы не убирали реакции более 120 секунд",
                    color=discord.Color.blurple()
                )
                reply.set_footer(text=str(ctx.author), icon_url=ctx.author.avatar_url)
                await ctx.send(ctx.author.mention, embed=reply)
                cycle = False

            else:
                role_id = server_rr.get_role(payload.message_id, payload.emoji)
                if role_id is None:
                    reply = discord.Embed(
                        title="⚠ Ошибка",
                        description="За эту реакцию не даётся роль",
                        color=discord.Color.gold()
                    )
                    reply.set_footer(text=str(ctx.author), icon_url=str(ctx.author.avatar_url))
                    await ctx.send(ctx.author.mention, embed=reply)

                else:
                    channel = ctx.guild.get_channel(payload.channel_id)
                    message = await channel.fetch_message(payload.message_id)
                    try:
                        await message.clear_reaction(payload.emoji)
                    except Exception:
                        pass
                    else:
                        cycle = False
                        _payload = payload
        
        # Adding emoji-role pair to database
        if _payload is not None:
            server_rr.remove_reaction(_payload.message_id, _payload.emoji)

            reply = discord.Embed(
                title="🎀 | Сброс роли за реакцию",
                description=f"Теперь, под указанным сообщением, роль **<@&{role_id}>** больше не даётся за реакцию [{_payload.emoji}].",
                color=discord.Color.magenta()
            )
            reply.set_footer(text=str(ctx.author), icon_url=ctx.author.avatar_url)
            await ctx.send(embed=reply)
        
        # Resetting cooldownd
        raise CooldownResetSignal()

    #----------------------------------------------+
    #                   Errors                     |
    #----------------------------------------------+


def setup(client):
    client.add_cog(reaction_roles(client))