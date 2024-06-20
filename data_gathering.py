#!/usr/bin/env python3

# Copyright 2024 Zach Lesher <lesher.zachary@protonmail.com>
# SPDX-License-Identifier: MIT

import requests
import json
import time
import datetime
import pandas as pd
import logging
import sys

LOG_LEVEL = logging.DEBUG
log = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stderr, encoding='utf-8', level=LOG_LEVEL)

# Here we define our query as a multi-line string
query = '''
query ($page: Int) {
  Page (page: $page, perPage: 50) {
    media (type: MANGA, popularity_greater: 200, isAdult: false) {
        id
            chapters
            volumes
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
      relations{
        edges{
          relationType
          node{
              type
          }
        }
      }
      characters{
        edges {
          role
          node{
            gender
          }
        }
      }
    }
  }
}
'''

# Defining URL for request
url = 'https://graphql.anilist.co'

# Defining empty list to store the entire set of the
# multiple requests we will make
response_list = []

# Looping through the number of pages needed to grab all of the manga
# records neccesary
while True:
    # 1. Making and saving request
    response = requests.post(url, json={'query': query, 'variables': {'page': len(response_list) + 1 }})

    # 2. Checking if response has hit rate limit; if so wait & try again
    if response.status_code == 429:
        log.debug("too many requests! waiting for a bit...")
        log.debug(f"should wait for {response.headers['Retry-After']} seconds")
        time.sleep(int(response.headers['Retry-After']) + 1)
        continue

    # 3. Checking if response is an unexpected code; if so stopping script altogether
    if response.status_code not in [200, 429]:
        sys.exit("got a weird response! Try running this script again.")

    # TODO: use me!
    rs_data = json.loads(response.text)['data']

    log.debug(f"response_list.len: {len(response_list)}")
    log.debug(response.status_code)
    log.debug(response.headers)
    log.debug(json.loads(response.text)['data'] is None)

    # 4. Checking if response got valid but blank response; ending loop if so
    if response.status_code == 200 and len(json.loads(response.text)['data']['Page']['media']) == 0:
        log.debug("")
        break

    response_list.append(response)

    # 5. Waiting to avoid triggering timeout, if possible
    # TODO: Sleep a random time in range [0.5, 1.5]
    time.sleep(1.25)

# Creating empty list to be filled with dictionaries, each one representing a
# manga, to be later converted to a pandas dataframe
staginglist = []

# A series of loops to un-nest the json file in the format described above
for responseindex in response_list:
    for mangaindex in json.loads(responseindex.text)['data']['Page']['media']:
        staginglist.append({})
        staginglist[-1]['id'] = mangaindex['id']
        staginglist[-1]['eng_title'] = mangaindex['title']['english']
        staginglist[-1]['rom_title'] = mangaindex['title']['romaji']
        staginglist[-1]['status'] = mangaindex['status']
        staginglist[-1]['chapters'] = mangaindex['chapters']
        staginglist[-1]['volumes'] = mangaindex['volumes']

        if mangaindex['startDate']['month'] is None:
            tempmonth = 5
        else:
            tempmonth = mangaindex['startDate']['month']

        if mangaindex['startDate']['day'] is None:
            tempday = 15
        else:
            tempday = mangaindex['startDate']['day']

        try:
            staginglist[-1]['start_date'] = datetime.datetime(
                        mangaindex['startDate']['year'],
                        tempmonth, tempday
                        )
        except:
            pass
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
                tempmonthEND = 5
            else:
                tempmonthEND = mangaindex['endDate']['month']

            if mangaindex['endDate']['day'] is None or mangaindex['endDate']['day'] > 28 or mangaindex['endDate']['day'] < 0:
                tempdayEND = 28
            else:
                tempdayEND = mangaindex['endDate']['day']
            staginglist[-1]['end_date'] = datetime.datetime(
                mangaindex['endDate']['year'], tempmonthEND, tempdayEND
            )
        for relationlisting in mangaindex['relations']['edges']:
            if "relation_" + relationlisting['relationType'] in staginglist[-1]:
                staginglist[-1]["relation_" + relationlisting['relationType']] += 1
            else:
                staginglist[-1]["relation_" + relationlisting['relationType']] = 1
            if "relationmedia_" + relationlisting['node']['type'] in staginglist[-1]:
                staginglist[-1]["relationmedia_" + relationlisting['node']['type']] += 1
            else:
                staginglist[-1]["relationmedia_" + relationlisting['node']['type']] = 1

        for characterlisting in mangaindex['characters']['edges']:
            log.debug(characterlisting)
            if characterlisting['role'] == "MAIN":
                if 'Total_Main_Roles' in staginglist[-1]:
                    staginglist[-1]['Total_Main_Roles'] += 1
                else:
                    staginglist[-1]['Total_Main_Roles'] = 1
                if characterlisting['node']['gender'] == "Female":
                    if 'Female_Main_Roles' in staginglist[-1]:
                        staginglist[-1]['Female_Main_Roles'] += 1
                    else:
                        staginglist[-1]['Female_Main_Roles'] = 1
            elif characterlisting['role'] == "SUPPORTING":
                if 'Total_Supporting_Roles' in staginglist[-1]:
                    staginglist[-1]['Total_Supporting_Roles'] += 1
                else:
                    staginglist[-1]['Total_Supporting_Roles'] = 1
                if characterlisting['node']['gender'] == "Female":
                    if 'Female_Supporting_Roles' in staginglist[-1]:
                        staginglist[-1]['Female_Supporting_Roles'] += 1
                    else:
                        staginglist[-1]['Female_Supporting_Roles'] = 1
            elif characterlisting['role'] == "BACKGROUND":
                if 'Total_Background_Roles' in staginglist[-1]:
                    staginglist[-1]['Total_Background_Roles'] += 1
                else:
                    staginglist[-1]['Total_Background_Roles'] = 1

# Converting list of dictionaries into pandas dataframe
df_whole = pd.DataFrame(staginglist)

# Converting start and end dates into number of days since Jan 1, 1950
df_whole['start_date_days'] = (df_whole['start_date']
    - datetime.datetime(1950, 1, 1)).transform(lambda x: x.days)
df_whole['end_date_days'] = (df_whole['end_date']
    - datetime.datetime(1950, 1, 1)).transform(lambda x: x.days)

## Replacing NAs in numeric columns with zeroes
numeric_columns = df_whole.select_dtypes(include=['number']).columns

df_whole.to_csv('manga.csv', index=False)
