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

# Finds anything up to 50 characters long that ends with "SLT"
SLT_CHUNK_PATTERN = re.compile(
    r"(?:(?:\b[\w\s,.:/'-]{1,50}\b)?\b(?:1[0-2]|0?[1-9])(?::[0-5][0-9])?\s*(?:am|pm)?|(?:[01]?[0-9]|2[0-3]):[0-5][0-9])\s*slt\b",
    re.IGNORECASE,
)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} - SLT Converter is active!")


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # Find potential time phrases ending in SLT
    matches = SLT_CHUNK_PATTERN.findall(message.content)

    if matches:
        converted_times = []
        now_slt = datetime.now(SLT_ZONE)

        for match_str in matches:
            # Clean off the "slt" label at the end
            clean_str = re.sub(r"\s*slt\b", "", match_str, flags=re.IGNORECASE).strip()

            # Clean out common prepositions at the start of matches if present
            clean_str = re.sub(
                r"^(?:will be|on|at|is|for|party|event)\s+",
                "",
                clean_str,
                flags=re.IGNORECASE,
            ).strip()

            parsed_dt = dateparser.parse(
                clean_str,
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
            # Remove duplicate timestamp outputs if any overlap
            unique_times = list(dict.fromkeys(converted_times))
            response = "**SLT Time Conversion:**\n" + "\n".join(unique_times)
            await message.reply(response, mention_author=False)


TOKEN = os.getenv("DISCORD_TOKEN")
if TOKEN:
    bot.run(TOKEN)
