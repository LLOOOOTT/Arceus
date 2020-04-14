import discord
from lib import settings
import sqlite3
import datetime
from discord.ext import commands

class General(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command(name="핑")
	async def ping(self, ctx):
		conn = sqlite3.connect("lib/data.db")
		cur = conn.cursor()
		cur.execute("SELECT * FROM bot")
		rows = cur.fetchall()
		t = rows[0][0]
		a = datetime.datetime.now() - datetime.datetime.strptime(t.split(".")[0], "%Y-%m-%d %H:%M:%S")
		b = datetime.datetime.strptime(str(a).split(".")[0], "%H:%M:%S")
		await ctx.send(":ping_pong: {0} - 루트! | API Latency : `{1}`ms | 작동 시간 ( 업타임 ) : {2}".format(ctx.author.mention, round(self.bot.latency * 1000), b.strftime("%H시간 %M분 %S초")))


	@commands.command(name="아바타")
	async def profilefinder(self, ctx, *args):
		if not args:
			em = discord.Embed(title="아바타 추적기", description="{0.name}#{0.discriminator}님의 아바타에요!".format(ctx.author), color=0xF4EB94)
			em.set_image(url=ctx.author.avatar_url_as(format="png", size=2048))
			await ctx.send(ctx.author.mention, embed=em)
		else:
			if not ctx.message.mentions:
				if args[0].isdecimal() == True:
					u = self.bot.get_user(int(args[0]))
					if u is not None:
						em = discord.Embed(title="아바타 추적기", description="{0.name}#{0.discriminator}님의 아바타에요!".format(u), color=0xF4EB94)
						em.set_image(url=u.avatar_url_as(format="png", size=2048))
						await ctx.send(ctx.author.mention, embed=em)
					else:
						await ctx.send("<:cs_no:659355468816187405> {} - 유저 ID의 값이 잘못되었거나, ID가 가리키는 값이 유저가 아니에요.".format(ctx.author.mention))
				else:
					await ctx.send("<:cs_no:659355468816187405> {} - 멘션이나 유저 ID가 식별되지 않았어요.".format(ctx.author.mention))
			else:
				em = discord.Embed(title="아바타 추적기", description="{0.name}#{0.discriminator}님의 아바타에요!".format(ctx.message.mentions[0]), color=0xF4EB94)
				em.set_image(url=ctx.message.mentions[0].avatar_url_as(format="png", size=2048))
				await ctx.send(ctx.author.mention, embed=em)


	@commands.command(name="초대")
	async def invite_link(self, ctx):
		await ctx.send("{0} - 여기 있어요!\nhttps://discordapp.com/oauth2/authorize?client_id={1}&permissions=842394975&scope=bot".format(ctx.author.mention, self.bot.user.id))

	@commands.command(name="유저정보")
	async def uinfo(self, ctx, *args):
		if not args:
			uemb = discord.Embed(title="{0.name}#{0.discriminator}님의 정보에요!".format(ctx.author), color=0xF4EB94)
			uemb.set_author(name="정보", icon_url=self.bot.user.avatar_url_as(format="png", size=2048))
			uemb.set_footer(text="아키우스 | {}".format(settings.Version))
			uemb.set_thumbnail(url=ctx.author.avatar_url_as(format="png", size=2048))
			uemb.add_field(name="이름", value=ctx.author.name)
			uemb.add_field(name="태그", value=ctx.author.discriminator)
			if ctx.author.status == discord.Status.online:
				uemb.add_field(name="현재 상태", value="온라인")
			if ctx.author.status == discord.Status.idle:
				uemb.add_field(name="현재 상태", value="자리 비움")
			if ctx.author.status == discord.Status.dnd:
				uemb.add_field(name="현재 상태", value="다른 용무 중")
			if ctx.author.status == discord.Status.offline:
				uemb.add_field(name="현재 상태", value="오프라인")
			uemb.add_field(name="역할", value=str(len(ctx.author.roles) - 1) + "개")
			uemb.add_field(name="유저 ID", value=ctx.author.id)
			uemb.add_field(name="디스코드 가입일", value=ctx.author.created_at.strftime('%Y년 %m월 %d일 %H:%M'), inline=False)
			uemb.add_field(name="{} 가입일".format(ctx.guild.name), value=ctx.author.joined_at.strftime('%Y년 %m월 %d일 %H:%M'), inline=False)
			await ctx.send(embed=uemb)

def setup(bot):
	bot.add_cog(General(bot)) 