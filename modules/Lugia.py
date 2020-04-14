import discord
from discord.ext import commands

class Lugia(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command(name="루기아")
	async def auth(self, ctx, *args):
		if ctx.guild.id == 675931753780609033:
			Confirmed = discord.utils.get(ctx.guild.roles, id=693002727453884426)
			if Confirmed in ctx.author.roles:
				await ctx.send("<:cs_no:659355468816187405> {} - 이미 접근이 승인되셨어요.".format(ctx.author.mention))
			else:
				if not args:
					await ctx.send("<:cs_no:659355468816187405> {} - 자신의 DiscordTag#0000 을 입력해주세요!".format(ctx.author.mention))
				else:
					if args[0] == "{0.name}#{0.discriminator}".format(ctx.author):
						await ctx.author.add_roles(Confirmed)
						await ctx.author.send("<:cs_yes:659355468715786262> {} - 인증되셨어요! 이제 서포트 채널의 모든 채널에 접근하실 수 있어요.".format(ctx.author.mention))
					else:
						await ctx.send("<:cs_no:659355468816187405> {} - DiscordTag#0000이 잘못 입력되었어요. 자신의 태그를 입력해주세요!".format(ctx.author.mention))
		else:
			await ctx.send("<:cs_no:659355468816187405> {} - 이 명령어는 아키우스 서포트 채널에서만 사용하실 수 있어요.".format(ctx.author.mention))

def setup(bot):
	bot.add_cog(Lugia(bot)) 