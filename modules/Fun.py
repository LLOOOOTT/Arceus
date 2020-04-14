import discord
import sqlite3
from lib import settings
import asyncio
from discord.ext import commands

class Fun(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command(name="에코")
	async def echo(self, ctx):
		conn = sqlite3.connect("lib/data.db")
		cur = conn.cursor()
		cur.execute("SELECT * FROM users WHERE user = {}".format(ctx.author.id))
		rows = cur.fetchall()
		if rows[0][1] == 'Administrator' or rows[0][1] == "Developer" or ctx.author.id in settings.Owners:
			await ctx.message.delete()
			await ctx.send(ctx.message.content[4:])
		else:
			await ctx.message.delete()
			await ctx.send(ctx.message.content[4:])
			await asyncio.sleep(2)
			await ctx.send("라고 말하라고 {0.name}#{0.discriminator}님이 시켰어요!".format(ctx.author))

def setup(bot):
	bot.add_cog(Fun(bot)) 