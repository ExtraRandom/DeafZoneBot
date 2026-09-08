from pymongo import MongoClient
import discord
import cogs.utils.IO as IO
from enum import Enum

from functools import wraps
from pymongo.errors import PyMongoError, ServerSelectionTimeoutError

url = IO.fetch_mongo_url_from_settings()
client = MongoClient(url, timeoutMS=2000)

db = client['main']

col_practice = db['practice']
col_config = db['config']

# CURRENTLY:
# role pings (game role id's only) and verification channel and roles id's are hardcoded
# moderation and monitoring channels id's are in database, can be changed easily

class CONFIG(Enum):
    CHANNEL_VC_UPDATES = ("CHANNEL_vc_updates_log", "VC Log Channel", discord.ui.ChannelSelect)
    CHANNEL_ACTION_REPORTS = ("CHANNEL_action_report", "Action Reports Channel", discord.ui.ChannelSelect)
    CHANNEL_PRACTISE_PING = ("CHANNEL_practise_ping", "Practise Ping Channel", discord.ui.ChannelSelect)

    ROLE_PRACTISE_PING = ("ROLE_practise_ping", "Practise Role (to ping)", discord.ui.RoleSelect)

    def __init__(self, key, label, select_type):
        self.key = key
        self.label = label
        self.select_type = select_type

class ERRORS(Enum):
    NO_CONNECTION = 1

def mongo_error_handler(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ServerSelectionTimeoutError:
            print("MongoDB connection timed out")
            return ERRORS.NO_CONNECTION
        except PyMongoError as e:
            print(f"MongoDB error: {e}")
            return ERRORS.NO_CONNECTION

    return wrapper

@mongo_error_handler
def check_for_existing_practice(user_id):
    practice = col_practice.find_one({'_id': str(user_id)})
    return practice

@mongo_error_handler
def get_server_config(server_id):
    server_id = str(server_id)
    doc = col_config.find_one({'_id': server_id})

    if doc is None:
        doc = {"_id": server_id}
        col_config.insert_one(doc)

    missing = {
        channel.key: None
        for channel in CONFIG
        if channel.key not in doc
    }

    if missing:
        col_config.update_one(
            {"_id": server_id},
            {"$set": missing}
        )
        doc.update(missing)

    return doc

def get_setting(server_id, setting):
    if server_id is None:
        return None
    document = get_server_config(server_id)
    return document.get(setting)

def set_setting(server_id, setting, new_setting_value):
    if setting not in CONFIG:
        raise ValueError(f"Unknown channel type: {setting}")

    col_config.update_one(
        {"_id": str(server_id)},
        {"$set": {setting: str(new_setting_value)}},
        upsert=True,
    )

def ensure_guild_config(guild_id):
    guild_id = str(guild_id)

    data = col_config.find_one({"_id": guild_id})

    if data is None:
        data = {"_id": guild_id}

    missing = {
        setting.key: None
        for setting in CONFIG
        if setting.key not in data
    }

    if missing:
        col_config.update_one(
            {"_id": guild_id},
            {"$set": missing},
            upsert=True
        )



class ConfigUpdateModal(discord.ui.DesignerModal):
    def __init__(self, server_id):
        super().__init__(title="Config Setup")

        self.inputs = {}
        self.server_id = server_id

        data = get_server_config(server_id)
        print(data)

        for setting in CONFIG:
            value = data.get(setting.key)

            default = [
                discord.SelectDefaultValue(
                    id=int(value),
                    type=(
                        discord.SelectDefaultValueType.channel
                        if setting.select_type is discord.ui.ChannelSelect
                        else discord.SelectDefaultValueType.role
                    )
                )
            ] if value else []

            select = setting.select_type(
                required=False,
                default_values=default
            )

            label = discord.ui.Label(setting.label, select)

            self.add_item(label)
            self.inputs[setting] = label



    async def callback(self, interaction: discord.Interaction):
        update = {}

        for config, label in self.inputs.items():
            values = label.item.values

            update[config.key] = (
                str(values[0].id)
                if values
                else None
            )

        col_config.update_one(
            {"_id": str(self.server_id)},
            {"$set": update},
            upsert=True
        )

        await interaction.response.send_message(update)