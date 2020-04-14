#coding=utf8
import discord
from discord.ext import commands
from lib import settings
import sqlite3



Token = settings.Token
prefix = settings.Prefix
owners = settings.Owners
bot = commands.Bot(command_prefix=settings.Prefix)
bot.remove_command('help')



modules = ['modules.Administrator', 
			'modules.EventListener', 
			'modules.Develop', 
			'modules.Owner', 
			'modules.Moderation', 
			'modules.General', 
			'modules.Fun', 
			'modules.Default', 
			'modules.Lugia',
			'modules.Test'
		]

if __name__ == '__main__':
    for module in modules:
        bot.load_extension(module)

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
			await msg.channel.send("<:cs_id:659355469034422282> {} - 등록되지 않은 사용자입니다. `.활성화` 명령어를 사용해보세요!".format(msg.author.mention))
		else:
			if rows[0][1] == "Not Authenticated" and msg.guild.id != 686523016158380052:
				if msg.content == prefix + "활성화" or msg.content == prefix + "아키":
					await bot.process_commands(msg)
				else:
					await msg.channel.send("<:cs_id:659355469034422282> {} - 등록되지 않은 사용자입니다. `.활성화` 명령어를 사용해보세요!".format(msg.author.mention))
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


bot.run(Token)
