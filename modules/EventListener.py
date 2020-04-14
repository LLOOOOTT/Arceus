import discord
from discord.ext import commands
import sqlite3
from lib import settings
import datetime
import asyncio

prefix = settings.Prefix
owners = settings.Owners

class EventListener(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_ready(self):
		print(self.bot.user.name + "#" + self.bot.user.discriminator)
		print(self.bot.user.id)
		print("Listening to messages...")
		conn = sqlite3.connect("lib/data.db")
		cur = conn.cursor()
		cur.execute("UPDATE bot SET uptime = '{}'".format(datetime.datetime.now()))
		conn.commit()
		conn.close()
		while not self.bot.is_closed():
			channel_count = 0
			for guild in self.bot.guilds:
				for channel in guild.text_channels:
					channel_count += 1
				for channel in guild.voice_channels:
					channel_count += 1
			statusmsg = ["{0} | {1}ms".format(self.bot.user.name, round(self.bot.latency * 1000)), 
				"{}개의 서버와 함께".format(len(self.bot.guilds)), 
				"{}명의 유저와 함께".format(len(self.bot.users)), 
				"{}개의 채널과 함께".format(channel_count), 
				"{} 버전에서 작동".format(settings.Version)
			]
			for current_status in statusmsg:
				await self.bot.change_presence(status=discord.Status.idle, activity=discord.Game(current_status))
				await asyncio.sleep(4)
	
	@commands.Cog.listener()
	async def on_guild_join(self, guild):
		while True:
			select = 0
			channel = guild.text_channels[select]
			try:
				await channel.send("{0.name}를 초대해주셔서 감사해요!\n{0.name}를 사용하기 위해서는 서버를 활성화해야 해요.\n이를 위해 `서버 관리` 권한을 가진 유저가 아래 지침을 따라주세요.\n0. 서버를 활성화할 관리자가 `,활성화`를 입력한다.\n1. 봇이 메시지를 관리할 수 있는 채널에서 `,아키셋 초기` 를 입력한다.\n2. 초기 설정이 완료되면 사용하실 수 있어요.\n*초기 설정이 완료되면 초기 설정을 한 채널에 자동적으로 중요 공지가 전달됩니다.*".format(self.bot.user))
				break
			except:
				select += 1

	@commands.Cog.listener()
	async def on_guild_remove(self, guild):
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

	@commands.Cog.listener()
	async def on_member_join(self, member):
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

	@commands.Cog.listener()
	async def on_member_remove(self, member):
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



def setup(bot):
	bot.add_cog(EventListener(bot))