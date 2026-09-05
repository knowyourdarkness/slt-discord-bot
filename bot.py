const { Client, GatewayIntentBits } = require('discord.js');

const client = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.MessageContent,
  ],
});

// Helper function to safely parse SLT time into a Unix timestamp
function parseSLTToUnix(targetHours, targetMinutes) {
  const now = new Date();
  
  // Format current date in America/Los_Angeles timezone
  const formatter = new Intl.DateTimeFormat('en-US', {
    timeZone: 'America/Los_Angeles',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
  });

  const parts = Object.fromEntries(
    formatter.formatToParts(now).map((p) => [p.type, p.value])
  );

  const year = parseInt(parts.year, 10);
  const month = parseInt(parts.month, 10) - 1;
  const day = parseInt(parts.day, 10);

  // Approximate UTC date matching the SLT components
  const utcGuess = Date.UTC(year, month, day, targetHours, targetMinutes, 0);

  // Calculate actual current PST/PDT offset in milliseconds
  const laString = now.toLocaleString('en-US', { timeZone: 'America/Los_Angeles' });
  const utcString = now.toLocaleString('en-US', { timeZone: 'UTC' });
  const offsetMs = new Date(laString).getTime() - new Date(utcString).getTime();

  // Subtract offset to get exact UTC time for the SLT target
  const finalTimestampMs = utcGuess - offsetMs;
  return Math.floor(finalTimestampMs / 1000);
}

client.on('messageCreate', async (message) => {
  try {
    // Ignore messages sent by bots
    if (message.author.bot) return;

    // 1. Remove all URLs so coordinates (e.g. /1803) in links are completely ignored
    const cleanContent = message.content.replace(/https?:\/\/\S+/gi, '');

    // 2. Search for time expressions ending in SLT
    const sltRegex = /\b(\d{1,2})(?::(\d{2}))?\s*(am|pm)?\s*slt\b/gi;
    const matches = [...cleanContent.matchAll(sltRegex)];

    if (matches.length === 0) return;

    const results = [];

    for (const match of matches) {
      let hours = parseInt(match[1], 10);
      const minutes = match[2] ? parseInt(match[2], 10) : 0;
      const meridian = match[3] ? match[3].toLowerCase() : null;

      // Convert 12-hour AM/PM to 24-hour format
      if (meridian === 'pm' && hours < 12) hours += 12;
      if (meridian === 'am' && hours === 12) hours = 0;

      // Skip invalid hour/minute inputs
      if (hours > 23 || minutes > 59) continue;

      const unixTimestamp = parseSLTToUnix(hours, minutes);

      if (!isNaN(unixTimestamp)) {
        results.push(`<t:${unixTimestamp}:F> (<t:${unixTimestamp}:R>)`);
      }
    }

    if (results.length > 0) {
      await message.reply(`**SLT Time Conversion:**\n${results.join('\n')}`);
    }
  } catch (error) {
    // Log error to Railway console without stopping the bot process
    console.error('Error processing SLT message:', error);
  }
});

client.login(process.env.DISCORD_TOKEN);
