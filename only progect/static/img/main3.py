import discord
from discord.ext import commands
TOKEN = ''


config = {
    'token': 'your-token',
    'prefix': 'prefix',
}
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix=config['prefix'], intents=intents)

@bot.event
async def on_message(ctx):
    if ctx.author != bot.user:
        await ctx.reply(ctx.content)

bot.run(TOKEN)
