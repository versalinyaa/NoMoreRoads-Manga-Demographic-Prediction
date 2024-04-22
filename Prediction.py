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

		if mangaindex['startDate']['year'] is None:
			pass
		else:
			if mangaindex['startDate']['month'] is None:
				tempmonthEND = 6
			else:
				tempmonthEND = mangaindex['startDate']['month'] 

			if mangaindex['startDate']['day'] is None:
				tempdayEND = 15
			else:
				tempdayEND = mangaindex['startDate']['day']
			staginglist[-1]['end_date'] = datetime.datetime(mangaindex['startDate']['year'], tempmonth, tempday)


df_whole = pd.DataFrame(staginglist)

print(df_whole)