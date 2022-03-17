import random
import discord
from discord.ext import commands


class Whois(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(name='Кто')
    async def who(self, ctx):
        players_mentioned = []
        msg = ctx.message.content.replace('+Кто','').replace('+who','')
        if ctx.message.mentions.__len__() > 0:
            for user in ctx.message.mentions:
                if user == self.client.user: #if bot is mentioned
                    await ctx.send('Конечно же, Lizardy няшка, но меня больше не отмечай')
                    return
                user_has_nick(user, players_mentioned)
                print(players_mentioned)
            msg = players_mentioned[random.randint(0, len(players_mentioned))] + msg[:msg.find('<')]

        else:
            for user in ctx.guild.members:
                if user == self.client.user:
                    continue
                user_has_nick(user, players_mentioned)
            msg = players_mentioned[random.randint(0, len(players_mentioned))] + msg


        await ctx.send(str(msg))


def user_has_nick(user,players_list):
    if user.nick is None:
        players_list.append(str(user))
    else:
        players_list.append(user.nick)


def setup(client):
    client.add_cog(Whois(client))