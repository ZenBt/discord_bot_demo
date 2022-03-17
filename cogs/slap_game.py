import random
import os
import pymongo
import discord
from discord.ext import commands
from decouple import config

MONGO = config('MONGO')

clientDB = pymongo.MongoClient(MONGO)
db = clientDB["slapgame"]
col = db.server


def slap_db_update(server, p1, p2, score1, score2):
    """Updates scores of players 1 and 2 on mongoDB server"""
    col.update_many({'server_id': server}, {'$inc': {str(p1): score1, str(p2): score2}}, upsert=True)


class Slap(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(name='slap')
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def slap_game(self, ctx):
        """frontend side of the slap game"""
        server_id = ctx.message.guild.id
        player_one_id = ctx.message.author.id

        # check if there are any mentions and saves the first in player_two_id
        if ctx.message.mentions.__len__() > 0:

            for user in ctx.message.mentions:
                player_two_id = user.id
                break
            # p1 and p2 are nicknames of players
            p1 = str(await discord.Guild.fetch_member(ctx.message.guild, player_one_id))
            p2 = str(await discord.Guild.fetch_member(ctx.message.guild, player_two_id))

            # check if you do not mention yourself or the bot
            if player_one_id != player_two_id and player_two_id != self.client.user.id:
                marker = slap_smb(server_id, player_one_id, player_two_id)

                if marker == 1:
                    await ctx.send(
                        f"{p1[:p1.find('#')]} показал свою мужественность и уничтожил {p2[:p2.find('#')]}, +2 победителю")
                elif marker == -1:
                    await ctx.send(f" {p1[:p1.find('#')]} оступился и попал по себе -1.")
                elif marker == 0:
                    await ctx.send(
                        f"Дурачки {p1[:p1.find('#')]} и {p2[:p2.find('#')]} вырубили друг друга и получили по -1")

            # if you mention bot
            elif player_two_id == self.client.user.id:
                liza_revenge(ctx.message.guild.id, player_one_id)
                await ctx.send(f'Я очень разочарована в тебе, {p1}, теперь у тебя -500 очков')
            # if you mention yourself
            else:

                await ctx.send('Не бей себя')
                ctx.command.reset_cooldown(ctx)

        else:
            await ctx.send('Отметь кого нибудь')
            ctx.command.reset_cooldown(ctx)

    @commands.command(aliases=['лидеры', 'Лидеры'])
    async def leaders(self, ctx):
        lead = leader_board(ctx.guild.id)
        leaders_str = discord.Embed(title='Список лидеров', color=discord.Colour.orange())
        if lead is not None:
            for id, score in lead.items():
                user = str(ctx.guild.get_member(id))
                if user == 'None':
                    user = 'Покинувший нас'
                leaders_str.add_field(name=user, value=f'Очки: {score}', inline=False)
            await ctx.send(embed=leaders_str)
        else:
            await ctx.send('Список лидеров пуст')

    @commands.command()
    async def atone(self, ctx):
        liza_forgive(ctx.guild.id, ctx.author.id)
        await ctx.send(f'Я прощаю тебя, {ctx.author.name}')


def slap_smb(server, p1, p2):
    """backend side of slap game"""
    chance = random.randint(0, 100)
    if chance > 45:
        slap_db_update(server, p1, p2, 2, -1)
        return 1

    elif chance < 35:
        slap_db_update(server, p1, p2, -1, 2)
        return -1

    else:
        slap_db_update(server, p1, p2, -1, -1)
        return 0


def liza_revenge(server, p1):
    """invoked when bot is mentioned in slap game"""
    col.update_one({'server_id': server}, {'$inc': {str(p1): -500}}, upsert=True)


def leader_board(server):
    """returns dict with ids and scores of the server from mongoDB"""
    slap_leaders = col.find_one({'server_id': server})
    del slap_leaders['server_id']
    del slap_leaders['_id']
    if slap_leaders is not None:
        return {int(k): v for k, v in sorted(slap_leaders.items(), key=lambda item: item[1], reverse=True)}
    else:
        return False


def liza_forgive(server, p1):
    """set player score on the server at 0 points"""
    col.update_one({'server_id': server}, {'$set': {str(p1): 0}}, upsert=True)


def setup(client):
    client.add_cog(Slap(client))
