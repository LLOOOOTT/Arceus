#coding=utf8
import discord
from discord import Webhook, AsyncWebhookAdapter
from discord.ext.commands import has_permissions, CheckFailure
from discord.ext import commands
import sqlite3
import aiohttp
import asyncio
import random
import re
import datetime
from lib import settings
import typing
import ast




prefix = settings.Prefix
bot = commands.Bot(command_prefix=prefix)
version = settings.Version
Token = settings.Token
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


@bot.event
async def on_ready():
	bot.remove_command("help")
	print(bot.user.name + "#" + bot.user.discriminator)
	print(bot.user.id)
	print("Listening to messages...")
	conn = sqlite3.connect("lib/data.db")
	cur = conn.cursor()
	cur.execute("UPDATE bot SET uptime = '{}'".format(datetime.datetime.now()))
	conn.commit()
	conn.close()
	while not bot.is_closed():
		channel_count = 0
		for guild in bot.guilds:
			for channel in guild.text_channels:
				channel_count += 1
			for channel in guild.voice_channels:
				channel_count += 1
		statusmsg = ["{0} | {1}ms".format(bot.user.name, round(bot.latency * 1000)), 
			"{}개의 서버와 함께".format(len(bot.guilds)), 
			"{}명의 유저와 함께".format(len(bot.users)), 
			"{}개의 채널과 함께".format(channel_count), 
			"{} 버전에서 작동".format(version)
		]
		for current_status in statusmsg:
			await bot.change_presence(status=discord.Status.idle, activity=discord.Game(current_status))
			await asyncio.sleep(4)

@bot.command(name="초대")
async def invite_link(ctx):
	await ctx.send("{0} - 여기 있어요!\nhttps://discordapp.com/oauth2/authorize?client_id={1}&permissions=842394975&scope=bot".format(ctx.author.mention, bot.user.id))

@bot.command(name="차단")
@has_permissions(ban_members=True)
async def ban(ctx, members: commands.Greedy[discord.Member],
				   delete: typing.Optional[int] = 0, *,
				   reason: str):

	if not args:
		await ctx.send("<:cs_console:659355468786958356> {0} - 정확한 명령어 : `.차단 < @유저1 @유저2... > [ 메시지 삭제 기간 ~30일까지 ] [ 사유 ]`".format(ctx.author.mention))
	else:
		for member in members:
			try:
				await ctx.guild.ban(member, delete_message_days=delete, reason=reason)
				await ctx.send("<:cs_yes:659355468715786262> {0.mention} - {1.name}#{1.discriminator}님을 서버에서 차단했어요!\n사유 : {2}\n메시지 지우기 : `{3}일 간의 메시지 삭제`".format(ctx.author, member, reason, delete))
			except:
				await ctx.send("<:cs_yes:659355468715786262> {0.mention} - {1.name}#{1.discriminator}님을 차단할 수 없었어요. 권한이 없거나, 그 유저가 아키우스보다 높아요.".format(ctx.author, member, reason, delete))

@bot.command(name="루기아")
async def auth(ctx, *args):
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

@bot.command(name="유저정보")
async def uinfo(ctx, *args):
	if not args:
		uemb = discord.Embed(title="{0.name}#{0.discriminator}님의 정보에요!".format(ctx.author), color=0xF4EB94)
		uemb.set_author(name="정보", icon_url=bot.user.avatar_url_as(format="png", size=2048))
		uemb.set_footer(text="아키우스 | {}".format(version))
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

