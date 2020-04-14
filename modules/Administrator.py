import discord
from discord.ext import commands
import sqlite3
import asyncio
from lib import settings

owners = settings.Owners

class Administrator(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command(name="채널")
	async def channel_counter(self, ctx):
		conn = sqlite3.connect("lib/data.db")
		cur = conn.cursor()
		cur.execute("SELECT * FROM users WHERE user = {}".format(ctx.author.id))
		rows = cur.fetchall()
		if rows[0][1] == 'Administrator' or rows[0][1] == "Developer" or ctx.author.id in owners:
			async with ctx.channel.typing():
				all = 0
				cate = 0
				text = 0
				voice = 0
				for guild in self.bot.guilds:
					for channel in guild.channels:
						all += 1
					for category in guild.categories:
						cate += 1
					for text_channel in guild.text_channels:
						text += 1
					for voice_channel in guild.voice_channels:
						voice += 1
				await asyncio.sleep(3)
			await ctx.send("현재 채널 개수는 **{0}**개에요.\n카테고리 : `{1}`개\n채팅 채널 `{2}`개\n음성 채널 : `{3}`개".format(all, cate, text, voice))
		else:
			await ctx.send("<:cs_no:659355468816187405> {} - 권한이 없어요. 이 명령어를 사용하려면 `봇 관리자` 권한이 있어야 해요.".format(ctx.author.mention))


	@commands.command(name="블랙")
	async def blacklist(self, ctx, *args):
		conn = sqlite3.connect("lib/data.db")
		cur = conn.cursor()
		cur.execute("SELECT * FROM users WHERE user = {}".format(ctx.author.id))
		rows = cur.fetchall()
		if rows[0][1] == 'Administrator' or rows[0][1] == "Developer" or ctx.author.id in owners:
			if not args:
				await ctx.send("<:cs_no:659355468816187405> {} - 블랙리스트에 추가할 유저의 ID를 입력해주세요.".format(ctx.author.mention))
			else:
				if args[0].isdecimal() == True:
					u = self.bot.get_user(int(args[0]))
					if u is not None:
						cur.execute("SELECT * FROM users WHERE user = {}".format(int(args[0])))
						rows = cur.fetchall()
						if not rows:
							cur.execute("INSERT INTO users(user, perms) VALUES({}, 'Blacklisted')".format(args[0]))
							conn.commit()
							conn.close()
							await ctx.send("<:cs_yes:659355468715786262> {} - 해당 유저를 DB에 등록함과 동시에, 블랙리스트에 추가했어요!".format(ctx.author.mention))
						else:
							if rows[0][1] == 'Blacklisted' and rows[0][1] == 'Administrator' and rows[0][1] == 'Owner':
								await ctx.send("<:cs_no:659355468816187405> {} - 해당 유저는 블랙리스트에 추가할 수 없어요. 이미 블랙리스트에 있거나, 봇 관리자에요.".format(ctx.author.mention))
							else:
								cur.execute("UPDATE users SET perms = 'Blacklisted' WHERE user = {}".format(args[0]))
								conn.commit()
								conn.close()
								await ctx.send("<:cs_yes:659355468715786262> {} - 해당 유저를 블랙리스트에 추가했어요!".format(ctx.author.mention))
					else:
						await ctx.send("<:cs_no:659355468816187405> {} - 그런 유저가 Discord 상에 없어요.".format(ctx.author.mention))
				else:
					await ctx.send("<:cs_no:659355468816187405> {} - 문자열은 입력하실 수 없어요.".format(ctx.author.mention))
		else:
			await ctx.send("<:cs_no:659355468816187405> {} - 권한이 없어요. 이 명령어를 사용하려면 `봇 관리자` 권한이 있어야 해요.".format(ctx.author.mention))

	@commands.command(name="언블랙")
	async def unblack(self, ctx, *args):
		conn = sqlite3.connect("lib/data.db")
		cur = conn.cursor()
		cur.execute("SELECT * FROM users WHERE user = {}".format(ctx.author.id))
		rows = cur.fetchall()
		if rows[0][1] == 'Administrator' or rows[0][1] == "Developer" or ctx.author.id in owners:
			if not args:
				await ctx.send("<:cs_no:659355468816187405> {} - 블랙리스트에서 삭제할 유저의 ID를 입력해주세요.".format(ctx.author.mention))
			else:
				if args[0].isdecimal() == True:
					u = self.bot.get_user(int(args[0]))
					if u is not None:
						cur.execute("SELECT * FROM users WHERE user = {}".format(int(args[0])))
						rows = cur.fetchall()
						if rows[0][1] != 'Blacklisted':
							await ctx.send("<:cs_no:659355468816187405> {} - 그 유저는 블랙리스트에 없어요.".format(ctx.author.mention))
						else:
							cur.execute("UPDATE users SET perms = 'Authenticated' WHERE user = {}".format(args[0]))
							conn.commit()
							conn.close()
							await ctx.send("<:cs_yes:659355468715786262> {} - 해당 유저를 블랙리스트에서 삭제했어요!".format(ctx.author.mention))
					else:
						await ctx.send("<:cs_no:659355468816187405> {} - 그런 유저가 Discord 상에 없어요.".format(ctx.author.mention))
				else:
					await ctx.send("<:cs_no:659355468816187405> {} - 문자열은 입력하실 수 없어요.".format(ctx.author.mention))
		else:
			await ctx.send("<:cs_no:659355468816187405> {} - 권한이 없어요. 이 명령어를 사용하려면 `봇 관리자` 권한이 있어야 해요.".format(ctx.author.mention))
	
	@commands.command(name="유저")
	async def user_count(self, ctx):
		conn = sqlite3.connect("lib/data.db")
		cur = conn.cursor()
		cur.execute("SELECT * FROM users WHERE user = {}".format(ctx.author.id))
		rows = cur.fetchall()
		if rows[0][1] == 'Administrator' or rows[0][1] == "Developer" or ctx.author.id in owners:
			async with ctx.channel.typing():
				await asyncio.sleep(3)
				botc = 0
				human = 0
				for u in self.bot.users:
					if u.bot:
						botc += 1
					else:
						human += 1
				await ctx.send("현재 집계된 계정은 **{0}**개에요.\n봇 개수 : `{1}`개\n유저 명수 : `{2}`명".format(len(self.bot.users), botc, human))
		else:
			await ctx.send("<:cs_no:659355468816187405> {} - 권한이 없어요. 이 명령어를 사용하려면 `봇 관리자` 권한이 있어야 해요.".format(ctx.author.mention))

	@commands.command(name="서버")
	async def serverlist(self, ctx):
		conn = sqlite3.connect("lib/data.db")
		cur = conn.cursor()
		cur.execute("SELECT * FROM users WHERE user = {}".format(ctx.author.id))
		rows = cur.fetchall()
		if rows[0][1] == 'Administrator' or rows[0][1] == "Developer" or ctx.author.id in owners:
			em = discord.Embed(title="{} 디버깅".format(self.bot.user.name), description="현재 {0}가 접속된 서버 개수 : {1}개".format(self.bot.user.name, len(self.bot.guilds)), color=0xF4EB94)
			i = 1
			async with ctx.channel.typing():
				for guild in self.bot.guilds:
					try:
						ginvites = await guild.invites()
						if not ginvites:
							try:
								ginvite = await guild.text_channels[0].create_invite()
								em.add_field(name="#{}".format(i), value="**{1.name}** ({1.id}, `{1.member_count}`명) Invite :: {2}".format(i, guild, ginvite.url), inline=False)
							except:
								em.add_field(name="#{}".format(i), value="**{1.name}** ({1.id}, `{1.member_count}`명) Invite :: `초대 링크를 불러올 수 없었어요.`".format(i, guild), inline=False)
						else:
							em.add_field(name="#{}".format(i), value="**{1.name}** ({1.id}, `{1.member_count}`명) Invite :: {2}".format(i, guild, ginvites[0].url), inline=False)
					except:
						try:
							ginvite = await guild.text_channels[0].create_invite()
							em.add_field(name="#{}".format(i), value="**{1.name}** ({1.id}, `{1.member_count}`명) Invite :: {2}".format(i, guild, ginvite.url), inline=False)
						except:
							em.add_field(name="#{}".format(i), value="**{1.name}** ({1.id}, `{1.member_count}`명) Invite :: `초대 링크를 불러올 수 없었어요.`".format(i, guild), inline=False)
					i += 1
			try:
				await ctx.send(ctx.author.mention, embed=em)
			except:
				await ctx.send("<:cs_no:659355468816187405> {} - 2000자가 넘거나, 중도에 오류가 발생했어요.\n`.서버레거시` 명령어를 사용해보세요!".format(ctx.author.mention))
		else:
			await ctx.send("<:cs_no:659355468816187405> {} - 권한이 없어요. 이 명령어를 사용하려면 `봇 관리자` 권한이 있어야 해요.".format(ctx.author.mention))

	@commands.command(name="공지")
	async def adman(self, ctx, *args):
		embed = discord.Embed(title="일반 :: {}".format(ctx.message.content.split(";")[1]), description="{}\n \n**봇과 관련된 문의는 LLOOOOTT#2260 혹은 [이 서버](https://discord.gg/HrG4ntB)에서 해주세요!**".format(ctx.message.content.split(";")[2]), color=0xF4EB94)
		embed.set_author(name="알림", icon_url=self.bot.user.avatar_url)
		embed.set_thumbnail(url=self.bot.user.avatar_url)
		embed.set_footer(text="배포자 : {0.name}#{0.discriminator}".format(ctx.author))
		conn = sqlite3.connect("lib/data.db")
		cur = conn.cursor()
		cur.execute("SELECT * FROM users WHERE user = {}".format(ctx.author.id))
		rows = cur.fetchall()
		if rows[0][1] == 'Administrator' or rows[0][1] == "Developer" or ctx.author.id in owners:
			sex = await ctx.send("<:cs_console:659355468786958356> {} - 정말로 이렇게 전송하시겠어요?".format(ctx.author.mention), embed=embed)
			await sex.add_reaction("<:cs_yes:659355468715786262>")
			def check(reaction, user):
				return user == ctx.author and reaction.message.id == sex.id and str(reaction.emoji) == "<:cs_yes:659355468715786262>"
			
			try:
				reaction, user = await self.bot.wait_for('reaction_add', timeout=100, check=check)
			except asyncio.TimeoutError:
				await sex.delete()
			else:
				cur.execute("SELECT * FROM announce")
				rows = cur.fetchall()
				error = 0
				no = 0
				sent = 0
				no_perms = 0
				invalid_channel = 0
				for row in rows:
					if row[1] == 'true':
						channel = self.bot.get_channel(row[2])
						if channel is not None:
							try:
								await channel.send(embed=embed)
								sent += 1
								no += 1
							except discord.Forbidden:
								no_perms += 1
								no += 1
							except discord.HTTPException:
								error += 1
								no += 1
							except:
								error += 1
								no += 1
						else:
							cur.execute("UPDATE announce SET enabled = 'false' WHERE guild = {}".format(row[0]))
							conn.commit()
							invalid_channel += 1
				erem = discord.Embed(description="공지 전송 시도 : `{4}`회\n전송됨 : `{0}`개의 서버\n권한 없음 : `{1}`개의 서버\n잘못된 채널 : `{5}`개의 서버\n오류 발생 : `{2}`개의 서버\n전송되지 않은 서버 : `{3}`개의 서버".format(sent, no_perms, error, len(self.bot.guilds) - sent, no, invalid_channel), color=0xF4EB94)
				await ctx.send(ctx.author.mention, embed=erem)
		else:
			await ctx.send("<:cs_no:659355468816187405> {} - 권한이 없어요. 이 명령어를 사용하려면 `봇 관리자` 권한이 있어야 해요.".format(ctx.author.mention))


def setup(bot):
	bot.add_cog(Administrator(bot)) 