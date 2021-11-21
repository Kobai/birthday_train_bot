import discord
import os
from discord import channel
from discord.ext.tasks import loop
import datetime
from pytz import timezone
from firebase_admin import credentials, firestore, initialize_app
import json

cred = credentials.Certificate('key.json')
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

def add_channel(guild_id,channel_id):
	payload = {
		'guild_id': guild_id,
		'channel_id': channel_id,
		'birthdays': []
	}
	store.document(guild_id).set(payload)
	

def remove_channel(guild_id):
	store.document(guild_id).delete()


def get_guilds():
	return [doc.to_dict() for doc in store.stream()]


def add_birthday(guild_id, msg):
	tokens = msg.split(' ')
	user = tokens[-2]
	date = tokens[-1]
	guild = store.document(guild_id).get().to_dict()
	guild['birthdays'].append({
		'user': user,
		'date': date
	})
	store.document(guild_id).set(guild)


def get_birthday(guild, date):
	for bday in guild['birthdays']:
		if date == bday['date']:
			return bday['user']
	return None


@client.event
async def on_ready():
	print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
	if message.author == client.user:
		return

	if message.content.startswith('!goodbye brain'):
		with open('cmd_list.txt', 'r') as f:
			data = f.read()
		await message.channel.send(data)

	if message.content.startswith('!goodbye vocal chords'):
		with open('lyrics.txt', 'r') as f:
			data = f.read()
		await message.channel.send(data)

	if message.content.startswith('!goodbye birthday train'):
		with open('channel.txt', 'w') as f:
			add_channel(f'{message.guild.id}', f'{message.channel.id}')
		await message.channel.send('Birthday Train has been set up')

	if message.content.startswith('!goodbye millia hp'):
		remove_channel(f'{message.guild.id}')
		await message.channel.send('Birthday Train has already gone')

	if message.content.startswith('!goodbye one year of your life'):
		add_birthday(f'{message.guild.id}', message.content)

	if message.content.startswith('!goodbye friends'):
		await message.channel.send(file=discord.File('no_friends.html'), content='And this is why we don\'t use self destruct')
	
	if message.content.startswith('!goodbye inputs'):
		await message.channel.send('INPUTS WEAVE INTO A SPIRE OF FLAME\nhttps://www.youtube.com/watch?v=EhgDibw7vB4')
		
	if message.content.startswith('!goodbye felix'):
		await message.channel.send('I\'M A FOOL\nI KNOW NOTHING\nI MAY SOUND LIKE A SILLY CLOWN\nAND I WILL TURN MY BACK ON LIFE\nhttps://streamable.com/qxqb9a')


	if message.content.startswith('!goodbye test'):
		if message.content.startswith('!goodbye test guilds'):
			print(get_guilds())
		elif message.content.startswith('!goodbye test train'):
			await test_train()


async def test_train():
	tz = timezone('America/New_York')
	now = datetime.datetime.now(tz)
	day = now.strftime("%A")
	for guild in get_guilds():
		channel = client.get_channel(int(guild['channel_id']))
		user = get_birthday(guild, now.strftime("%m-%d"))
		if user is not None:
			msg = LYRICS['Birthday']
			await channel.send(file=discord.File('Birthday Train.mp3'), content=f'{msg} {user}')
		elif day in LYRICS.keys():
			await channel.send(file=discord.File('Birthday Train.mp3'), content=LYRICS[day])



@loop(minutes=1)
async def bdt():
	tz = timezone('America/New_York')
	now = datetime.datetime.now(tz)
	day = now.strftime("%A")
	if now.strftime('%H:%M') == '16:20':
		for guild in get_guilds():
			channel = client.get_channel(int(guild['channel_id']))
			user = get_birthday(guild, now.strftime("%m-%d"))
			if user is not None:
				msg = LYRICS['Birthday']
				await channel.send(file=discord.File('Birthday Train.mp3'), content=f'{msg} {user}')
			elif day in LYRICS.keys():
				await channel.send(file=discord.File('Birthday Train.mp3'), content=LYRICS[day])


@bdt.before_loop
async def bdt_before():
	await client.wait_until_ready()


bdt.start()
with open('token.txt', 'r') as f:
	token = f.read()
client.run(token)