import pandas as pd
import requests
import random


def add_channel(store, guild_id, channel_id):
	payload = {
		'guild_id': guild_id,
		'channel_id': channel_id,
		'birthdays': []
	}
	store.document(guild_id).set(payload)
	

def remove_channel(store, guild_id):
	store.document(guild_id).delete()


def get_guilds(store):
	return [doc.to_dict() for doc in store.stream()]


def add_birthday(store, guild_id, msg):
	tokens = msg.split(' ')
	user = tokens[-2]
	date = tokens[-1]
	guild = store.document(guild_id).get().to_dict()
	guild['birthdays'].append({
		'user': user,
		'date': date
	})
	store.document(guild_id).set(guild)
	return user


def get_birthday(guild, date):
	for bday in guild['birthdays']:
		if date == bday['date']:
			return bday['user']
	return None


def goodbye_brain():
	with open('cmd_list.txt', 'r') as f:
		return f.read()
def goodbye_vocal_chords():
	with open('lyrics.txt', 'r') as f:
		return f.read()
def goodbye_johns():
	with open('johns.txt', 'r') as f:
		return f.read()

def goodbye_primos():
	characters = requests.get('https://api.genshin.dev/characters/all').json()
	weapons = requests.get('https://api.genshin.dev/weapons/all').json()

	pool = []
	for character in characters:
		pool.append({
			'name': character['name'],
			'rarity': character['rarity']
		})
	for weapon in weapons:
		pool.append({
			'name': weapon['name'],
			'rarity': weapon['rarity']
		})

	df = pd.DataFrame(pool)
	star_pull = random.choices([5,4,3], [0.6, 5.1, 94.3], k=1)
	star_set = df[df['rarity'] == star_pull[0]]['name'].to_list()
	item_pull = random.choices(star_set, k=1)
	return f'Congratulations! You pulled a(n) {item_pull[0]}!'