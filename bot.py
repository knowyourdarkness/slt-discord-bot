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

# Expanded pattern to match dates, weekdays, or month names before the time
# Matches: "9th September 2pm slt", "Sept 9 14:00 SLT", "Friday 8pm slt", or "2pm slt"
TIME_REGEX = re.compile(
    r"\b((?:(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\s+\d{1,2}(?:st|nd|rd|th)?|\d{1,2}(?:st|nd|rd|th)?\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*|mon|tue|wed|thu|fri|sat|sun|monday|tuesday|wednesday|thursday|friday|saturday|sunday)?\s*(?:1[0-2]|0?[1-9])(?::[0-5][0-9])?\s*(?:am|pm)?|(?:[01]?[0-9]|2[0-3]):[0-5][0-9])\s*slt\b",
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
            cleaned_str = time_str.strip()
            if not cleaned_str:
                continue

            parsed_dt = dateparser.parse(
                cleaned_str,
                settings={
                    "RELATIVE_BASE": now_slt.replace(tzinfo=None),
                    "PREFER_DATES_FROM": "future",
                    "DATE_ORDER": "DMY",
                },
            )

            if parsed_dt:
                localized_slt = SLT_ZONE.localize(parsed_dt)
                unix_timestamp = int(localized_slt.timestamp())

                # Uses full date format tag <t:TIMESTAMP:F> so date changes are clear
                converted_times.append(
                    f"<t:{unix_timestamp}:F> (<t:{unix_timestamp}:R>)"
                )

        if converted_times:
            response = "**SLT Time Conversion:**\n" + "\n".join(converted_times)
            await message.reply(response, mention_author=False)


TOKEN = os.getenv("DISCORD_TOKEN")
if TOKEN:
    bot.run(TOKEN)
