import discord
from discord.ext import commands
import sqlite3
from lib import settings
import asyncio
import ast

owners = settings.Owners
version = settings.Version

class Owner(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command(name="답장")
	async def reply(self, ctx, *args):
		conn = sqlite3.connect("lib/data.db")
		cur = conn.cursor()
		cur.execute("SELECT * FROM users WHERE user = {}".format(ctx.author.id))
		rows = cur.fetchall()
		if ctx.author.id in owners:
			replyer = self.bot.get_user(int(args[0]))
			reply_content = discord.Embed(title="{0.name}#{0.discriminator}님의 피드백에 대해 답장이 도착했어요!".format(replyer), description=ctx.message.content[22:], color=0xF4EB94)
			reply_content.set_author(name="지원 / 관리", icon_url=self.bot.user.avatar_url_as(format="png", size=2048))
			reply_content.set_thumbnail(url=ctx.author.avatar_url_as(format="png", size=2048))
			reply_content.set_footer(text="아키우스 | {}".format(version))
			try:
				await replyer.send(replyer.mention, embed=reply_content)
				await ctx.send("<:cs_yes:659355468715786262> {0} - {1.name}#{1.discriminator} 님에게 답장을 전송했어요!".format(ctx.author.mention, replyer))
			except discord.Forbidden:
				await ctx.send("<:cs_no:659355468816187405> {} - 해당 유저가 DM을 막아놓은 것 같아요! 전송에 실패했어요.".format(ctx.author.mention))
		else:
			await ctx.send("<:cs_no:659355468816187405> {} - 권한이 없어요. 이 명령어를 사용하려면 `봇 관리자` 권한이 있어야 해요.".format(ctx.author.mention))
	
	@commands.command(name="종료")
	async def turnoff(self, ctx):
		conn = sqlite3.connect("lib/data.db")
		cur = conn.cursor()
		cur.execute("SELECT * FROM users WHERE user = {}".format(ctx.author.id))
		rows = cur.fetchall()
		if ctx.author.id in owners:
			tom = await ctx.send("<:cs_stop:665173353874587678> {} - 정말로 봇을 종료하시겠어요? 종료하시려면 <:cs_yes:659355468715786262> 반응을 추가해주세요!\n*이 요청은 30초 후 만료될 거에요.*".format(ctx.author.mention))
			await tom.add_reaction("<:cs_yes:659355468715786262>")
			def check(reaction, user):
				return user == ctx.author and reaction.message.channel == ctx.channel and str(reaction.emoji) == '<:cs_yes:659355468715786262>'

			try:
				reaction, user = await self.bot.wait_for('reaction_add', timeout=10, check=check)
			except asyncio.TimeoutError:
				await tom.edit(content='<:cs_no:659355468816187405> {} - 아무런 반응이 없어 봇 종료를 취소했어요.'.format(ctx.author.mention), delete_after=5)
			else:
				await tom.edit(content="<:cs_stop:665173353874587678> {} - 5초 후 봇이 종료될 거에요.".format(ctx.author.mention))
				await asyncio.sleep(2)
				await tom.edit(content="<:cs_stop:665173353874587678> {} - 3초 후 봇이 종료될 거에요.".format(ctx.author.mention))
				await asyncio.sleep(1)
				await tom.edit(content="<:cs_stop:665173353874587678> {} - 2초 후 봇이 종료될 거에요.".format(ctx.author.mention))
				await asyncio.sleep(1)
				await tom.edit(content="<:cs_stop:665173353874587678> {} - 1초 후 봇이 종료될 거에요.".format(ctx.author.mention))
				await asyncio.sleep(1)
				await tom.edit(content="<:cs_stop:665173353874587678> {} - 봇이 종료되고 있어요....".format(ctx.author.mention))
				await self.bot.close()
		else:
			await ctx.send("<:cs_no:659355468816187405> {} - 권한이 없어요. 이 명령어를 사용하려면 `봇 소유자` 권한이 있어야 해요.".format(ctx.author.mention))

def setup(bot):
	bot.add_cog(Owner(bot)) 