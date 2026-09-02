import os
import re
from datetime import datetime
import dateparser
import discord
import pytz

intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)

SLT_ZONE = pytz.timezone("America/Los_Angeles")

# Matches the full date + time phrase right before SLT
SLT_PATTERN = re.compile(
    r"\b((?:(?:on|at|this|next)\s+)?(?:(?:\d{1,2}(?:st|nd|rd|th)?\s+(?:of\s+)?(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)|(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\s+\d{1,2}(?:st|nd|rd|th)?|mon(?:day)?|tue(?:sday)?|wed(?:nesday)?|thu(?:rsday)?|fri(?:day)?|sat(?:urday)?|sun(?:day)?)\s*,?\s*)?(?:1[0-2]|0?[1-9])(?::[0-5][0-9])?\s*(?:am|pm)?|(?:[01]?[0-9]|2[0-3]):[0-5][0-9])\s*slt\b",
    re.IGNORECASE,
)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} - SLT Converter is active!")


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # finditer captures the entire matched string safely
    matches = [m.group(0) for m in SLT_PATTERN.finditer(message.content)]

    if matches:
        converted_times = []
        now_slt = datetime.now(SLT_ZONE)

        for match_str in matches:
            # Strip off trailing SLT / slt for parsing
            clean_time_str = re.sub(r"\s*slt\b", "", match_str, flags=re.IGNORECASE).strip()

            parsed_dt = dateparser.parse(
                clean_time_str,
                settings={
                    "RELATIVE_BASE": now_slt.replace(tzinfo=None),
                    "PREFER_DATES_FROM": "future",
                    "DATE_ORDER": "DMY",
                },
            )

            if parsed_dt:
                localized_slt = SLT_ZONE.localize(parsed_dt)
                unix_timestamp = int(localized_slt.timestamp())

                converted_times.append(
                    f"<t:{unix_timestamp}:F> (<t:{unix_timestamp}:R>)"
                )

        if converted_times:
            response = "**SLT Time Conversion:**\n" + "\n".join(converted_times)
            await message.reply(response, mention_author=False)


TOKEN = os.getenv("DISCORD_TOKEN")
if TOKEN:
    bot.run(TOKEN)
