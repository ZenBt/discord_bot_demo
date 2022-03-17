import discord
from discord.ext import commands


class Jap(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(name='jap')
    async def japanizator(self, ctx):

        text = ctx.message.content.replace('+jap ', '').replace(' ', '    ')
        await ctx.send(stylish(text))

    @commands.command()
    async def get_id(self, ctx):
        await ctx.send(ctx.message.author.id)



def stylish(text):
    '''replace all letters with japanese'''
    text_new = ''
#   alph_old = 'abcdefghijklmnopqrstuvwxyzабвгдеёжзийклмнопрстуфхцчшщъыьэюя'
#   alph_new = '丹归仁力乞下厶廾工丁长乚从九口尸㔿尺丂丅凵リ山乂丫乙丹石归广亼乞庄水乡仈认长人从廾口刀尸仁丅丫中乂凵丩山山乙辷乙刁扣牙'
    text_to_jap = {'a': '丹', 'b': '归', 'c': '仁', 'd': '力', 'e': '乞', 'f': '下', 'g': '厶', 'h': '廾', 'i': '工', 'j': '丁', 'k': '长',
     'l': '乚', 'm': '从', 'n': '九', 'o': '口', 'p': '尸', 'q': '㔿', 'r': '尺', 's': '丂', 't': '丅', 'u': '凵', 'v': 'リ',
     'w': '山', 'x': '乂', 'y': '丫', 'z': '乙', 'а': '丹', 'б': '石', 'в': '归', 'г': '广', 'д': '亼', 'е': '乞', 'ё': '庄',
     'ж': '水', 'з': '乡', 'и': '仈', 'й': '认', 'к': '长', 'л': '人', 'м': '从', 'н': '廾', 'о': '口', 'п': '刀', 'р': '尸',
     'с': '仁', 'т': '丅', 'у': '丫', 'ф': '中', 'х': '乂', 'ц': '凵', 'ч': '丩', 'ш': '山', 'щ': '山', 'ъ': '乙', 'ы': '辷',
     'ь': '乙', 'э': '刁', 'ю': '扣', 'я': '牙'}
    
    for literal in text.lower():
        if literal.isalpha():
            text_new += text_to_jap[literal]
        else:
            text_new += literal
    return text_new



def setup(client):
    client.add_cog(Jap(client))
