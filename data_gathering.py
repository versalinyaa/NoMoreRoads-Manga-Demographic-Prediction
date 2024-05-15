import requests
import json
import time
import datetime
import pandas as pd


# Here we define our query as a multi-line string

query = '''
query ($page: Int) {
  Page (page: $page, perPage: 50) {
    media (type: MANGA, popularity_greater: 3000, isAdult: false) {
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

# Defining URL for request

url = 'https://graphql.anilist.co'

# Defining empty list to store the entire set of the 
# multiple requests we will make

wholeresponse = []

# Looping through the number of pages needed to grab all of the manga
# records neccesary

while True:
	# 1. Making and saving request
	wholeresponse.append(
		requests.post(url, json={'query': query, 'variables': {'page': len(wholeresponse)+1 }})
	)

	# 2. Checking if response has hit rate limit; if so wait & try again
	if wholeresponse[-1].status_code == 429:
		print("too many requests! waiting for a bit...")
		print(f"should wait for {wholeresponse[-1].headers['Retry-After']} seconds")
		time.sleep(int(wholeresponse[-1].headers['Retry-After']) + 1)
		del wholeresponse[-1]

	if len(wholeresponse) > 0:
		# 3. Checking if response is an unexpected code; if so stopping script altogether
		if wholeresponse[-1].status_code not in [200, 429]:
			sys.exit("got a weird response! Try running this script again.")
		print(len(wholeresponse))
		print(wholeresponse[-1].status_code)
		print(wholeresponse[-1].headers)
		print(json.loads(wholeresponse[-1].text)['data'] is None)

		# 4. Checking if response got valid but blank response; ending loop if so
		if wholeresponse[-1].status_code == 200 and len(json.loads(wholeresponse[-1].text)['data']['Page']['media']) == 0:
			print("")
			del wholeresponse[-1]
			break

	# 5. Waiting to avoid triggering timeout, if possible
	time.sleep(1.25)







# Creating empty list to be filled with dictionaries, each one representing a
# manga, to be later converted to a pandas dataframe

staginglist = []

# # A series of loops to un-nest the json file in the format described above

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

		staginglist[-1]['start_date'] = datetime.datetime(
			mangaindex['startDate']['year'], 
			tempmonth, tempday
			)
		for scorebucket in mangaindex['stats']['scoreDistribution']:
			staginglist[-1][f"scored_{scorebucket['score']}_count"]\
				= scorebucket['amount']

		for statusguys in mangaindex['stats']['statusDistribution']:
			staginglist[-1][f"status_{statusguys['status']}_count"]\
				= statusguys['amount']

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
			staginglist[-1]['end_date'] = datetime.datetime(
				mangaindex['endDate']['year'], tempmonthEND, tempdayEND
				)


# # Converting list of dictionaries into pandas dataframe

df_whole = pd.DataFrame(staginglist)

# # Converting start and end dates into number of days since Jan 1, 1950

df_whole['start_date_days'] = (df_whole['start_date']
 - datetime.datetime(1950, 1, 1)).transform(lambda x: x.days)
df_whole['end_date_days'] = (df_whole['end_date']
 - datetime.datetime(1950, 1, 1)).transform(lambda x: x.days)

print(df_whole)

df_whole.to_csv('manga.csv', index=False) 