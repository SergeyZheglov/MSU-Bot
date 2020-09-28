from discord.ext import commands
from pymongo import MongoClient
import os


app_string = str(os.environ.get('db_token'))
cluster = MongoClient(app_string)
db = cluster["guilds"]


perms_tr = {
    "create_instant_invite": "Создавать приглашения",
    "kick_members": "Кикать участников",
    "ban_members": "Банить участников",
    "administrator": "Администратор",
    "manage_channels": "Управлять каналами",
    "manage_guild": "Управлять сервером",
    "add_reactions": "Добавлять реакции",
    "view_audit_log": "Просматривать журнал аудита",
    "priority_speaker": "Приоритетный режим",
    "stream": "Видео",
    "read_messages": "Читать сообщения",
    "view_channel": "Видеть канал",
    "send_messages": "Отправлять сообщения",
    "send_tts_messages": "Отправлять TTS сообщения",
    "manage_messages": "Управлять сообщениями",
    "embed_links": "Встраивать ссылки",
    "attach_files": "Прикреплять файлы",
    "read_message_history": "Просматривать историю сообщений",
    "mention_everyone": "Упоминать everyone / here",
    "external_emojis": "Использовать внешние эмодзи",
    "view_guild_insights": "View server insights",
    "connect": "Подключаться",
    "speak": "Говорить",
    "mute_members": "Выключать микрофон у участников",
    "deafen_members": "Заглушать участников",
    "move_members": "Перемещать участников",
    "use_voice_activation": "Использовать режим рации",
    "change_nickname": "Изменять никнейм",
    "manage_nicknames": "Управлять никнеймами",
    "manage_roles": "Управлять ролями",
    "manage_permissions": "Управлять правами",
    "manage_webhooks": "Управлять вебхуками",
    "manage_emojis": "Управлять эмодзи"
}
def display_perms(missing_perms):
    out = ""
    for perm in missing_perms:
        out += f"> {perms_tr[perm]}\n"
    return out


def visual_delta(td):
    delta = [
        ("дн", td.days),
        ("ч", td.seconds // 3600),
        ("мин", td.seconds % 3600 // 60),
        ("сек", td.seconds % 60)
    ]
    out = ""
    for kw, v in delta:
        if v != 0:
            out += f"{v} {kw} "
    return "0 сек" if out == "" else out.strip()


def has_instance(_list: list, _class):
    has = False
    for elem in _list:
        if isinstance(elem, _class):
            has = True
            break
    return has


class CooldownResetSignal(commands.CommandError):
    pass


class ReactionRolesConfig:
    def __init__(self, server_id: int):
        self.id = server_id
    
    def get_role(self, message_id: int, emoji: str):
        collection = db["reaction_roles"]
        result = collection.find_one(
            {"_id": self.id, f"{message_id}.{emoji}": {"$exists": True}},
            projection={str(message_id): True}
        )
        return None if result is None else result.get(f"{message_id}", {}).get(f"{emoji}")
    
    def add_role(self, message_id: int, emoji: str, role_id: int):
        collection = db["reaction_roles"]
        collection.update_one(
            {"_id": self.id, f"{message_id}.{emoji}": {"$exists": False}},
            {"$set": {f"{message_id}.{emoji}": role_id}},
            upsert=True
        )
    
    def remove_reaction(self, message_id: int, emoji: str):
        collection = db["reaction_roles"]
        collection.update_one(
            {"_id": self.id, f"{message_id}.{emoji}": {"$exists": True}},
            {"$unset": {f"{message_id}.{emoji}": ""}}
        )

    def get_roles(self, message_id: int):
        collection = db["reaction_roles"]
        result = collection.find_one(
            {"_id": self.id, f"{message_id}": {"$exists": True}},
            projection={str(message_id): True}
        )
        return {} if result is None else result.get(str(message_id), {})

    def delete_branch(self, message_id: int):
        collection = db["reaction_roles"]
        collection.update_one(
            {"_id": self.id, f"{message_id}": {"$exists": True}},
            {"$unset": {f"{message_id}": ""}}
        )


# Ha ha lol