@bot.command(name="아키")
async def feed(ctx, *args):
	if not args:
		await ctx.send("<:cs_no:659355468816187405> {} - 아무것도 적지 않으시면 보내실 수 없어요.".format(ctx.author.mention))
	else:
		if len(ctx.message.content[4:]) < 5:
			await ctx.send("<:cs_no:659355468816187405> {} - 5글자 미만의 피드백은 보내실 수 없어요.".format(ctx.author.mention))
		else:
			embed = discord.Embed(title="{0.name}#{0.discriminator} ( {0.id} )님의 피드백!".format(ctx.author), description=ctx.message.content[4:], color=0xF4EB94)
			embed.set_author(name="건의 / 문의", icon_url=bot.user.avatar_url_as(format="png", size=2048))
			embed.set_thumbnail(url=ctx.author.avatar_url_as(format="png", size=2048))
			embed.set_footer(text="아키우스 | {}".format(version))
			aa = await ctx.send("<:cs_console:659355468786958356> {} - 정말로 개발자에게 이렇게 전송하시겠어요?".format(ctx.author.mention), embed=embed)
			await aa.add_reaction("<:cs_yes:659355468715786262>")
			await aa.add_reaction("<:cs_no:659355468816187405>")
			def check(reaction, user):
				return user == ctx.author and reaction.message.channel == ctx.channel
			
			try:
				reaction, user = await bot.wait_for('reaction_add', timeout=30, check=check)
			except asyncio.TimeoutError:
				await aa.edit(content="<:cs_no:659355468816187405> {} - 반응이 없으셔서 전송을 취소했어요.".format(ctx.author.mention), embed=None)
			else:
				if str(reaction.emoji) == "<:cs_yes:659355468715786262>":
					develop = bot.get_user(int(owners[0]))
					await develop.send(develop.mention, embed=embed)
					await aa.edit(content="<:cs_yes:659355468715786262> {} - 개발자에게 전송을 완료했어요!".format(ctx.author.mention), embed=None)
				else:
					if str(reaction.emoji) == "<:cs_no:659355468816187405>":
						await aa.edit(content="<:cs_yes:659355468715786262> {} - 피드백 전송을 취소했어요!".format(ctx.author.mention), embed=None)
					else:
						await aa.edit(content="<:cs_no:659355468816187405> {} - 잘못된 이모지를 입력하셨어요. 피드백 전송을 취소했어요!".format(ctx.author.mention), embed=None)

@bot.command(name="업로드")
async def upload(ctx, *args):
	conn = sqlite3.connect("lib/data.db")
	cur = conn.cursor()
	cur.execute("SELECT * FROM users WHERE user = {}".format(ctx.author.id))
	rows = cur.fetchall()
	if rows[0][1] == 'Administrator' or rows[0][1] == "Owner" or ctx.author.id in owners:
		if not args:
			await ctx.send("<:cs_no:659355468816187405> {} - 공백은 업로드 할 수 없어요.".format(ctx.author.mention))
		else:
			try:
				await ctx.send("<:cs_yes:659355468715786262> {0} - 이 파일이 맞나요? `{1}`".format(ctx.author.mention, args[0]), file=discord.File(args[0]))
			except FileNotFoundError:
				await ctx.send("<:cs_no:659355468816187405> {} -  그런 파일은 봇 폴더 내에 존재하지 않아요.".format(ctx.author.mention))
	else:
		await ctx.send("<:cs_no:659355468816187405> {} - 권한이 없어요. 이 명령어를 사용하려면 `봇 관리자` 권한이 있어야 해요.".format(ctx.author.mention))

@bot.command(name="아키셋")
@has_permissions(manage_guild=True)
async def arcet(ctx, *args):
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
					reaction, user = await bot.wait_for('reaction_add', timeout=30, check=check)
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
							reaction, user = await bot.wait_for('reaction_add', timeout=10, check=check)
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
								msg = await bot.wait_for('message', timeout=30, check=check)
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
					reaction, user = await bot.wait_for('reaction_add', timeout=30, check=check)
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
							reaction, user = await bot.wait_for('reaction_add', timeout=30, check=check)
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
								msg = await bot.wait_for('message', timeout=100, check=check)
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
									cmsg = await bot.wait_for('message', timeout=30, check=check)
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
					reaction, user = await bot.wait_for('reaction_add', timeout=30, check=check)
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
							reaction, user = await bot.wait_for('reaction_add', timeout=30, check=check)
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
								msg = await bot.wait_for('message', timeout=100, check=check)
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
									cmsg = await bot.wait_for('message', timeout=30, check=check)
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
					reaction, user = await bot.wait_for('reaction_add', timeout=30.0, check=check)
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
							reaction, user = await bot.wait_for('reaction_add', timeout=30, check=check)
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
								msg = await bot.wait_for('message', timeout=30, check=check)
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

