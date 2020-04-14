import discord
import sqlite3
import asyncio
from discord.ext import commands
from discord.ext.commands import has_permissions, CheckFailure
import typing

class Moderation(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command(name="삭제")
	@has_permissions(manage_messages=True)
	async def bulkDelete(self, ctx, *args):
		if not args:
			await ctx.send("<:cs_no:659355468816187405> {} - 메시지를 몇 개 삭제할 건지 적어주세요!".format(ctx.author.mention))
		else:
			if args[0].isdecimal() == True:
				if int(args[0]) > 100 or int(args[0]) <= 0:
					await ctx.send("<:cs_no:659355468816187405> {} - 숫자가 100을 넘거나, 음수 혹은 0일 수 없어요!".format(ctx.author.mention))
				else:
					await ctx.message.delete()
					await ctx.channel.purge(limit=int(args[0]))
					await ctx.send("<:cs_yes:659355468715786262> {0} - 총 **{1}**개의 메시지를 삭제했어요!".format(ctx.author.mention, args[0]), delete_after=5)
			else:
				await ctx.send("<:cs_no:659355468816187405> {} - 문자열은 적으실 수 없어요!".format(ctx.author.mention))


	@commands.command(name="추방")
	@has_permissions(kick_members=True)
	async def kick(self, ctx, members: commands.Greedy[discord.Member], *,
					reason: str):

		if not members:
			await ctx.send("<:cs_console:659355468786958356> {0} - 정확한 명령어 : `.추방 < @유저1 @유저2... > [ 사유 ]`".format(ctx.author.mention))
		else:
			for member in members:
				try:
					await member.kick(reason=reason)
					await ctx.send("<:cs_yes:659355468715786262> {0.mention} - {1.name}#{1.discriminator}님을 서버에서 추방했어요!\n사유 : {2}".format(ctx.author, member, reason))
				except:
					await ctx.send("<:cs_yes:659355468715786262> {0.mention} - {1.name}#{1.discriminator}님을 추방할 수 없었어요. 권한이 없거나, 그 유저가 아키우스보다 높아요.".format(ctx.author, member, reason))


	@commands.command(name="차단")
	@has_permissions(ban_members=True)
	async def ban(self, ctx, members: commands.Greedy[discord.Member],
					delete: typing.Optional[int] = 0, *,
					reason: str):

		if not members:
			await ctx.send("<:cs_console:659355468786958356> {0} - 정확한 명령어 : `.차단 < @유저1 @유저2... > [ 메시지 삭제 기간 ~30일까지 ] [ 사유 ]`".format(ctx.author.mention))
		else:
			for member in members:
				try:
					await ctx.guild.ban(member, delete_message_days=delete, reason=reason)
					await ctx.send("<:cs_yes:659355468715786262> {0.mention} - {1.name}#{1.discriminator}님을 서버에서 차단했어요!\n사유 : {2}\n메시지 지우기 : `{3}일 간의 메시지 삭제`".format(ctx.author, member, reason, delete))
				except:
					await ctx.send("<:cs_yes:659355468715786262> {0.mention} - {1.name}#{1.discriminator}님을 차단할 수 없었어요. 권한이 없거나, 그 유저가 아키우스보다 높아요.".format(ctx.author, member, reason, delete))

	@ban.error
	async def banerr(self, ctx, error):
		if isinstance(error, CheckFailure):
			await ctx.send("<:cs_no:659355468816187405> {} - 권한이 없어요. 이 명령어를 사용하려면 `멤버 차단` 권한이 있어야 해요.".format(ctx.author.mention))

	@kick.error
	async def kickerr(self, ctx, error):
		if isinstance(error, CheckFailure):
			await ctx.send("<:cs_no:659355468816187405> {} - 권한이 없어요. 이 명령어를 사용하려면 `멤버 추방` 권한이 있어야 해요.".format(ctx.author.mention))

	@bulkDelete.error
	async def deleteerror(self, ctx, error):
		if isinstance(error, CheckFailure):
			await ctx.send("<:cs_no:659355468816187405> {} - 권한이 없어요. 이 명령어를 사용하려면 `메시지 관리` 권한이 있어야 해요.".format(ctx.author.mention))

def setup(bot):
	bot.add_cog(Moderation(bot))