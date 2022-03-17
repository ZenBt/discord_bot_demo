import random
import discord
import requests
from discord.ext import commands
from bs4 import BeautifulSoup as bs


class Memes(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(aliases=['pic', 'пикча', 'пик'])
    async def get_pic(self, ctx):
        text = ctx.message.content
        try:
            vk_url, vk_id = get_name_id(text)
            meme = MemeParser(vk_url, vk_id)
            img_url = meme.get_url_of_picture()
            embd = discord.Embed(title=vk_url, color=discord.Colour.orange(), description=meme.get_post_comment())
            embd.set_image(url=img_url)
            await ctx.send(embed=embd)
        except TypeError:
            await ctx.send('Паблик не найден')


class MemeParser:

    def __init__(self, vk_url, vk_id):
        self.vk_url = vk_url
        self.vk_id = vk_id
        self.post_url = ''
        self.html = ''

    def get_last_post_id(self):
        soup = bs(requests.get(f'https://vk.com/{self.vk_url}').text, 'html.parser')
        last_post = soup.find_all('a', {'class': 'post__anchor anchor'})[1].get('name')
        last_post = last_post[last_post.find('_') + 1:]

        return int(last_post)

    def get_post_url(self):
        self.post_url = f'https://vk.com/wall-{self.vk_id}_{random.randint(0, self.get_last_post_id())}'

    def get_url_of_picture(self):
        while True:
            try:
                self.get_post_url()
                self.html = requests.get(self.post_url).text
                soup = bs(self.html, 'html.parser')
                div = soup.find('div', {'class': 'wi_body'}).find_all('div',
                                                                      {'class': 'thumb_map_img thumb_map_img_as_div'})
                if len(div) == 1:
                    break
            except AttributeError:
                continue
        temp = div[0].get("style")
        return temp[temp.find('(') + 1:-2]

    def get_post_comment(self):
        try:
            soup = bs(self.html, 'html.parser')
            post_comment = soup.find('div', {'class': 'pi_text'}).text

        except AttributeError:
            post_comment = ''
        return post_comment


def get_name_id(text):
    text = text.lower().replace('+пикча', '').replace('+pic', '').replace('+get_pic', '').replace('+пик', '').replace(' ','')
    meme_publics = {'eternal': ('eternalclassic', '129440544'),
                    '9gag': ('ru9gag', '32041317'),
                    'баян': ('public205691465', '205691465'),
                    'tyan': ('2d_despair', '110788487'),
                    'sci': ('sciencemem', '159146575'),
                    'японика': ('japonika18','157094959'),
                    '2dch': ('2d_ch','100892059'),
                    'leekch': ('leekchan','118140055'),
                    'anichan': ('2dmemeschan','150014441'),
                    'kaiko': ('kaikoclub','191475924'),
                    'кыр': ('a_hahahah','174862538'),
                    'станция': ('pic_station','122162987')
                    }
    if len(text) == 0:
        return random.choice(list(meme_publics.values()))
    return meme_publics.get(text)


def setup(client):
    client.add_cog(Memes(client))
