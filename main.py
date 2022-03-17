import os
import discord
from discord.ext import commands
from decouple import config

TOKEN = config('TOKEN')
ADMIN_ID1 = config('ADMIN_ID1')
ADMIN_ID2 = config('ADMIN_ID2')

intents = discord.Intents.all()
client = commands.Bot(command_prefix='+', intents=intents)

@client.command()
async def load(ctx, extension):
    '''load specific cog(extension)'''
    if ctx.message.author.id == int(ADMIN_ID1) or int(ADMIN_ID2):
        client.load_extension(f'cogs.{extension}')


@client.command()
async def unload(ctx, extension):
    '''unload specific cog(extension)'''
    if ctx.message.author.id == int(ADMIN_ID1) or int(ADMIN_ID2):
        client.unload_extension(f'cogs.{extension}')
    else:
        await ctx.send('Недостаточно прав')

# load all exising cogs
for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')



client.run(TOKEN)
