import discord
from discord.ext import commands
from lib import settings

owners = settings.Owners

class Test(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command(name="접속")
	async def comehere(self, ctx):
		if ctx.author.id in owners:
			await ctx.author.voice.channel.connect()
			await ctx.send("<:cs_yes:659355468715786262> {0.mention} - 당신이 있는 `{0.voice.channel.name}` 채널에 연결했어요!".format(ctx.author))
		else:
			await ctx.send("<:cs_no:659355468816187405> {} - 죄송해요. 이 명령어는 아직 사용하실 수 없어요.".format(ctx.author.mention))

	@commands.command(name="나가")
	async def ggeojyeo(self, ctx, *args):
		if ctx.author.id in owners:
			if not args:
				await self.bot.voice_clients[0].disconnect()
			else:
				t = args[0]
				await self.bot.voice_clients[t].disconnect()
		else:
			await ctx.send("<:cs_no:659355468816187405> {} - 죄송해요. 이 명령어는 아직 사용하실 수 없어요.".format(ctx.author.mention))

def setup(bot):
	bot.add_cog(Test(bot))