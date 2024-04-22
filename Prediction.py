import requests
import json
import pandas as pd
import time
import datetime

# Here we define our query as a multi-line string



query = '''
query ($page: Int) {
  Page (page: $page, perPage: 50) {
    media (type: MANGA, popularity_greater: 3500, isAdult: false) { # Insert our variables into the query arguments (id) (type: ANIME is hard-coded in the query)
    	id
    	title{
    		english
    		romaji
    	}
    	status
		startDate {
      		year
      		month
      		day
    	}
    	stats {
      		scoreDistribution {
        		score
        		amount
      		}
      		statusDistribution {
        		status
        		amount
      		}
    	}
    	favourites
    	source
    	genres
    	countryOfOrigin
    	tags{
    		name
    		rank
    		isAdult
    	}
    	endDate{
      		year
      		month
      		day
    	}
    }
  }
}
'''

url = 'https://graphql.anilist.co'

wholeresponse = []

for pagenum in range(2):
#	Make the HTTP Api request
	wholeresponse.append(
		requests.post(url, json={'query': query, 'variables': {'page': pagenum} })
	)


staginglist = []

for responseindex in wholeresponse:
	for mangaindex in json.loads(responseindex.text)['data']['Page']['media']:
		staginglist.append({})
		staginglist[-1]['id'] = mangaindex['id']
		staginglist[-1]['eng_title'] = mangaindex['title']['english']
		staginglist[-1]['rom_title'] = mangaindex['title']['romaji']
		staginglist[-1]['status'] = mangaindex['status']

		if mangaindex['startDate']['month'] is None:
			tempmonth = 6
		else:
			tempmonth = mangaindex['startDate']['month'] 

		if mangaindex['startDate']['day'] is None:
			tempday = 15
		else:
			tempday = mangaindex['startDate']['day'] 

		staginglist[-1]['start_date'] = datetime.datetime(mangaindex['startDate']['year'], tempmonth, tempday)
		for scorebucket in mangaindex['stats']['scoreDistribution']:
			staginglist[-1][f"scored_{scorebucket['score']}_count"] = scorebucket['amount']

		for statusguys in mangaindex['stats']['statusDistribution']:
			staginglist[-1][f"status_{statusguys['status']}_count"] = statusguys['amount']

		staginglist[-1]['favorites'] = mangaindex['favourites']
		staginglist[-1]['source'] = mangaindex['source']

		for genrelisting in mangaindex['genres']:
			staginglist[-1][genrelisting] = 1

		staginglist[-1]['country'] = mangaindex['countryOfOrigin']

		for taglisting in mangaindex['tags']:
			if taglisting['isAdult'] == False:
				staginglist[-1][taglisting['name']] = taglisting['rank']
			else:
				pass

		if mangaindex['endDate']['year'] is None:
			pass
		else:
			if mangaindex['endDate']['month'] is None:
				tempmonthEND = 6
			else:
				tempmonthEND = mangaindex['endDate']['month'] 

			if mangaindex['endDate']['day'] is None:
				tempdayEND = 15
			else:
				tempdayEND = mangaindex['endDate']['day']
			staginglist[-1]['end_date'] = datetime.datetime(mangaindex['endDate']['year'], tempmonthEND, tempdayEND)


df_whole = pd.DataFrame(staginglist)

df_whole['start_date_days'] = (df_whole['start_date'] - datetime.datetime(1950, 1, 1)).transform(lambda x: x.days)
df_whole['end_date_days'] = (df_whole['end_date'] - datetime.datetime(1950, 1, 1)).transform(lambda x: x.days)

nullsubset = ['scored_10_count', 'scored_20_count', 'scored_30_count', 'scored_40_count', 'scored_50_count', 'scored_60_count', 'scored_70_count', 'scored_80_count', 
'scored_90_count', 'scored_100_count', 'status_CURRENT_count', 'status_PLANNING_count', 'status_COMPLETED_count', 'status_DROPPED_count', 'status_PAUSED_count', 'favorites', 
'Comedy', 'Ecchi', 'Fantasy', 'Romance', 'country', 'Demons', 'Heterosexual', 'Ensemble Cast', 'Tsundere', 'Nudity', 'Female Protagonist', 'Magic', 'Primarily Female Cast', 
'Elf', 'Shounen', 'Drama', 'Mystery', 'Supernatural', 'Shoujo', 'Afterlife', 'Reincarnation', 'Tragedy', 'Amnesia', 'Ghost', 'Suicide', 'Urban Fantasy', 'Love Triangle', 
'end_date', 'Action', 'Adventure', 'Isekai', 'Female Harem', 'Horror', 'Psychological', 'Sci-Fi', 'Seinen', 'Primarily Child Cast', 'Denpa', 'Philosophy', 'Body Horror', 
'Cosmic Horror', 'Bullying', 'Gore', 'Military', 'LGBTQ+ Themes', 'Transgender', 'Guns', 'Cars', 'Police', 'Crime', 'Mafia', 'Urban', 'Primarily Adult Cast', 'Gangs', 
'Drugs', 'Age Gap', 'Memory Manipulation', 'Foreign', 'Bisexual', 'War', 'Politics', 'Swordplay', 'Historical', 'Full Color', 'Gender Bending', 'Tomboy', 'School', 
'Crossdressing', 'Drawing', 'Martial Arts', 'Time Skip', 'Male Protagonist', 'Femboy', 'Male Harem', 'Mythology', 'Unrequited Love', 'Battle Royale', 'Espionage', 
'Vampire', 'Witch', 'Super Power', 'Slice of Life', 'Family Life', 'Twins', 'Iyashikei', 'Gods', 'Dragons', 'Tanned Skin', 'Motorcycles', 'College', 'Alchemy', 'Robots', 
'Kuudere', 'Band', 'Ninja', 'School Club', 'Aliens', 'Cult', 'Lost Civilization', 'Dystopian', 'Post-Apocalyptic', 'Detective', 'Conspiracy', 'Cyberpunk', 'Henshin', 
'Tokusatsu', 'Coming of Age', 'Age Regression', 'Slapstick', 'Surreal Comedy', 'Yandere', 'Chibi', "Boys' Love", 'Office Lady', 'Work', 'Anti-Hero', 'Dungeon', 'Gambling', 
'Skeleton', 'Assassins', 'Zombie', 'Found Family', '4-koma', 'Monster Girl', 'Primarily Teen Cast', 'Yuri', 'Fencing', 'Boarding School', 'Meta', 'Parody', 
'Primarily Male Cast', 'Episodic', 'Josei', 'Video Games', 'Cannibalism', 'Survival', 'Slavery', 'Language Barrier', 'Travel', 'Cultivation', 'Wuxia', 'Samurai', 'Fugitive', 
'Oiran', 'Sports', 'Basketball', 'Delinquents', 'Food', 'Youkai', 'Animals', 'Horticulture', 'Classic Literature', 'Death Game', 'Advertisement', 'Fashion', 'Ojou-sama', 
'Villainess', 'Maids', 'Butler', 'Circus', 'Medicine', 'Rural', 'Educational', 'Marriage', 'Artificial Intelligence', 'Baseball', 'Football', 'Archery', 
'Dissociative Identities', 'Adoption', 'Ero Guro', 'Trains', 'start_date_days']

df_whole.loc[:, nullsubset] = df_whole.loc[:, nullsubset].fillna(0)
df_whole.loc[:, 'country'] = df_whole.loc[:, 'country'].fillna('UNKNOWN')

print(df_whole.country.unique())
