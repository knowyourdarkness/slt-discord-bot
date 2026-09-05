const { Client, GatewayIntentBits } = require('discord.js');

const client = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.MessageContent,
  ],
});

client.on('messageCreate', async (message) => {
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

    // Build the target time in Pacific Time (SLT)
    // Note: SLT follows America/Los_Angeles (PST/PDT)
    const now = new Date();
    const sltDateString = new Date().toLocaleDateString('en-US', { timeZone: 'America/Los_Angeles' });
    const sltDateTime = new Date(`${sltDateString} ${hours}:${minutes}:00`);

    // Convert to Unix timestamp in seconds for Discord's native relative timestamp tag
    const unixTimestamp = Math.floor(sltDateTime.getTime() / 1000);

    // Format as Discord dynamic timestamps (<t:UNIX:F> for full date, <t:UNIX:R> for relative)
    results.push(`<t:${unixTimestamp}:F> (<t:${unixTimestamp}:R>)`);
  }

  if (results.length > 0) {
    await message.reply(`**SLT Time Conversion:**\n${results.join('\n')}`);
  }
});

client.login('YOUR_DISCORD_BOT_TOKEN');
