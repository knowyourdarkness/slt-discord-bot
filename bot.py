import os
import re
from datetime import datetime
from dateparser.search import search_dates
import discord
import pytz

intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)

SLT_ZONE = pytz.timezone("America/Los_Angeles")


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} - SLT Converter is active!")


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # Check if the message contains SLT (case-insensitive)
    if "slt" not in message.content.lower():
        return

    now_slt = datetime.now(SLT_ZONE)

    # Clean the message text for better parsing
    cleaned_text = message.content

    # Normalize day abbreviations like 'Weds' or 'Wed'
    cleaned_text = re.sub(r"\bweds?\b", "Wednesday", cleaned_text, flags=re.IGNORECASE)

    # Remove 'slt' so dateparser doesn't get confused by the timezone label
    cleaned_text = re.sub(r"\bslt\b", "", cleaned_text, flags=re.IGNORECASE)

    # Search the entire message string for any date/time pattern in any format
    results = search_dates(
        cleaned_text,
        settings={
            "RELATIVE_BASE": now_slt.replace(tzinfo=None),
            "PREFER_DATES_FROM": "future",
            "DATE_ORDER": "DMY",  # Ensures 5/09/2026 reads as 5th Sept, not May 9th
        },
    )

    if results:
        converted_times = []
        for text_match, parsed_dt in results:
            # Avoid matching standalone single digits or non-time noise
            if len(text_match.strip()) < 2 or text_match.strip().isdigit():
                continue

            localized_slt = SLT_ZONE.localize(parsed_dt)
            unix_timestamp = int(localized_slt.timestamp())

            converted_times.append(
                f"<t:{unix_timestamp}:F> (<t:{unix_timestamp}:R>)"
            )

        if converted_times:
            # Remove duplicates if any overlap
            unique_times = list(dict.fromkeys(converted_times))
            response = "**SLT Time Conversion:**\n" + "\n".join(unique_times)
            await message.reply(response, mention_author=False)


TOKEN = os.getenv("DISCORD_TOKEN")
if TOKEN:
    bot.run(TOKEN)
