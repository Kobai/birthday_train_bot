import discord
import os
from discord import channel
from discord.ext.tasks import loop
import datetime
from pytz import timezone
from firebase_admin import credentials, firestore, initialize_app
import requests
import pandas as pd
import json
from util import *

cred = credentials.Certificate('secrets/key.json')
default_app = initialize_app(cred)
db = firestore.client()
store = db.collection('data')

LYRICS = {
	'Sunday':"Where can I find you?\nThe train has already gone\nNot a big deal No need to rush\nLet's go by the Sunday train", 
	'Monday': "Where can I find you?\nThe train has already gone\nNot a big deal No need to rush\nLet's go by the Monday train",
	'Tuesday': 'Oh goodbye Tuesday train\nI\'m looking for a milestone\nBut it doesn\'t seem to be one on this path\nIt\'s far from what I want',
	'Wednesday': "Oh goodbye Wednesday train\nI'm looking for the merit of mine\nBut it does not seem to be one on this path.\nIt's far from what I want.",
	'Thursday': "Where can I find you?\nThe train has already gone\nNot a big deal No need to rush\nLet's go by the Thursday train",
	'Friday': "Oh goodbye Friday train\nI'm looking for decent deal\nBut it seems that there are none on this path\nIt's far from what I want",
	'Saturday': "Oh goodbye Saturday train\nI'm looking for an appropriate time\nBut it seems that there are none on this path\nIt's far from what I want",
	'Birthday': "Oh we can go anywhere\nThere's nothing left here to do\nIt's just perfect No need to rush.\nLet's go by the Birthday train.\nHBD",
}


client = discord.Client()


@client.event
async def on_ready():
	print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
	if message.author == client.user:
		return

	if message.content.startswith('!goodbye brain'):
		await message.channel.send(goodbye_brain())

	if message.content.startswith('!goodbye vocal chords'):
		await message.channel.send(goodbye_vocal_chords())
	
	if message.content.startswith('!goodbye johns'):
		await message.channel.send(goodbye_johns())

	if message.content.startswith('!goodbye birthday train'):
		add_channel(store, f'{message.guild.id}', f'{message.channel.id}')
		await message.channel.send('Birthday Train has been set up')

	if message.content.startswith('!goodbye millia hp'):
		remove_channel(store, f'{message.guild.id}')
		await message.channel.send('Birthday Train has already gone')

	if message.content.startswith('!goodbye one year of your life'):
		user = add_birthday(store, f'{message.guild.id}', message.content)
		await message.channel.send(f'{user} has boarded the Birthday Train')

	if message.content.startswith('!goodbye friends'):
		await message.channel.send(file=discord.File('res/no_friends.html'), content='And this is why we don\'t use self destruct')
	
	if message.content.startswith('!goodbye inputs'):
		await message.channel.send('INPUTS WEAVE INTO A SPIRE OF FLAME\nhttps://www.youtube.com/watch?v=EhgDibw7vB4')
		
	if message.content.startswith('!goodbye felix'):
		await message.channel.send('I\'M A FOOL\nI KNOW NOTHING\nI MAY SOUND LIKE A SILLY CLOWN\nAND I WILL TURN MY BACK ON LIFE\nhttps://streamable.com/qxqb9a')

	if message.content.startswith('!goodbye primos'):
		await message.channel.send(goodbye_primos())

	if message.content.startswith('!goodbye padoru'):
		await message.channel.send(file=discord.File('padoru.gif'), content='hashire sori yo\nkaze no you ni\ntsukimihara wo\npadoru padoru')

	if message.content.startswith('!goodbye patch notes'):
		await message.channel.send(goodbye_patch_notes())

	if message.content.startswith('!goodbye time'):
		await message.channel.send('https://discord.com/channels/381473336250859520/630461683617234964/876190243919892560')

	if message.content.startswith('!goodbye test'):
		await bdt()


@loop(minutes=1)
async def bdt():
	tz = timezone('America/New_York')
	now = datetime.datetime.now(tz)
	day = now.strftime("%A")
	if now.strftime('%H:%M') == '16:20':
		for guild in get_guilds(store):
			channel = client.get_channel(int(guild['channel_id']))
			user = get_birthday(guild, now.strftime("%m-%d"))
			if user is not None:
				msg = LYRICS['Birthday']
				await channel.send(file=discord.File('res/Birthday Train.mp3'), content=f'{msg} {user}')
			elif day in LYRICS.keys():
				await channel.send(file=discord.File('res/Birthday Train.mp3'), content=LYRICS[day])


@bdt.before_loop
async def bdt_before():
	await client.wait_until_ready()


bdt.start()
with open('secrets/token.txt', 'r') as f:
	token = f.read()
client.run(token)
