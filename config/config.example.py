import discord
from utils.functions.permissions import get_integer

bot_version = "0.0.1"

client_id = 11111111111111111111

support_invite = "https://discord.gg/2ZRKrzf"

intents = discord.Intents().all()

permissions = discord.Permissions(get_integer(
    [
        "CREATE_INSTANT_INVITE",
        "READ_MESSAGE_HISTORY",
        "USE_EXTERNAL_EMOJIS",
        "CHANGE_NICKNAME",
        "VIEW_AUDIT_LOG",
        "SEND_MESSAGES",
        "ATTACH_FILES",
        "EMBED_LINKS",
        "CONNECT",
        "SPEAK",
    ]
))

owners = [
    173237945149423619  # Kanin | Please keep my ID here
]

presences = [
    {
        "status": discord.Status.online,
        "activity": {
            "type": discord.Activity,
            "prefix": discord.ActivityType.playing,
            "text": "with Kanin"
        }
    }
]

colors = {
    "main": 0x06a2c9,
    "error": 0xe74c3c
}

prefixes = {
    "main": [
        "!"
    ],
    "debug": [
        "!!"
    ]
}

# https://strftime.org/
time_format = "%A, %B %d %Y @ %I:%M%p"
