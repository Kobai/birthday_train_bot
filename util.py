import pandas as pd
import requests
import random
import json


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
	with open('res/cmd_list.txt', 'r') as f:
		return f.read()
def goodbye_vocal_chords():
	with open('res/lyrics.txt', 'r') as f:
		return f.read()
def goodbye_johns():
	with open('res/johns.txt', 'r') as f:
		return f.read()


def goodbye_primos():
	characters = requests.get('https://api.genshin.dev/characters/all').json()
	weapons = requests.get('https://api.genshin.dev/weapons/all').json()

	pool = []
	for character in characters:
		if character['name'] not in ('Traveler', 'Aloy'):
			pool.append({
				'name': character['name'],
				'rarity': character['rarity']
			})
	for weapon in weapons:
		if weapon['location'] == 'Gacha':
			pool.append({
				'name': weapon['name'],
				'rarity': weapon['rarity']
			})
	df = pd.DataFrame(pool)
	star_pull = random.choices([5,4,3], [0.6, 5.1, 94.3], k=1)
	star_set = df[df['rarity'] == star_pull[0]]['name'].to_list()
	item_pull = random.choices(star_set, k=1)
	return f'Congratulations! You pulled: {item_pull[0]}!'

def goodbye_patch_notes():
	res = requests.get('https://api.github.com/repos/Kobai/birthday_train_bot/commits').json()
	commit_msg = res[0]["commit"]["message"]
	return f'```Patch Notes:\n{commit_msg}```'



STATS = ['attack', 'health', 'defense', 'effectiveness', 'effect resistance', 'critical hit chance', 'critical hit damage', 'speed']

def fetch_ocr(url: str) -> str:
    print(f'Making api call with url: {url}')
    payload = {
        'url': url,
        'apikey': 'K82384577388957',
        'OCREngine': 2,
    }
    res = requests.post(
            'https://api.ocr.space/parse/image',
            data=payload,
        )
    res_json = json.loads(res.content.decode()) 
    raw_text = res_json['ParsedResults'][0]['ParsedText']
    print(f'Received: {raw_text}')
    return raw_text
        
def transform_raw_text(raw_text: str) -> pd.DataFrame:
    tokens = raw_text.lower().split('\n')
    while tokens[0] not in STATS:
        tokens = tokens[1:]
    tokens = tokens[2:]
    stats, nums = tokens[:len(tokens)//2],tokens[len(tokens)//2:]
    gear_df = pd.DataFrame({'stat':stats,'values':nums})
    gear_df['stat_type'] = gear_df.apply(lambda row: '%' if row['values'][-1]=='%' else 'flat', axis=1)
    gear_df['values'] = gear_df['values'].str.rstrip("%").astype(float)
    return gear_df

def calculate_gear_score(gear_df: pd.DataFrame) -> str:
    gear_score_df = pd.read_csv('res/gear_score.csv')
    gear_score_df['multiplier'] = gear_score_df['multiplier'].astype(float)
    calc_df = gear_df.merge(gear_score_df,on=['stat','stat_type'])
    calc_df['score'] = calc_df.apply(lambda row: row['values']*row['multiplier'],axis=1)
    score = calc_df['score'].sum()
    return f'Your gear score is: {score}'

def call_gear_score(url: str) -> str:
    try:
        raw_text = fetch_ocr(url)
        gear_df = transform_raw_text(raw_text)
        return calculate_gear_score(gear_df)
    except Exception as e:
        print(f"Error: {e}")
        return "Error: could not successfully calculate gear score"