import discord
import sqlite3
import asyncio
from discord.ext import commands
from discord.ext.commands import has_permissions, CheckFailure
from lib import settings

owners = settings.Owners
version = settings.Version

class Default(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command(name="활성화")
	async def activate(self, ctx):
		conn = sqlite3.connect("lib/data.db")
		cur = conn.cursor()
		cur.execute("SELECT * FROM users WHERE user = {}".format(ctx.author.id))
		rows = cur.fetchall()
		if not rows:
			cur.execute("INSERT INTO users(user, perms) VALUES({}, 'Authenticated')".format(ctx.author.id))
			conn.commit()
			conn.close()
			await ctx.send("<:cs_yes:659355468715786262> {} - 당신의 계정을 활성화했어요! 이제 모든 명령어를 이용하실 수 있어요!".format(ctx.author.mention))
		else:
			if rows[0][1] == "Not Authenticated":
					cur.execute("UPDATE users SET perms = 'Authenticated' WHERE user = {}".format(ctx.author.id))
					conn.commit()
					conn.close()
					await ctx.send("<:cs_yes:659355468715786262> {} - 당신의 계정을 활성화했어요! 이제 모든 명령어를 이용하실 수 있어요!".format(ctx.author.mention))
			else:
					await ctx.send("<:cs_no:659355468816187405> {} - 이미 활성화된 계정이에요.".format(ctx.author.mention))

	@commands.command(name="아키셋")
	@has_permissions(manage_guild=True)
	async def arcet(self, ctx, *args):
		await ctx.message.delete()
		if not args:
			await ctx.send("<:cs_console:659355468786958356> {} - 설정할 값을 지정해야 해요. 설정값은 `,아키셋 설정값` 명령어로 확인하실 수 있어요.".format(ctx.author.mention), delete_after=5)
		else:
			conn = sqlite3.connect("lib/data.db")
			cur = conn.cursor()
			cur.execute("SELECT * FROM servers WHERE guild = {}".format(ctx.guild.id))
			rows = cur.fetchall()
			if not rows:
				if args[0] == "초기":
					setup = await ctx.send("<:cs_settings:659355468992610304> {} - 아키우스 초기 설정을 하고 있어요... 잠시만 기다려주세요...".format(ctx.author.mention))
					async with ctx.typing():
						conn = sqlite3.connect("lib/data.db")
						cur = conn.cursor()
						cur.execute("INSERT INTO announce(guild, enabled, channel) VALUES({0.id}, 'false', {1.id})".format(ctx.guild, ctx.channel))
						cur.execute("INSERT INTO log(guild, enabled, channel) VALUES({}, 'false', 1234)".format(ctx.guild.id))
						cur.execute("INSERT INTO servers(guild, perms, verified, invitefilter) VALUES({}, 'Authenticated', 'false', 'false')".format(ctx.guild.id))
						cur.execute("INSERT INTO customWelcome(guild, enabled, message, channel) VALUES({}, 'false', 'None', 1234)".format(ctx.guild.id))
						cur.execute("INSERT INTO customBye(guild, enabled, message, channel) VALUES({}, 'false', 'None', 1234)".format(ctx.guild.id))
						conn.commit()
						conn.close()
						await asyncio.sleep(3)
					await setup.edit(content="<:cs_yes:659355468715786262> {} - 서버 기본값이 적용 완료되었어요. 이제 아키우스의 모든 기능을 이용하실 수 있어요.".format(ctx.author.mention), delete_after=10)
				else:
					await ctx.send("<:cs_settings:659355468992610304> {} - 이 서버는 초기 설정이 완료되지 않았어요. `,아키셋 초기`를 사용해 초기 설정을 완료해주세요!".format(ctx.author.mention))
			else:
				if args[0] == "초기":
					await ctx.send("<:cs_settings:659355468992610304> {} - 이미 초기 설정이 완료된 서버에요. 삭제는 관리자에게 문의해주세요.".format(ctx.author.mention))

				elif args[0] == "로그":
					yee = await ctx.send("<:cs_settings:659355468992610304> {} - 서버 이벤트 로그를 켜시겠어요?\n<:cs_yes:659355468715786262> - 예\n<:cs_no:659355468816187405> - 아니오".format(ctx.author.mention))
					await yee.add_reaction("<:cs_yes:659355468715786262>")
					await yee.add_reaction("<:cs_no:659355468816187405>")
					def check(reaction, user):
						return user == ctx.author and reaction.message.channel == ctx.channel

					try:
						reaction, user = await self.bot.wait_for('reaction_add', timeout=30, check=check)
					except asyncio.TimeoutError:
						await yee.edit(content="<:cs_no:659355468816187405> {} - 아무런 반응이 없으셨어요. 아키셋을 취소할게요.".format(ctx.author.mention), suppress=False, delete_after=5)
					else:
						if str(reaction.emoji) == "<:cs_yes:659355468715786262>":
							conn = sqlite3.connect("lib/data.db")
							cur = conn.cursor()
							cur.execute("UPDATE log SET enabled = 'true' WHERE guild = {}".format(ctx.guild.id))
							conn.commit()
							conn.close()
							await yee.clear_reactions()
							await yee.add_reaction("<:cs_settings:659355468992610304>")
							await yee.edit(content="<:cs_yes:659355468715786262> {} - 로그 기능을 활성화했어요. 채널을 설정하려면 아래 <:cs_settings:659355468992610304> 반응을 눌러주세요.".format(ctx.author.mention), suppress=False)
							def check(reaction, user):
								return user == ctx.author and reaction.message.channel == ctx.channel and str(reaction.emoji) == "<:cs_settings:659355468992610304>"

							try:
								reaction, user = await self.bot.wait_for('reaction_add', timeout=10, check=check)
							except asyncio.TimeoutError:
								await yee.clear_reactions()
								conn = sqlite3.connect("lib/data.db")
								cur = conn.cursor()
								cur.execute("SELECT * FROM log WHERE guild = {}".format(ctx.guild.id))
								rows = cur.fetchall()
								if not rows:
									await yee.edit(content="<:cs_yes:659355468715786262> {0} - 로그 채널을 변경하지 않으시는 걸로 알아둘게요! 현재 로그 채널은 지정되지 않았어요.".format(ctx.author.mention), suppress=False, delete_after=10)
								else:
									channel = ctx.guild.get_channel(rows[0][1])
									if channel is None:
										await yee.edit(content="<:cs_yes:659355468715786262> {0} - 로그 채널을 변경하지 않으시는 걸로 알아둘게요! 현재 로그 채널은 삭제되었거나, 잘못된 채널이에요.".format(ctx.author.mention), suppress=False, delete_after=10)
									else:
										await yee.edit(content="<:cs_yes:659355468715786262> {0} - 로그 채널을 변경하지 않으시는 걸로 알아둘게요! 현재 로그 채널은 <#{1}> 채널이에요.".format(ctx.author.mention, rows[0][1]), suppress=False, delete_after=10)
							else:
								await yee.clear_reactions()
								await yee.edit(content="<:cs_settings:659355468992610304> {} - 이벤트 로그를 전송할 채널을 멘션해주세요.".format(ctx.author.mention), suppress=False)
								def check(msg):
									return msg.author == ctx.author and msg.channel == ctx.channel

								try:
									msg = await self.bot.wait_for('message', timeout=30, check=check)
								except asyncio.TimeoutError:
									await yee.edit(content="<:cs_no:659355468816187405> {} - 아무런 반응이 없으셨어요. 채널 설정을 취소할게요.".format(ctx.author.mention), suppress=False, delete_after=5)
								else:
									if not msg.channel_mentions:
										await yee.edit(content="<:cs_no:659355468816187405> {} - 잘못된 값을 입력하셨어요. 채널 설정을 취소할게요.".format(ctx.author.mention), suppress=False, delete_after=5)
									else:
										channel = ctx.guild.get_channel(msg.channel_mentions[0].id)
										if channel is None:
											await yee.edit(content="<:cs_no:659355468816187405> {} - 잘못된 값을 입력하셨어요. 채널 설정을 취소할게요.".format(ctx.author.mention), suppress=False, delete_after=5)
										else:
											conn = sqlite3.connect("lib/data.db")
											cur = conn.cursor()
											cur.execute("UPDATE log SET channel = {0} WHERE guild = {0}".format(msg.channel_mentions[0].id, ctx.guild.id))
											conn.commit()
											conn.close()
											await yee.edit(content="<:cs_yes:659355468715786262> {0} - 로그 채널 변경을 완료했어요! 현재 로그 채널은 <#{1}> 채널이에요.".format(ctx.author.mention, msg.channel_mentions[0].id), suppress=False, delete_after=10)

						if str(reaction.emoji) == "<:cs_no:659355468816187405>":
							conn = sqlite3.connect("lib/data.db")
							cur = conn.cursor()
							cur.execute("UPDATE log SET enabled = 'false' WHERE guild = {}".format(ctx.guild.id))
							conn.commit()
							conn.close()
							await yee.clear_reactions()
							await yee.edit(content="<:cs_yes:659355468715786262> {} - 로그 기능을 비활성화했어요. 더 이상 이벤트를 로깅하지 않아요.".format(ctx.author.mention), suppress=False)

				elif args[0] == "입장":
					ws = await ctx.send("<:cs_settings:659355468992610304> {} - 유저 환영 기능을 켜시겠어요?\n<:cs_yes:659355468715786262> - 예\n<:cs_no:659355468816187405> - 아니오".format(ctx.author.mention))
					await ws.add_reaction("<:cs_yes:659355468715786262>")
					await ws.add_reaction("<:cs_no:659355468816187405>")
					def check(reaction, user):
						return user == ctx.author and reaction.message.channel == ctx.channel

					try:
						reaction, user = await self.bot.wait_for('reaction_add', timeout=30, check=check)
					except asyncio.TimeoutError:
						await ws.edit(content="<:cs_no:659355468816187405> {} - 아무런 반응이 없으셨어요. 아키셋을 취소할게요.".format(ctx.author.mention), suppress=False, delete_after=5)
					else:
						if str(reaction.emoji) == "<:cs_yes:659355468715786262>":
							conn = sqlite3.connect("lib/data.db")
							cur = conn.cursor()
							cur.execute("UPDATE customWelcome SET enabled = 'true' WHERE guild = {}".format(ctx.guild.id))
							conn.commit()
							conn.close()
							await ws.edit(content="<:cs_yes:659355468715786262> {} - 유저 환영 기능을 활성화했어요.\n메시지와 채널을 변경하시려면 아래 <:cs_settings:659355468992610304> 반응을 눌러주세요!".format(ctx.author.mention), suppress=False)
							await ws.clear_reactions()
							await ws.add_reaction("<:cs_settings:659355468992610304>")
							def check(reaction, user):
								return user == ctx.author and reaction.message.channel == ctx.channel and str(reaction.emoji) == "<:cs_settings:659355468992610304>"

							try:
								reaction, user = await self.bot.wait_for('reaction_add', timeout=30, check=check)
							except asyncio.TimeoutError:
								conn = sqlite3.connect("lib/data.db")
								cur = conn.cursor()
								cur.execute("SELECT * FROM customWelcome WHERE guild = {}".format(ctx.guild.id))
								rows = cur.fetchall()
								channel = ctx.guild.get_channel(rows[0][3])
								welcomemsg = rows[0][2]
								if channel is None and welcomemsg == 'None':
									await ws.edit(content="<:cs_no:659355468816187405> {} - 유저 환영 메시지와 채널을 설정하지 않으시는 걸로 알아둘게요!\n현재 채널이 설정되어 있지 않아요. | 현재 출력되는 메시지가 등록되지 않았어요.".format(ctx.author.mention), suppress=False, delete_after=5)

								if channel is None and welcomemsg != 'None':
									latest = welcomemsg.replace("{0.mention}", str(ctx.author.mention))
									latest2 = latest.replace("{1.name}", str(ctx.guild.name))
									latest3 = latest2.replace("{1.member_count}", str(ctx.guild.member_count))
									await ws.edit(content="<:cs_no:659355468816187405> {0.mention} - 유저 환영 메시지와 채널을 설정하지 않으시는 걸로 알아둘게요!\n현재 채널이 설정되어 있지 않아요. | 현재 출력되는 메시지는 {1}(이)에요.".format(ctx.author.mention, latest3), suppress=False, delete_after=5)

								if channel is not None and welcomemsg == 'None':
									await ws.edit(content="<:cs_no:659355468816187405> {0.mention} - 유저 환영 메시지와 채널을 설정하지 않으시는 걸로 알아둘게요!\n현재 채널은 <#{2}> 채널이에요. | 현재 출력되는 메시지가 등록되지 않았어요.".format(ctx.author, channel.id), suppress=False, delete_after=5)

								if channel is not None and welcomemsg != 'None':
									latest = welcomemsg.replace("{0.mention}", str(ctx.author.mention))
									latest2 = latest.replace("{1.name}", str(ctx.guild.name))
									latest3 = latest2.replace("{1.member_count}", str(ctx.guild.member_count))
									await ws.edit(content="<:cs_no:659355468816187405> {0.mention} - 유저 환영 메시지와 채널을 설정하지 않으시는 걸로 알아둘게요!\n현재 채널은 <#{1}> 채널이에요. | 현재 출력되는 메시지는 {2}(이)에요.".format(ctx.author.mention, channel.id, latest3), suppress=False, delete_after=5)
							else:
								await ws.edit(content="<:cs_settings:659355468992610304> {} - 설정할 메시지를 입력해주세요. 아래는 메시지에 쓸 수 있는 함수에요.\n[멘션] - 들어온 유저를 멘션합니다.\n[서버] - 서버 이름을 출력합니다.\n[유저수] - 서버의 유저 명수를 출력합니다.".format(ctx.author.mention))
								await ws.clear_reactions()
								def check(msg):
									return msg.author == ctx.author and msg.channel == ctx.channel

								try:
									msg = await self.bot.wait_for('message', timeout=100, check=check)
								except asyncio.TimeoutError:
									await ws.edit(content='<:cs_no:659355468816187405> {} - 아무런 반응이 없으셨어요. 아키셋을 취소할게요.'.format(ctx.author.mention), suppress=False, delete_after=5)
								else:
									conn = sqlite3.connect("lib/data.db")
									cur = conn.cursor()
									a = msg.content.replace("[멘션]", "{0.mention}")
									b = a.replace("[서버]", "{1.name}")
									last = b.replace("[유저수]", "{1.member_count}")
									cur.execute("UPDATE customWelcome SET message = '{1}' WHERE guild = {0}".format(ctx.guild.id, last))
									conn.commit()
									conn.close()
									await msg.delete()
									await ws.clear_reactions()
									await ws.edit(content="<:cs_settings:659355468992610304> {} - 메시지를 전송할 채널을 멘션해주세요.".format(ctx.author.mention), suppress=False)
									def check(cmsg):
										return cmsg.author == ctx.author and cmsg.channel == ctx.channel

									try:
										cmsg = await self.bot.wait_for('message', timeout=30, check=check)
									except asyncio.TimeoutError:
										await ws.edit(content='<:cs_no:659355468816187405> {} - 아무런 반응이 없으셨어요. 채널 설정을 취소할게요.', suppress=False, delete_after=5)
									else:
										if not cmsg.channel_mentions:
											await ws.edit(content='<:cs_no:659355468816187405> {} - 잘못된 값을 입력하셨어요. 채널 설정을 취소할게요.', suppress=False, delete_after=5)
										else:
											conn = sqlite3.connect("lib/data.db")
											cur = conn.cursor()
											cur.execute("UPDATE customWelcome SET channel = {0} WHERE guild = {1}".format(cmsg.channel_mentions[0].id, ctx.guild.id))
											conn.commit()
											conn.close()
											latest = last.replace("{0.mention}", str(ctx.author.mention))
											latest2 = latest.replace("{1.name}", str(ctx.guild.name))
											latest3 = latest2.replace("{1.member_count}", str(ctx.guild.member_count))
											await ws.edit(content="<:cs_yes:659355468715786262> 설정이 완료되었어요.\n이제 유저가 들어올 때마다 <#{0}> 채널에 {1}(이)라고 알림을 전송할 거에요.\n비활성화하려면 `.아키셋 입장` 명령어를 사용해주세요.".format(cmsg.channel_mentions[0].id, latest3), suppress=False, delete_after=20)
											await cmsg.delete()

						if str(reaction.emoji) == "<:cs_no:659355468816187405>":
							conn = sqlite3.connect("lib/data.db")
							cur = conn.cursor()
							cur.execute("UPDATE customWelcome SET enabled = 'false' WHERE guild = {}".format(ctx.guild.id))
							conn.commit()
							conn.close()
							await ws.clear_reactions()
							await ws.edit(content="<:cs_yes:659355468715786262> {} - 유저 환영 기능을 비활성화했어요. 더 이상 유저가 입장해도 알림을 전송하지 않아요.".format(ctx.author.mention), suppress=False, delete_after=10)

				elif args[0] == "퇴장":
					ws = await ctx.send("<:cs_settings:659355468992610304> {} - 유저 퇴장 알림 기능을 켜시겠어요?\n<:cs_yes:659355468715786262> - 예\n<:cs_no:659355468816187405> - 아니오".format(ctx.author.mention))
					await ws.add_reaction("<:cs_yes:659355468715786262>")
					await ws.add_reaction("<:cs_no:659355468816187405>")
					def check(reaction, user):
						return user == ctx.author and reaction.message.channel == ctx.channel

					try:
						reaction, user = await self.bot.wait_for('reaction_add', timeout=30, check=check)
					except asyncio.TimeoutError:
						await ws.edit(content="<:cs_no:659355468816187405> {} - 아무런 반응이 없으셨어요. 아키셋을 취소할게요.".format(ctx.author.mention), suppress=False, delete_after=5)
					else:
						if str(reaction.emoji) == "<:cs_yes:659355468715786262>":
							conn = sqlite3.connect("lib/data.db")
							cur = conn.cursor()
							cur.execute("UPDATE customBye SET enabled = 'true' WHERE guild = {}".format(ctx.guild.id))
							conn.commit()
							conn.close()
							await ws.edit(content="<:cs_yes:659355468715786262> {} - 유저 퇴장 알림 기능을 활성화했어요.\n메시지와 채널을 변경하시려면 아래 <:cs_settings:659355468992610304> 반응을 눌러주세요!".format(ctx.author.mention), suppress=False)
							await ws.clear_reactions()
							await ws.add_reaction("<:cs_settings:659355468992610304>")
							def check(reaction, user):
								return user == ctx.author and reaction.message.channel == ctx.channel and str(reaction.emoji) == "<:cs_settings:659355468992610304>"

							try:
								reaction, user = await self.bot.wait_for('reaction_add', timeout=30, check=check)
							except asyncio.TimeoutError:
								conn = sqlite3.connect("lib/data.db")
								cur = conn.cursor()
								cur.execute("SELECT * FROM customBye WHERE guild = {}".format(ctx.guild.id))
								rows = cur.fetchall()
								channel = ctx.guild.get_channel(rows[0][3])
								welcomemsg = rows[0][2]
								if channel is None and welcomemsg == 'None':
									await ws.edit(content="<:cs_no:659355468816187405> {} - 유저 퇴장 알림 메시지와 채널을 설정하지 않으시는 걸로 알아둘게요!\n현재 채널이 설정되어 있지 않아요. | 현재 출력되는 메시지가 등록되지 않았어요.".format(ctx.author.mention), suppress=False, delete_after=5)

								if channel is None and welcomemsg != 'None':
									latest = welcomemsg.replace("{0.mention}", str(ctx.author.mention))
									latest2 = latest.replace("{1.name}", str(ctx.guild.name))
									latest3 = latest2.replace("{1.member_count}", str(ctx.guild.member_count))
									await ws.edit(content="<:cs_no:659355468816187405> {0} - 유저 퇴장 알림 메시지와 채널을 설정하지 않으시는 걸로 알아둘게요!\n현재 채널이 설정되어 있지 않아요. | 현재 출력되는 메시지는 {1}(이)에요.".format(ctx.author.mention, welcomemsg), suppress=False, delete_after=5)

								if channel is not None and welcomemsg == 'None':
									await ws.edit(content="<:cs_no:659355468816187405> {0} - 유저 퇴장 알림 메시지와 채널을 설정하지 않으시는 걸로 알아둘게요!\n현재 채널은 <#{1}> 채널이에요. | 현재 출력되는 메시지가 등록되지 않았어요.".format(ctx.author.mention, channel.id), suppress=False, delete_after=5)

								if channel is not None and welcomemsg != 'None':
									latest = welcomemsg.replace("{0.mention}", str(ctx.author.mention))
									latest2 = latest.replace("{1.name}", str(ctx.guild.name))
									latest3 = latest2.replace("{1.member_count}", str(ctx.guild.member_count))
									await ws.edit(content="<:cs_no:659355468816187405> {0} - 유저 퇴장 알림 메시지와 채널을 설정하지 않으시는 걸로 알아둘게요!\n현재 채널은 <#{1}> 채널이에요. | 현재 출력되는 메시지는 {2}(이)에요.".format(ctx.author.mention, channel.id, welcomemsg), suppress=False, delete_after=5)
							else:
								await ws.edit(content="<:cs_settings:659355468992610304> {} - 설정할 메시지를 입력해주세요. 아래는 메시지에 쓸 수 있는 함수에요.\n[태그] - 나간 유저의 태그를 출력합니다.\n[서버] - 서버 이름을 출력합니다.\n[유저수] - 서버의 유저 명수를 출력합니다.".format(ctx.author.mention))
								await ws.clear_reactions()
								def check(msg):
									return msg.author == ctx.author and msg.channel == ctx.channel

								try:
									msg = await self.bot.wait_for('message', timeout=100, check=check)
								except asyncio.TimeoutError:
									await ws.edit(content='<:cs_no:659355468816187405> {} - 아무런 반응이 없으셨어요. 아키셋을 취소할게요.'.format(ctx.author.mention), suppress=False, delete_after=5)
								else:
									conn = sqlite3.connect("lib/data.db")
									cur = conn.cursor()
									a = msg.content.replace("[태그]", "{0.name}#{0.discriminator}")
									b = a.replace("[서버]", "{1.name}")
									last = b.replace("[유저수]", "{1.member_count}")
									cur.execute("UPDATE customBye SET message = '{1}' WHERE guild = {0}".format(ctx.guild.id, last))
									conn.commit()
									conn.close()
									await msg.delete()
									await ws.edit(content="<:cs_settings:659355468992610304> {} - 메시지를 전송할 채널을 멘션해주세요.".format(ctx.author.mention), suppress=False)
									def check(cmsg):
										return cmsg.author == ctx.author and cmsg.channel == ctx.channel

									try:
										cmsg = await self.bot.wait_for('message', timeout=30, check=check)
									except asyncio.TimeoutError:
										await ws.edit(content='<:cs_no:659355468816187405> {} - 아무런 반응이 없으셨어요. 채널 설정을 취소할게요.', suppress=False, delete_after=5)
									else:
										if not cmsg.channel_mentions:
											await ws.edit(content='<:cs_no:659355468816187405> {} - 잘못된 값을 입력하셨어요. 채널 설정을 취소할게요.', suppress=False, delete_after=5)
										else:
											conn = sqlite3.connect("lib/data.db")
											cur = conn.cursor()
											cur.execute("UPDATE customBye SET channel = {0} WHERE guild = {1}".format(cmsg.channel_mentions[0].id, ctx.guild.id))
											conn.commit()
											conn.close()
											latest = last.replace("{0.name}#{0.discriminator}", str(ctx.author.name + "#" + ctx.author.discriminator))
											latest2 = latest.replace("{1.name}", str(ctx.guild.name))
											latest3 = latest2.replace("{1.member_count}", str(ctx.guild.member_count))
											await ws.edit(content="<:cs_yes:659355468715786262> 설정이 완료되었어요.\n이제 유저가 나갈 때마다 <#{0}> 채널에 {1}(이)라고 알림을 전송할 거에요.\n비활성화하려면 `.아키셋 퇴장` 명령어를 사용해주세요.".format(cmsg.channel_mentions[0].id, latest3), suppress=False, delete_after=20)
											await cmsg.delete()

						if str(reaction.emoji) == "<:cs_no:659355468816187405>":
							conn = sqlite3.connect("lib/data.db")
							cur = conn.cursor()
							cur.execute("UPDATE customBye SET enabled = 'false' WHERE guild = {}".format(ctx.guild.id))
							conn.commit()
							conn.close()
							await ws.clear_reactions()
							await ws.edit(content="<:cs_yes:659355468715786262> {} - 유저 퇴장 알림 기능을 비활성화했어요. 더 이상 유저가 나가도 알림을 전송하지 않아요.".format(ctx.author.mention), suppress=False, delete_after=10)

				elif args[0] == "공지":
					announce = await ctx.send("<:cs_settings:659355468992610304> {} - 아키우스의 공지를 받아보시겠어요? [ 비활성화해도 중요공지는 반드시 전송됩니다. ]\n<:cs_yes:659355468715786262> - 예\n<:cs_no:659355468816187405> - 아니오".format(ctx.author.mention))
					await announce.add_reaction("<:cs_yes:659355468715786262>")
					await announce.add_reaction("<:cs_no:659355468816187405>")
					def check(reaction, user):
						return user == ctx.author and reaction.message.channel == ctx.channel

					try:
						reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check=check)
					except asyncio.TimeoutError:
						await announce.clear_reactions()
						await announce.edit(content="<:cs_no:659355468816187405> {} - 아무런 반응이 없으셨어요. 아키셋을 취소할게요.".format(ctx.author.mention), delete_after=5)
					else:
						if str(reaction.emoji) == "<:cs_yes:659355468715786262>":
							await announce.clear_reactions()
							conn = sqlite3.connect("lib/data.db")
							cur = conn.cursor()
							cur.execute("UPDATE announce SET enabled = 'true' WHERE guild = {}".format(ctx.guild.id))
							conn.commit()
							conn.close()
							await announce.edit(content="<:cs_yes:659355468715786262> {} - 아키우스 알림 기능을 활성화했어요.\n채널을 설정하시려면 아래 반응을 추가해주세요.".format(ctx.author.mention))
							await announce.add_reaction("<:cs_settings:659355468992610304>")
							def check(reaction, user):
								return user == ctx.author and reaction.message.channel == ctx.channel and str(reaction.emoji) == "<:cs_settings:659355468992610304>"

							try:
								reaction, user = await self.bot.wait_for('reaction_add', timeout=30, check=check)
							except asyncio.TimeoutError:
								await announce.clear_reactions()
								conn = sqlite3.connect("lib/data.db")
								cur = conn.cursor()
								cur.execute("SELECT * FROM announce WHERE guild = {}".format(ctx.guild.id))
								rows = cur.fetchall()
								if rows[0][2] == 1234:
									await announce.edit(content="<:cs_yes:659355468715786262> {} - 공지 알림 채널을 설정하지 않으시는 걸로 알아둘게요!\n현재 아키우스 공지는 `랜덤 채널`로 전송되고 있어요.".format(ctx.author.mention), delete_after=10)
								else:
									channel = ctx.guild.get_channel(int(rows[0][2]))
									if channel is not None:
										await announce.edit(content="<:cs_yes:659355468715786262> {0} - 공지 알림 채널을 설정하지 않으시는 걸로 알아둘게요!\n현재 아키우스 공지는 <#{1}> 채널로 전송되고 있어요.".format(ctx.author.mention, rows[0][2]), delete_after=10)
									else:
										await announce.edit(content="<:cs_yes:659355468715786262> {} - 공지 알림 채널을 설정하지 않으시는 걸로 알아둘게요!\n현재 아키우스 공지는 `랜덤 채널`로 전송되고 있어요.".format(ctx.author.mention), delete_after=10)
							else:
								await announce.clear_reactions()
								await announce.edit(content="<:cs_settings:659355468992610304> {} - 아키우스의 소식 및 공지를 받아보실 채널을 멘션해주세요.".format(ctx.author.mention))
								def check(msg):
									return msg.author == ctx.author and msg.channel == ctx.channel

								try:
									msg = await self.bot.wait_for('message', timeout=30, check=check)
								except asyncio.TimeoutError:
									await announce.edit(content="<:cs_no:659355468816187405> {} - 아무런 반응이 없으셨어요. 채널 설정을 취소할게요.".format(ctx.author.mention), delete_after=5)
								else:
									if not msg.channel_mentions:
										await announce.edit(content="<:cs_no:659355468816187405> {} - 잘못된 값을 입력하셨어요. 채널 설정을 취소할게요.".format(ctx.author.mention), delete_after=5)
									else:
										chtest = ctx.guild.get_channel(int(msg.channel_mentions[0].id))
										if chtest is not None:
											conn = sqlite3.connect("lib/data.db")
											cur = conn.cursor()
											cur.execute("UPDATE announce SET channel = {0} WHERE guild = {1}".format(chtest.id, ctx.guild.id))
											conn.commit()
											conn.close()
											await announce.edit(content="<:cs_yes:659355468715786262> {0} - 이제 아키우스의 공지 및 알림 사항이 모두 <#{1}> 채널에 전송될거에요!".format(ctx.author.mention, chtest.id))
										else:
											await announce.edit(content="<:cs_no:659355468816187405> {} - 잘못된 값을 입력하셨어요. 채널 설정을 취소할게요.".format(ctx.author.mention), delete_after=5)

						if str(reaction.emoji) == "<:cs_no:659355468816187405>":
							await announce.clear_reactions()
							conn = sqlite3.connect("lib/data.db")
							cur = conn.cursor()
							cur.execute("UPDATE announce SET enabled = 'false' WHERE guild = {}".format(ctx.guild.id))
							conn.commit()
							conn.close()
							await announce.edit(content="<:cs_yes:659355468715786262> {} - 아키우스 알림 기능을 비활성화했어요!".format(ctx.author.mention), delete_after=10)

				elif args[0] == "설정값":
					await ctx.send("<:cs_console:659355468786958356> {} - 등록된 아키셋 설정 값 : `초기`, `공지`, `입장`, `퇴장`, `로그`".format(ctx.author.mention))

				else:
					await ctx.send("<:cs_console:659355468786958356> {} - 그런 값이 등록되지 않았어요. 설정값은 `,아키셋 설정값` 명령어로 확인하실 수 있어요.".format(ctx.author.mention), delete_after=5)

	@commands.command(name="아키")
	async def feed(self, ctx, *args):
		if not args:
			await ctx.send("<:cs_no:659355468816187405> {} - 아무것도 적지 않으시면 보내실 수 없어요.".format(ctx.author.mention))
		else:
			if len(ctx.message.content[4:]) < 5:
				await ctx.send("<:cs_no:659355468816187405> {} - 5글자 미만의 피드백은 보내실 수 없어요.".format(ctx.author.mention))
			else:
				embed = discord.Embed(title="{0.name}#{0.discriminator} ( {0.id} )님의 피드백!".format(ctx.author), description=ctx.message.content[4:], color=0xF4EB94)
				embed.set_author(name="건의 / 문의", icon_url=self.bot.user.avatar_url_as(format="png", size=2048))
				embed.set_thumbnail(url=ctx.author.avatar_url_as(format="png", size=2048))
				embed.set_footer(text="아키우스 | {}".format(version))
				aa = await ctx.send("<:cs_console:659355468786958356> {} - 정말로 개발자에게 이렇게 전송하시겠어요?".format(ctx.author.mention), embed=embed)
				await aa.add_reaction("<:cs_yes:659355468715786262>")
				await aa.add_reaction("<:cs_no:659355468816187405>")
				def check(reaction, user):
					return user == ctx.author and reaction.message.channel == ctx.channel
				
				try:
					reaction, user = await self.bot.wait_for('reaction_add', timeout=30, check=check)
				except asyncio.TimeoutError:
					await aa.edit(content="<:cs_no:659355468816187405> {} - 반응이 없으셔서 전송을 취소했어요.".format(ctx.author.mention), embed=None)
				else:
					if str(reaction.emoji) == "<:cs_yes:659355468715786262>":
						develop = self.bot.get_user(int(owners[0]))
						await develop.send(develop.mention, embed=embed)
						await aa.edit(content="<:cs_yes:659355468715786262> {} - 개발자에게 전송을 완료했어요!".format(ctx.author.mention), embed=None)
					else:
						if str(reaction.emoji) == "<:cs_no:659355468816187405>":
							await aa.edit(content="<:cs_yes:659355468715786262> {} - 피드백 전송을 취소했어요!".format(ctx.author.mention), embed=None)
						else:
							await aa.edit(content="<:cs_no:659355468816187405> {} - 잘못된 이모지를 입력하셨어요. 피드백 전송을 취소했어요!".format(ctx.author.mention), embed=None)


	@arcet.error
	async def seterror(self, ctx, error):
		if isinstance(error, CheckFailure):
			await ctx.send("<:cs_no:659355468816187405> {} - 권한이 없어요. 이 명령어를 사용하려면 `서버 관리` 권한이 있어야 해요.".format(ctx.author.mention))


def setup(bot):
	bot.add_cog(Default(bot))