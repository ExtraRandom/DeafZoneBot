from pymongo import MongoClient
import discord
import cogs.utils.IO as IO
from enum import Enum

url = IO.fetch_mongo_url_from_settings()
client = MongoClient(url)

db = client['main']

col_practice = db['practice']
col_channels = db['channels']

class CHANNELS(Enum):
    VC_UPDATES = "vc_updates_log"
    ACTION_REPORTS = "action_report_channel"



"""CHANNELS = {
    "vc_updates_log",
    "action_report_channel"
}"""


def check_for_existing_practice(user_id):
    practice = col_practice.find_one({'_id': str(user_id)})
    return practice

def get_server_channels(server_id):
    server_id = str(server_id)
    doc = col_channels.find_one({'_id': server_id})

    if doc is None:
        doc = {"_id": server_id}
        col_channels.insert_one(doc)

    missing = {
        channel.value: None
        for channel in CHANNELS
        if channel.value not in doc
    }

    if missing:
        col_channels.update_one(
            {"_id": server_id},
            {"$set": missing}
        )
        doc.update(missing)

    return doc

def get_channel(server_id, channel_type):
    if server_id is None:
        return None
    document = get_server_channels(server_id)
    return document.get(channel_type)

def set_channel(server_id, channel, channel_id):
    if channel not in CHANNELS:
        raise ValueError(f"Unknown channel type: {channel}")

    col_channels.update_one(
        {"_id": str(server_id)},
        {"$set": {channel: str(channel_id)}},
        upsert=True,
    )


class ChannelUpdateModal(discord.ui.DesignerModal):
    def __init__(self, server_id):
        super().__init__(title="test")

        data = get_server_channels(server_id)
        print(data)

        vc = data.get(CHANNELS.VC_UPDATES.value)
        vc_default = None
        if vc is not None:
            vc_default = discord.SelectDefaultValue(id=int(vc), type=discord.SelectDefaultValueType.channel)

        self.vc_log_channel = discord.ui.Label(
            "VC Log Channel",
            discord.ui.ChannelSelect(
                required=False, default_values=[vc_default] if vc_default else [],
            )
        )
        self.add_item(self.vc_log_channel)

        ar = data.get(CHANNELS.ACTION_REPORTS.value)
        ar_default = None
        if ar is not None:
            ar_default = discord.SelectDefaultValue(id=int(ar), type=discord.SelectDefaultValueType.channel)
        self.action_report_channel = discord.ui.Label(
            "Action Reports Channel",
            discord.ui.ChannelSelect(
                required=False, default_values=[ar_default] if ar_default else [],
            )
        )
        self.add_item(self.action_report_channel)

    async def callback(self, interaction: discord.Interaction):
        vc_log = self.vc_log_channel.item.values[0]
        action = self.action_report_channel.item.values[0]

        await interaction.response.send_message(f"vc log selected was {vc_log}, {vc_log.id}\n"
                                                f"action channel selected was {action}, {action.id}")