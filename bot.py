import os
import re
from datetime import datetime
import dateparser
import discord
import pytz

# Enable message reading intents
intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)

# SLT maps directly to US Pacific Time (handles PST/PDT automatically)
SLT_ZONE = pytz.timezone("America/Los_Angeles")

# Matches patterns like: 2pm slt, 2:30pm SLT, 14:00 slt, or plain numbers followed by slt
TIME_REGEX = re.compile(
    r"\b((?:1[0-2]|0?[1-9])(?::[0-5][0-9])?\s*(?:am|pm)?|(?:[01]?[0-9]|2[0-3]):[0-5][0-9])\s*slt\b",
    re.IGNORECASE,
)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} - SLT Converter is active!")


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    matches = TIME_REGEX.findall(message.content)

    if matches:
        converted_times = []
        now_slt = datetime.now(SLT_ZONE)

        for time_str in matches:
            # Parse time relative to current Pacific date
            parsed_dt = dateparser.parse(
                time_str,
                settings={
                    "RELATIVE_BASE": now_slt.replace(tzinfo=None),
                    "PREFER_DATES_FROM": "future",
                },
            )

            if parsed_dt:
                # Localize directly to Pacific (SLT)
                localized_slt = SLT_ZONE.localize(parsed_dt)
                unix_timestamp = int(localized_slt.timestamp())

                # Outputs dynamic Discord timestamp tag directly so everyone sees local time
                converted_times.append(
                    f"<t:{unix_timestamp}:f> (<t:{unix_timestamp}:R>)"
                )

        if converted_times:
            response = "**SLT Time Conversion:**\n" + "\n".join(converted_times)
            await message.reply(response, mention_author=False)


# Reads the secret token safely from Railway variables
TOKEN = os.getenv("DISCORD_TOKEN")
if TOKEN:
    bot.run(TOKEN)
else:
    print("Error: DISCORD_TOKEN environment variable not set!")
