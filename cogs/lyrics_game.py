import random
import re
import requests
import discord
from bs4 import BeautifulSoup as bs
from discord.ext import commands


class Lyrics(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    @commands.command(aliases=['текст'])
    async def lyr(self, ctx):
        artist_group = ctx.message.content.replace('+lyr ','').replace('+текст ','').lower()
        if ArtistParser.existing_artists_group(artist_group) is None and artist_group != 'дальше':
            await ctx.send('Не правильная группа исполнителей')
        else:
            server_id = ctx.message.guild.id
            player_id = ctx.message.author.id
            try:
                LyricsGameBackend.current_games[server_id][player_id]['attemps']
            except:
                await ctx.send('Подбираю песню')
            verse = LyricsGameBackend.game_handler(server_id, player_id, artist_group)
            if verse is not None:
                left = 3 - LyricsGameBackend.current_games[server_id][player_id]['attemps']
                embed=discord.Embed(title=str(ctx.guild.get_member(player_id)), description=f"Оставшихся подсказок {left}", color=0x00fffb)
                embed.add_field(name=verse[0], value=verse[1], inline=False)
                embed.add_field(name=verse[2], value=verse[3], inline=False)
                await ctx.send(embed=embed)
            else:
                # if player runs out of attemps
                await ctx.send(f'Количество посказок закончилось. Дальше сам')
                
    
    @commands.command(aliases=['ответ'])
    async def answer(self, ctx):
        answr = ctx.message.content.replace('+answer ','').replace('+ответ ','').lower().strip()
        server_id = ctx.message.guild.id
        player_id = ctx.message.author.id
        try:
            if LyricsGameBackend.is_correct_answer(server_id, player_id, answr):
                await ctx.send(random.choice(['Ты чертовски прав', 'Именно так', 'Gracios', 'Ты действовал наверняка', 'Ладно, это было легко']))
                LyricsGameBackend.delete_game(server_id, player_id)
            else:
                await ctx.send(random.choice(['Nope, не в этот раз','Ты еще никогда так не ошибался...', 'Когда нибудь повезет...', 'Может лучше сдаться?']))
        except:
            await ctx.send('Начни игру, написав +lyr <тег>')

            
            
    @commands.command(aliases=['сдаться', 'сдаюсь'])
    async def surrender(self, ctx):
        server_id = ctx.message.guild.id
        player_id = ctx.message.author.id
        try:
            await ctx.send(f'Правильный ответ - {LyricsGameBackend.current_games[server_id][player_id]["full_name"]}')
            await ctx.send('В следующи раз обязательно повезет')
            LyricsGameBackend.delete_game(server_id, player_id)
        except:
            await ctx.send('Начни игру, написав +lyr <тег>')
        
class LyricsGameBackend:
    current_games = {}
    # TEMPLATE OF current_gamws dictionary
    # {
    #     12312313: {
    #         1234:
    #             {
    #                 'attemps': 0,
    #                 'song': 'Kosandra',
    #                 'lyrics': list of lyrics
    #             },
    #         4321:
    #             {
    #                 'attemps': 3,
    #                 'song': 'Rap God',
    #                 'lyrics': list of lyrics 2
    #                 'previous': 2
    #             }
    #     },
    #     100000001: {}
    # }

    @classmethod
    def game_handler(cls, server_id, player_id, key):
        """verify the ability to continue the game """
        try:
            if cls.has_enough_attemps(server_id, player_id):
                return cls.get_current_verse(server_id, player_id, key)
            else:
                return None
        except KeyError:
            return cls.get_current_verse(server_id, player_id, key) #if no more lines left return the whole song
    
    @classmethod
    def server_has_games(cls, server_id):
        return True if cls.current_games.get(server_id) is not None else False

    @classmethod
    def is_currently_on_game(cls, server_id, player_id):
        if cls.server_has_games(server_id):
            return bool(cls.current_games[server_id].get(player_id))
        cls.current_games[server_id] = {}
        return False
    
    @classmethod
    def has_enough_attemps(cls, server_id, player_id):
        return cls.current_games[server_id][player_id]['attemps'] < 3 
    
    @classmethod
    def is_correct_answer(cls, server_id, player_id, answer):
        return cls.current_games[server_id][player_id]['song'].strip().lower() == answer
    
    @classmethod
    def initialize_game(cls, server_id, player_id, title, lyrics, name, previous):
        cls.current_games[server_id][player_id] = {
            'attemps': 0,
            'song': title,
            'lyrics': lyrics,
            'previous': previous,
            'full_name': name
        }
    
    @classmethod
    def delete_game(cls, server_id, player_id):
        del cls.current_games[server_id][player_id]
    
    @classmethod
    def get_current_verse(cls, server_id, player_id, key):
        LINES_FOR_ONE_TRY = 4
        if cls.is_currently_on_game(server_id, player_id):
            lyrics = cls.current_games[server_id][player_id]['lyrics']
            previous = cls.current_games[server_id][player_id]['previous']
            cls.current_games[server_id][player_id]['previous'] += LINES_FOR_ONE_TRY
            cls.current_games[server_id][player_id]['attemps'] += 1
            try:
                return [lyrics[i] for i in range(previous, previous + LINES_FOR_ONE_TRY + 1)]
            except IndexError:
                return lyrics
        lyr_obj = LyricsParser(ArtistParser.get_song_data(ArtistParser.get_popular_songs(key)))
        lyrics = lyr_obj.refine_lyrics(lyr_obj.get_lyrics())
        title = lyr_obj.title
        name = lyr_obj.name + '-' + title
        cls.initialize_game(server_id, player_id, title, lyrics, name, previous=LINES_FOR_ONE_TRY)
        return [lyrics[i] for i in range(LINES_FOR_ONE_TRY)]
    
class ArtistParser:
    artist_pool = { 
        'ru': ('70468', '1050560', '1451552', '2945418'), #IDs of artists at genius.com
        'en': ('506', '45', '12493', '1112784', '182'),
        'miyagi': ('70468', '2945418'),
        'gachi': ('2491803', '2491803'),
        'em': ('45', '45'),
        'ру': ('70468', '1050560', '1451552', '2945418')
        
    }

    @classmethod
    def choose_artist(cls, key):
        return random.choice(cls.artist_pool[key])
    
    @classmethod
    def existing_artists_group(cls, key):
        return cls.artist_pool.get(key)
    
    @classmethod
    def get_popular_songs(cls, key):
        while True:
            r = requests.get('https://genius.com/api/artists/{}/songs?page={}&sort=popularity'.\
                format(cls.choose_artist(key), random.randint(1, 5))).json()
            songs = r['response']['songs']
            if songs:
                return songs
    
    @staticmethod
    def get_song_data(songs_list):
        song = random.choice(songs_list)
        index = song['title'].find(' (')
        if index != -1:
            title = song['title'][:index].lower() # title: 'Speedom (Worldwide Choppers 2)' -> 'speedom'
        else:
            title = song['title']
            print(title)
        url = song['url']
        name = song['artist_names']
        return (title, url, name)
    
class LyricsParser:
    
    def __init__(self, song_data):
        self._title = song_data[0]
        self._url = song_data[1]
        self._name = song_data[2]
    
    @property
    def title(self):
        return self._title
    
    @property
    def name(self):
        return self._name
    
    def get_lyrics(self):
        r = requests.get(self._url).text
        soup = bs(r, 'html.parser')
        return soup.find_all('div', {'data-lyrics-container':'true'})  
    
    @staticmethod
    def refine_lyrics(lyrics_list):
        refined_lyr = []
        for i in range(len(lyrics_list)):
            q = lyrics_list[i].text
            counter = 0
            for i in range(len(q)-1):
                if (q[i] not in ' ["«(' and q[i+1].isupper()\
                    and ((q[i].isalpha() and q[i].islower()) \
                        or q[i].isdigit() or q[i] in "'?\"")) or \
                    (q[i] != ' ' and q[i+1] in'[(') \
                    or (q[i] in '])»' and q[i+1] != ']'): # it somehow works, you'd better not touch it
                        refined_lyr.append(q[counter:i+1])
                        counter = i + 1
        return LyricsParser.remove_brackets(refined_lyr)
    
    @staticmethod
    def remove_brackets(refined_lyr):
        return [line for line in refined_lyr if re.match(r'.*(\[|\]).*', line) is None]
    
    
def setup(client):
    client.add_cog(Lyrics(client))