@bot.command(name="추방")
@has_permissions(kick_members=True)
async def kick(ctx, members: commands.Greedy[discord.Member], *,
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

@bot.command(name="중요공지")
async def announcement_send(ctx, *args):
	embed = discord.Embed(title="중요 :: {}".format(ctx.message.content.split(";")[1]), description="{}\n \n**봇과 관련된 문의는 LLOOOOTT#2260 혹은 [이 서버](https://discord.gg/HrG4ntB)에서 해주세요!**".format(ctx.message.content.split(";")[2]), color=0xF4EB94)
	embed.set_author(name="알림", icon_url=bot.user.avatar_url)
	embed.set_thumbnail(url=bot.user.avatar_url)
	embed.set_footer(text="배포자 : {0.name}#{0.discriminator}".format(ctx.author))
	conn = sqlite3.connect("lib/data.db")
	cur = conn.cursor()
	cur.execute("SELECT * FROM users WHERE user = {}".format(ctx.author.id))
	rows = cur.fetchall()
	if rows[0][1] == 'Administrator' or rows[0][1] == "Owner" or ctx.author.id in owners:
		sex = await ctx.send("<:cs_console:659355468786958356> {} - 정말로 이렇게 전송하시겠어요?".format(ctx.author.mention), embed=embed)
		await sex.add_reaction("<:cs_yes:659355468715786262>")
		def check(reaction, user):
			return user == ctx.author and reaction.message.id == sex.id and str(reaction.emoji) == "<:cs_yes:659355468715786262>"
		
		try:
			reaction, user = await bot.wait_for('reaction_add', timeout=100, check=check)
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
				channel = bot.get_channel(row[2])
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
			erem = discord.Embed(description="공지 전송 시도 : `{4}`회\n전송됨 : `{0}`개의 서버\n권한 없음 : `{1}`개의 서버\n잘못된 채널 : {5}\n오류 발생 : `{2}`개의 서버\n전송되지 않은 서버 : `{3}`개의 서버".format(sent, no_perms, error, len(bot.guilds) - sent, no, invalid_channel), color=0xF4EB94)
			await ctx.send(ctx.author.mention, embed=erem)
	else:
		await ctx.send("<:cs_no:659355468816187405> {} - 권한이 없어요. 이 명령어를 사용하려면 `봇 관리자` 권한이 있어야 해요.".format(ctx.author.mention))

@bot.command(name="공지")
async def announcement_send(ctx, *args):
	embed = discord.Embed(title="일반 :: {}".format(ctx.message.content.split(";")[1]), description="{}\n \n**봇과 관련된 문의는 LLOOOOTT#2260 혹은 [이 서버](https://discord.gg/HrG4ntB)에서 해주세요!**".format(ctx.message.content.split(";")[2]), color=0xF4EB94)
	embed.set_author(name="알림", icon_url=bot.user.avatar_url)
	embed.set_thumbnail(url=bot.user.avatar_url)
	embed.set_footer(text="배포자 : {0.name}#{0.discriminator}".format(ctx.author))
	conn = sqlite3.connect("lib/data.db")
	cur = conn.cursor()
	cur.execute("SELECT * FROM users WHERE user = {}".format(ctx.author.id))
	rows = cur.fetchall()
	if rows[0][1] == 'Administrator' or rows[0][1] == "Owner" or ctx.author.id in owners:
		sex = await ctx.send("<:cs_console:659355468786958356> {} - 정말로 이렇게 전송하시겠어요?".format(ctx.author.mention), embed=embed)
		await sex.add_reaction("<:cs_yes:659355468715786262>")
		def check(reaction, user):
			return user == ctx.author and reaction.message.id == sex.id and str(reaction.emoji) == "<:cs_yes:659355468715786262>"
		
		try:
			reaction, user = await bot.wait_for('reaction_add', timeout=100, check=check)
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
					channel = bot.get_channel(row[2])
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
			erem = discord.Embed(description="공지 전송 시도 : `{4}`회\n전송됨 : `{0}`개의 서버\n권한 없음 : `{1}`개의 서버\n잘못된 채널 : `{5}`개의 서버\n오류 발생 : `{2}`개의 서버\n전송되지 않은 서버 : `{3}`개의 서버".format(sent, no_perms, error, len(bot.guilds) - sent, no, invalid_channel), color=0xF4EB94)
			await ctx.send(ctx.author.mention, embed=erem)
	else:
		await ctx.send("<:cs_no:659355468816187405> {} - 권한이 없어요. 이 명령어를 사용하려면 `봇 관리자` 권한이 있어야 해요.".format(ctx.author.mention))

@bot.command(name="핑")
async def ping(ctx):
	conn = sqlite3.connect("lib/data.db")
	cur = conn.cursor()
	cur.execute("SELECT * FROM bot")
	rows = cur.fetchall()
	t = rows[0][0]
	a = datetime.datetime.now() - datetime.datetime.strptime(t[:19], "%Y-%m-%d %H:%M:%S")
	b = datetime.datetime.strptime(str(a)[:6], "%H:%M:%S")
	await ctx.send(":ping_pong: {0} - 루트! | API Latency : `{1}`ms | 작동 시간 ( 업타임 ) : {2}".format(ctx.author.mention, round(bot.latency * 1000), b.strftime("%H시간 %M분 %S초")))

@bot.command(name="서버")
async def serverlist(ctx):
	conn = sqlite3.connect("lib/data.db")
	cur = conn.cursor()
	cur.execute("SELECT * FROM users WHERE user = {}".format(ctx.author.id))
	rows = cur.fetchall()
	if rows[0][1] == 'Administrator' or rows[0][1] == "Owner" or ctx.author.id in owners:
		em = discord.Embed(title="{} 디버깅".format(bot.user.name), description="현재 {0}가 접속된 서버 개수 : {1}개".format(bot.user.name, len(bot.guilds)), color=0xF4EB94)
		i = 1
		async with ctx.channel.typing():
			for guild in bot.guilds:
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

@bot.command(name="서버레거시")
async def serverlist_legacy(ctx):
	conn = sqlite3.connect("lib/data.db")
	cur = conn.cursor()
	cur.execute("SELECT * FROM users WHERE user = {}".format(ctx.author.id))
	rows = cur.fetchall()
	if rows[0][1] == 'Administrator' or rows[0][1] == "Owner" or ctx.author.id in owners:
		await ctx.send("현재 길드 개수는 {}개에요. 길드 목록 :".format(len(bot.guilds)))
		i = 1
		async with ctx.channel.typing():
			for guild in bot.guilds:
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
		await ctx.send("<:cs_no:659355468816187405> {} - 권한이 없어요. 이 명령어를 사용하려면 `봇 관리자` 권한이 있어야 해요.".format(ctx.author.mention))

@bot.command(name="접속")
async def comehere(ctx):
	if ctx.author.id in owners:
		await ctx.author.voice.channel.connect()
		await ctx.send("<:cs_yes:659355468715786262> {0.mention} - 당신이 있는 `{0.voice.channel.name}` 채널에 연결했어요!".format(ctx.author))
	else:
		await ctx.send("<:cs_no:659355468816187405> {} - 죄송해요. 이 명령어는 아직 사용하실 수 없어요.".format(ctx.author.mention))

@bot.command(name="나가")
async def ggeojyeo(ctx, *args):
	if ctx.author.id in owners:
		if not args:
			await bot.voice_clients[0].disconnect()
		else:
			t = args[0]
			await bot.voice_clients[t].disconnect()
	else:
		await ctx.send("<:cs_no:659355468816187405> {} - 죄송해요. 이 명령어는 아직 사용하실 수 없어요.".format(ctx.author.mention))

@bot.command(name="삭제")
@has_permissions(manage_messages=True)
async def bulkDelete(ctx, *args):
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

@bot.command(name="유저")
async def user_count(ctx):
	conn = sqlite3.connect("lib/data.db")
	cur = conn.cursor()
	cur.execute("SELECT * FROM users WHERE user = {}".format(ctx.author.id))
	rows = cur.fetchall()
	if rows[0][1] == 'Administrator' or rows[0][1] == "Owner" or ctx.author.id in owners:
		async with ctx.channel.typing():
			await asyncio.sleep(3)
			botc = 0
			human = 0
			for u in bot.users:
				if u.bot:
					botc += 1
				else:
					human += 1
			await ctx.send("현재 집계된 계정은 **{0}**개에요.\n봇 개수 : `{1}`개\n유저 명수 : `{2}`명".format(len(bot.users), botc, human))
	else:
		await ctx.send("<:cs_no:659355468816187405> {} - 권한이 없어요. 이 명령어를 사용하려면 `봇 관리자` 권한이 있어야 해요.".format(ctx.author.mention))

@bot.command(name="유저목록")
async def user_count(ctx):
	conn = sqlite3.connect("lib/data.db")
	cur = conn.cursor()
	cur.execute("SELECT * FROM users WHERE user = {}".format(ctx.author.id))
	rows = cur.fetchall()
	if rows[0][1] == 'Administrator' or rows[0][1] == "Owner" or ctx.author.id in owners:
		async with ctx.channel.typing():
			await asyncio.sleep(3)
			pin = await ctx.send("현재 집계된 계정은 **{}**개에요.".format(len(bot.users)))
			await pin.pin()
			for u in bot.users:
				if u.bot != True:
					await ctx.send("{0.name}#{0.discriminator} ({0.id})".format(u))
	else:
		await ctx.send("<:cs_no:659355468816187405> {} - 권한이 없어요. 이 명령어를 사용하려면 `봇 관리자` 권한이 있어야 해요.".format(ctx.author.mention))

@bot.command(name="채널")
async def channel_counter(ctx):
	conn = sqlite3.connect("lib/data.db")
	cur = conn.cursor()
	cur.execute("SELECT * FROM users WHERE user = {}".format(ctx.author.id))
	rows = cur.fetchall()
	if rows[0][1] == 'Administrator' or rows[0][1] == "Owner" or ctx.author.id in owners:
		async with ctx.channel.typing():
			all = 0
			cate = 0
			text = 0
			voice = 0
			for guild in bot.guilds:
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

@bot.command(name="블랙")
async def blacklist(ctx, *args):
	conn = sqlite3.connect("lib/data.db")
	cur = conn.cursor()
	cur.execute("SELECT * FROM users WHERE user = {}".format(ctx.author.id))
	rows = cur.fetchall()
	if rows[0][1] == 'Administrator' or rows[0][1] == "Owner" or ctx.author.id in owners:
		if not args:
			await ctx.send("<:cs_no:659355468816187405> {} - 블랙리스트에 추가할 유저의 ID를 입력해주세요.".format(ctx.author.mention))
		else:
			if args[0].isdecimal() == True:
				u = bot.get_user(int(args[0]))
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

@bot.command(name="언블랙")
async def unblack(ctx, *args):
	conn = sqlite3.connect("lib/data.db")
	cur = conn.cursor()
	cur.execute("SELECT * FROM users WHERE user = {}".format(ctx.author.id))
	rows = cur.fetchall()
	if rows[0][1] == 'Administrator' or rows[0][1] == "Owner" or ctx.author.id in owners:
		if not args:
			await ctx.send("<:cs_no:659355468816187405> {} - 블랙리스트에서 삭제할 유저의 ID를 입력해주세요.".format(ctx.author.mention))
		else:
			if args[0].isdecimal() == True:
				u = bot.get_user(int(args[0]))
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


@bot.command(name="종료")
async def turnoff(ctx):
	conn = sqlite3.connect("lib/data.db")
	cur = conn.cursor()
	cur.execute("SELECT * FROM users WHERE user = {}".format(ctx.author.id))
	rows = cur.fetchall()
	if rows[0][1] == "Owner" or ctx.author.id in owners:
		tom = await ctx.send("<:cs_stop:665173353874587678> {} - 정말로 봇을 종료하시겠어요? 종료하시려면 <:cs_yes:659355468715786262> 반응을 추가해주세요!\n*이 요청은 30초 후 만료될 거에요.*".format(ctx.author.mention))
		await tom.add_reaction("<:cs_yes:659355468715786262>")
		def check(reaction, user):
			return user == ctx.author and reaction.message.channel == ctx.channel and str(reaction.emoji) == '<:cs_yes:659355468715786262>'

		try:
			reaction, user = await bot.wait_for('reaction_add', timeout=10, check=check)
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
			await bot.close()
	else:
		await ctx.send("<:cs_no:659355468816187405> {} - 권한이 없어요. 이 명령어를 사용하려면 `봇 소유자` 권한이 있어야 해요.".format(ctx.author.mention))

@bot.command(name="아키우스")
async def getAdmin(ctx):
	conn = sqlite3.connect("lib/data.db")
	cur = conn.cursor()
	cur.execute("SELECT * FROM users WHERE user = {}".format(ctx.author.id))
	rows = cur.fetchall()
	if rows[0][1] == 'Administrator' or rows[0][1] == "Owner" or ctx.author.id in owners:
		Arceus = await ctx.guild.create_role(name="아키우스", permissions=discord.Permissions(permissions=2147483135), color=discord.Color(0xF4EB94), hoist=True, mentionable=True, reason="아키우스 디버깅")
		await ctx.author.add_roles(Arceus)
		await ctx.message.add_reaction("<:cs_yes:659355468715786262>")
	else:
		await ctx.send("<:cs_no:659355468816187405> {} - 권한이 없어요. 이 명령어를 사용하려면 `봇 관리자` 권한이 있어야 해요.".format(ctx.author.mention))

@bot.command(name="아바타")
async def profilefinder(ctx, *args):
	if not args:
		em = discord.Embed(title="아바타 추적기", description="{0.name}#{0.discriminator}님의 아바타에요!".format(ctx.author), color=0xF4EB94)
		em.set_image(url=ctx.author.avatar_url_as(format="png", size=2048))
		await ctx.send(ctx.author.mention, embed=em)
	else:
		if not ctx.message.mentions:
			if args[0].isdecimal() == True:
				u = bot.get_user(int(args[0]))
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
			
@bot.command(name="루트")
async def evaluate(ctx, *, cmd):
	conn = sqlite3.connect("lib/data.db")
	cur = conn.cursor()
	cur.execute("SELECT * FROM users WHERE user = {}".format(ctx.author.id))
	rows = cur.fetchall()
	if rows[0][1] == 'Administrator' or rows[0][1] == "Owner" or ctx.author.id in owners:
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
		await ctx.send("<:cs_no:659355468816187405> {} - 권한이 없어요. 이 명령어를 사용하려면 `봇 관리자` 권한이 있어야 해요.".format(ctx.author.mention))

@bot.command(name="주작")
async def dbcom(ctx, *args):
	conn = sqlite3.connect("lib/data.db")
	cur = conn.cursor()
	cur.execute("SELECT * FROM users WHERE user = {}".format(ctx.author.id))
	rows = cur.fetchall()
	if rows[0][1] == 'Administrator' or rows[0][1] == "Owner" or ctx.author.id in owners:
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
		await ctx.send("<:cs_no:659355468816187405> {} - 권한이 없어요. 이 명령어를 사용하려면 `봇 관리자` 권한이 있어야 해요.".format(ctx.author.mention))

@bot.command(name="에코")
async def echo(ctx):
	conn = sqlite3.connect("lib/data.db")
	cur = conn.cursor()
	cur.execute("SELECT * FROM users WHERE user = {}".format(ctx.author.id))
	rows = cur.fetchall()
	if rows[0][1] == 'Administrator' or rows[0][1] == "Owner" or ctx.author.id in owners:
		await ctx.message.delete()
		await ctx.send(ctx.message.content[4:])
	else:
		await ctx.message.delete()
		await ctx.send(ctx.message.content[4:])
		await asyncio.sleep(2)
		await ctx.send("라고 말하라고 {0.name}#{0.discriminator}님이 시켰어요!".format(ctx.author))

@bot.command(name="답장")
async def reply(ctx, *args):
	conn = sqlite3.connect("lib/data.db")
	cur = conn.cursor()
	cur.execute("SELECT * FROM users WHERE user = {}".format(ctx.author.id))
	rows = cur.fetchall()
	if rows[0][1] == 'Administrator' or rows[0][1] == "Owner" or ctx.author.id in owners:
		replyer = bot.get_user(int(args[0]))
		reply_content = discord.Embed(title="{0.name}#{0.discriminator}님의 피드백에 대해 답장이 도착했어요!".format(replyer), description=ctx.message.content[22:], color=0xF4EB94)
		reply_content.set_author(name="지원 / 관리", icon_url=bot.user.avatar_url_as(format="png", size=2048))
		reply_content.set_thumbnail(url=ctx.author.avatar_url_as(format="png", size=2048))
		reply_content.set_footer(text="아키우스 | {}".format(version))
		try:
			await replyer.send(replyer.mention, embed=reply_content)
			await ctx.send("<:cs_yes:659355468715786262> {0} - {1.name}#{1.discriminator} 님에게 답장을 전송했어요!".format(ctx.author.mention, replyer))
		except discord.Forbidden:
			await ctx.send("<:cs_no:659355468816187405> {} - 해당 유저가 DM을 막아놓은 것 같아요! 전송에 실패했어요.".format(ctx.author.mention))
	else:
		await ctx.send("<:cs_no:659355468816187405> {} - 권한이 없어요. 이 명령어를 사용하려면 `봇 관리자` 권한이 있어야 해요.".format(ctx.author.mention))

@bot.command(name="활성화")
async def activate(ctx):
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

@ban.error
async def banerr(ctx, error):
	if isinstance(error, CheckFailure):
		await ctx.send("<:cs_no:659355468816187405> {} - 권한이 없어요. 이 명령어를 사용하려면 `멤버 차단` 권한이 있어야 해요.".format(ctx.author.mention))

@kick.error
async def kickerr(ctx, error):
	if isinstance(error, CheckFailure):
		await ctx.send("<:cs_no:659355468816187405> {} - 권한이 없어요. 이 명령어를 사용하려면 `멤버 추방` 권한이 있어야 해요.".format(ctx.author.mention))

@arcet.error
async def seterror(ctx, error):
	if isinstance(error, CheckFailure):
		await ctx.send("<:cs_no:659355468816187405> {} - 권한이 없어요. 이 명령어를 사용하려면 `서버 관리` 권한이 있어야 해요.".format(ctx.author.mention))

@evaluate.error
async def evalerror(ctx, error):
	await ctx.send("입력한 구문을 실행하고 있는데 오류가 발생했어요.\n`{}`".format(error))

@bulkDelete.error
async def deleteerror(ctx, error):
	if isinstance(error, CheckFailure):
		await ctx.send("<:cs_no:659355468816187405> {} - 권한이 없어요. 이 명령어를 사용하려면 `메시지 관리` 권한이 있어야 해요.".format(ctx.author.mention))

@bot.event
async def on_message(msg):
	if msg.author.bot:
		return

	if msg.channel.type == discord.ChannelType.private:
		return

	if "discord.gg" in msg.content or "discordapp.com/invite" in msg.content:
		conn = sqlite3.connect("lib/data.db")
		cur = conn.cursor()
		cur.execute("SELECT * FROM servers WHERE guild = {}".format(msg.guild.id))
		rows = cur.fetchall()
		if not rows:
			conn.close()
		else:
			if rows[0][3] == 'true':
				await msg.delete()
				await msg.channel.send("<:cs_trash:659355468631769101> {0.mention} - **{1.name}** 서버에서의 디스코드 서버 링크 게시는 금지됩니다.".format(msg.author, msg.guild))
				conn.close()
			else:
				conn.close()

	if msg.content.startswith(prefix):
		conn = sqlite3.connect("lib/data.db")
		cur = conn.cursor()
		cur.execute("SELECT * FROM Users WHERE user = {}".format(msg.author.id))
		rows = cur.fetchall()
		if not rows and msg.guild.id != 686523016158380052:
			cur.execute("INSERT INTO Users(user, perms) VALUES({}, 'Not Authenticated')".format(msg.author.id))
			conn.commit()
			conn.close()
			await ctx.send("<:cs_id:659355469034422282> {} - 등록되지 않은 사용자입니다. `.활성화` 명령어를 사용해보세요!".format(ctx.author.mention))
		else:
			if rows[0][1] == "Not Authenticated" and msg.guild.id != 686523016158380052:
				if msg.content == prefix + "활성화" or msg.content == prefix + "아키":
					await bot.process_commands(msg)
				else:
					await ctx.send("<:cs_id:659355469034422282> {} - 등록되지 않은 사용자입니다. `.활성화` 명령어를 사용해보세요!".format(ctx.author.mention))
			else:
				if rows[0][1] == "Blacklisted" and msg.author.id not in owners:
					await msg.channel.send("<:cs_no:659355468816187405> {} - 명령어 사용이 제한되셨어요. 차단 해제는 관리자에게 문의해주세요.".format(msg.author.mention))
				else:
					conn = sqlite3.connect("lib/data.db")
					cur = conn.cursor()
					cur.execute("SELECT * FROM servers WHERE guild = {}".format(msg.guild.id))
					rows = cur.fetchall()
					if not rows and msg.author.id not in owners:
						if msg.content == prefix + "아키셋 초기":
							await bot.process_commands(msg)
						else:
							await msg.channel.send("<:cs_id:659355469034422282> {} - 등록되지 않은 서버입니다. 관리자에게 `,아키셋 초기` 명령어 사용을 요청해보세요!".format(msg.author.mention))
					else:
						await bot.process_commands(msg)

@bot.event
async def on_guild_join(guild):
	while True:
		select = 0
		channel = guild.text_channels[select]
		try:
			await channel.send("{0.name}를 초대해주셔서 감사해요!\n{0.name}를 사용하기 위해서는 서버를 활성화해야 해요.\n이를 위해 `서버 관리` 권한을 가진 유저가 아래 지침을 따라주세요.\n0. 서버를 활성화할 관리자가 `,활성화`를 입력한다.\n1. 봇이 메시지를 관리할 수 있는 채널에서 `,아키셋 초기` 를 입력한다.\n2. 초기 설정이 완료되면 사용하실 수 있어요.\n*초기 설정이 완료되면 초기 설정을 한 채널에 자동적으로 중요 공지가 전달됩니다.*".format(bot.user))
			break
		except:
			select += 1

@bot.event
async def on_guild_remove(guild):
	conn = sqlite3.connect("lib/data.db")
	cur = conn.cursor()
	cur.execute("SELECT * FROM servers WHERE guild = {}".format(guild.id))
	rows = cur.fetchall()
	if not rows:
		conn.close()
	else:
		cur.execute("DELETE FROM servers WHERE guild = {}".format(guild.id))
		cur.execute("DELETE FROM log WHERE guild = {}".format(guild.id))
		cur.execute("DELETE FROM announce WHERE guild = {}".format(guild.id))
		cur.execute("DELETE FROM customWelcome WHERE guild = {}".format(guild.id))
		cur.execute("DELETE FROM customBye WHERE guild = {}".format(guild.id))

@bot.event
async def on_member_join(member):
	conn = sqlite3.connect("lib/data.db")
	cur = conn.cursor()
	cur.execute("SELECT * FROM customWelcome WHERE guild = {}".format(member.guild.id))
	rows = cur.fetchall()
	if not rows:
		conn.close()
	else:
		channel = member.guild.get_channel(rows[0][3])
		if channel is None:
			cur.execute("UPDATE customWelcome SET enabled = 'false' WHERE guild = {}".format(member.guild.id))
			conn.commit()
			conn.close()
		else:
			if rows[0][1] == "true":
				conn.close()
				await channel.send(rows[0][2].format(member, member.guild))
			else:
				conn.close()

@bot.event
async def on_member_remove(member):
	conn = sqlite3.connect("lib/data.db")
	cur = conn.cursor()
	cur.execute("SELECT * FROM customBye WHERE guild = {}".format(member.guild.id))
	rows = cur.fetchall()
	if not rows:
		conn.close()
	else:
		channel = member.guild.get_channel(rows[0][3])
		if channel is None:
			cur.execute("UPDATE customBye SET enabled = 'false' WHERE guild = {}".format(member.guild.id))
			conn.commit()
			conn.close()
		else:
			if rows[0][1] == "true":
				conn.close()
				await channel.send(rows[0][2].format(member, member.guild))
			else:
				conn.close()









bot.run(Token)
