# coding = utf8
import discord
from discord.ext import commands
from discord import Webhook, AsyncWebhookAdapter
import asyncio
import aiohttp
import random
import itertools
import re
import datetime
import youtube_dl
from Arceus_Core import Configuration




#Settings
Token = Configuration.ArceusLoginToken
prefix = "$"
arceus = commands.Bot(command_prefix=commands.when_mentioned_or(prefix), description="""Creator of Pokèmon""")




@arceus.event
async def on_ready():
    await arceus.change_presence(status=discord.Status.dnd, activity=discord.Game("with world"))
    print("Arceus is now working. Latency : {}ms".format(round(client.latency * 1000)))

class Arceus:
    def _init_(self, bot):
        self.bot = bot
    
    @commands.command
    async def kick(ctx, *args):
        if not args:
            await ctx.send("{} 잘못된 명령어 문법이다.".format(ctx.author.mention))
        else:
            if not ctx.message.mentions:
                await ctx.send("{} 잘못된 명령어 문법이다.".format(ctx.author.mention))
            else:
                try:
                    user = ctx.message.mentions[0]
                    await ctx.guild.kick(user)
                    accepting = await ctx.send("{1} {0.name} ( {0.id} )를 서버에서 추방하였다.\n이것이 정확하게 처리된 것인가?".format(user, ctx.author.mention))
                    #await accepting.add_reaction("")
                    #await accepting.add_reaction("")
                except:
                    await ctx.send("{}, 명령어 실행 중 오류가 발생했다. 관리자에게 문의하도록.".format(ctx.author.mention))
