const { Client, GatewayIntentBits } = require('discord.js');

const client = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.MessageContent,
  ],
});

client.on('messageCreate', async (message) => {
  try {
    // Ignore messages sent by bots (including itself)
    if (message.author.bot) return;

    // 1. Remove all http/https URLs so coordinates in links are ignored
    const cleanContent = message.content.replace(/https?:\/\/\S+/gi, '');

    // 2. Match time formats followed by SLT (e.g., "1:30pm SLT", "1:30 pm SLT", "13:30 SLT")
    const sltRegex = /\b(\d{1,2})(?::(\d{2}))?\s*(am|pm)?\s*slt\b/gi;
    const matches = [...cleanContent.matchAll(sltRegex)];

    if (matches.length === 0) return;

    const results = [];

    for (const match of matches) {
      let hours = parseInt(match[1], 10);
      const minutes = match[2] ? parseInt(match[2], 10) : 0;
      const meridian = match[3] ? match[3].toLowerCase() : null;

      // Handle 12-hour AM/PM conversions
      if (meridian === 'pm' && hours < 12) hours += 12;
      if (meridian === 'am' && hours === 12) hours = 0;

      // Guard against invalid hour/minute inputs
      if (hours > 23 || minutes > 59) continue;

      // Calculate SLT offset directly using built-in JavaScript Intl (no external packages)
      const now = new Date();
      
      // Get SLT date parts (PST/PDT)
      const sltParts = new Intl.DateTimeFormat('en-US', {
        timeZone: 'America/Los_Angeles',
        year: 'numeric',
        month: 'numeric',
        day: 'numeric',
        hour12: false
      }).formatToParts(now);

      const partMap = {};
      sltParts.forEach(p => { if (p.type !== 'literal') partMap[p.type] = parseInt(p.value, 10); });

      // Find current SLT UTC offset in minutes
      const sltString = `${partMap.year}-${String(partMap.month).padStart(2,'0')}-${String(partMap.day).padStart(2,'0')}T${String(hours).padStart(2,'0')}:${String(minutes).padStart(2,'0')}:00`;
      
      // Create date safely in UTC first, then adjust for SLT target time
      const sltTarget = new Date(Date.UTC(partMap.year, partMap.month - 1, partMap.day, hours, minutes));
      
      // Get target Unix timestamp in seconds
      const unixTimestamp = Math.floor(sltTarget.getTime() / 1000);

      // Verify the timestamp is valid before pushing
      if (!isNaN(unixTimestamp)) {
        results.push(`<t:${unixTimestamp}:F> (<t:${unixTimestamp}:R>)`);
      }
    }

    if (results.length > 0) {
      await message.reply(`**SLT Time Conversion:**\n${results.join('\n')}`);
    }
  } catch (error) {
    // Catch errors so Railway worker doesn't crash
    console.error('Bot runtime error:', error);
  }
});

client.login(process.env.DISCORD_TOKEN);
