#!/usr/bin/env python3

# Copyright 2024 Zach Lesher <lesher.zachary@protonmail.com>
# SPDX-License-Identifier: MIT

import json
import time
import datetime
import logging
import sys
import requests
import pandas as pd

LOG_LEVEL = logging.DEBUG
log = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stderr, encoding='utf-8', level=LOG_LEVEL)

# Here we define our query as a multi-line string
QUERY = '''
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
URL = 'https://graphql.anilist.co'

# Defining empty list to store the entire set of the
# multiple requests we will make
response_list = []

# Looping through the number of pages needed to grab all of the manga
# records neccesary
while True:
    # 1. Making and saving request
    response = requests.post(URL, json={'query': QUERY,
                                        'variables': {'page': len(response_list) + 1 }},
                                        timeout=15)
    rs_retry_time = response.headers['Retry-After']
    rs_status = response.status_code
    rs_data = json.loads(response.text)['data']

    # 2. Checking if response has hit rate limit; if so wait & try again
    if rs_status == 429:
        log.debug("too many requests! waiting for a bit...")
        log.debug("should wait for %s seconds", rs_retry_time)
        time.sleep(int(rs_retry_time) + 1)
        continue

    # 3. Checking if response is an unexpected code; if so stopping script altogether
    if rs_status not in [200, 429]:
        sys.exit("got a weird response! Try running this script again.")

    log.debug("response_list.len: %s", len(response_list))
    log.debug(rs_status)
    log.debug(response.headers)
    log.debug(rs_data is None)

    # 4. Checking if response got valid but blank response; ending loop if so
    if rs_status == 200 and len(rs_data['Page']['media']) == 0:
        break

    response_list.append(response)

    # 5. Waiting to avoid triggering timeout, if possible
    # TODO: Sleep a random time in range [0.5, 1.5]
    time.sleep(1.25)

# Creating empty list to be filled with dictionaries, each one representing a
# manga, to be later converted to a pandas dataframe
staging_list = []

# A series of loops to un-nest the json file in the format described above
for response in response_list:
    for mangaindex in json.loads(response.text)['data']['Page']['media']:
        entry = {}
        entry['id'] = mangaindex['id']
        entry['eng_title'] = mangaindex['title']['english']
        entry['rom_title'] = mangaindex['title']['romaji']
        entry['status'] = mangaindex['status']
        entry['chapters'] = mangaindex['chapters']
        entry['volumes'] = mangaindex['volumes']

        if mangaindex['startDate']['month'] is None:
            TEMP_MONTH = 5
        else:
            TEMP_MONTH = mangaindex['startDate']['month']

        if mangaindex['startDate']['day'] is None:
            TEMP_DAY = 15
        else:
            TEMP_DAY = mangaindex['startDate']['day']

        try:
            entry['start_date'] = datetime.datetime(
                        mangaindex['startDate']['year'],
                        TEMP_MONTH, TEMP_DAY
                        )
        except:
            pass
        for scorebucket in mangaindex['stats']['scoreDistribution']:
            entry[f"scored_{scorebucket['score']}_count"]\
                = scorebucket['amount']

        for statusguys in mangaindex['stats']['statusDistribution']:
            entry[f"status_{statusguys['status']}_count"]\
                = statusguys['amount']

        entry['favorites'] = mangaindex['favourites']
        entry['source'] = mangaindex['source']

        for genrelisting in mangaindex['genres']:
            entry[genrelisting] = 1

        entry['country'] = mangaindex['countryOfOrigin']

        for taglisting in mangaindex['tags']:
            if taglisting['isAdult'] == False:
                entry[taglisting['name']] = taglisting['rank']
            else:
                pass

        if mangaindex['endDate']['year'] is None:
            pass
        else:
            if mangaindex['endDate']['month'] is None:
                TEMP_MONTH_END = 5
            else:
                TEMP_MONTH_END = mangaindex['endDate']['month']

            if (mangaindex['endDate']['day'] is None
                or mangaindex['endDate']['day'] > 28
                or mangaindex['endDate']['day'] < 0):
                TEMP_DAY_END = 28
            else:
                TEMP_DAY_END = mangaindex['endDate']['day']
            entry['end_date'] = datetime.datetime(
                mangaindex['endDate']['year'], TEMP_MONTH_END, TEMP_DAY_END
            )
        for relationlisting in mangaindex['relations']['edges']:
            if "relation_" + relationlisting['relationType'] in entry:
                entry["relation_" + relationlisting['relationType']] += 1
            else:
                entry["relation_" + relationlisting['relationType']] = 1
            if "relationmedia_" + relationlisting['node']['type'] in entry:
                entry["relationmedia_" + relationlisting['node']['type']] += 1
            else:
                entry["relationmedia_" + relationlisting['node']['type']] = 1

        for characterlisting in mangaindex['characters']['edges']:
            log.debug(characterlisting)
            if characterlisting['role'] == "MAIN":
                if 'Total_Main_Roles' in entry:
                    entry['Total_Main_Roles'] += 1
                else:
                    entry['Total_Main_Roles'] = 1
                if characterlisting['node']['gender'] == "Female":
                    if 'Female_Main_Roles' in entry:
                        entry['Female_Main_Roles'] += 1
                    else:
                        entry['Female_Main_Roles'] = 1
            elif characterlisting['role'] == "SUPPORTING":
                if 'Total_Supporting_Roles' in entry:
                    entry['Total_Supporting_Roles'] += 1
                else:
                    entry['Total_Supporting_Roles'] = 1
                if characterlisting['node']['gender'] == "Female":
                    if 'Female_Supporting_Roles' in entry:
                        entry['Female_Supporting_Roles'] += 1
                    else:
                        entry['Female_Supporting_Roles'] = 1
            elif characterlisting['role'] == "BACKGROUND":
                if 'Total_Background_Roles' in entry:
                    entry['Total_Background_Roles'] += 1
                else:
                    entry['Total_Background_Roles'] = 1

    staging_list.append(entry)

# Converting list of dictionaries into pandas dataframe
df_whole = pd.DataFrame(staging_list)

# Converting start and end dates into number of days since Jan 1, 1950
df_whole['start_date_days'] = (df_whole['start_date']
    - datetime.datetime(1950, 1, 1)).transform(lambda x: x.days)
df_whole['end_date_days'] = (df_whole['end_date']
    - datetime.datetime(1950, 1, 1)).transform(lambda x: x.days)

## Replacing NAs in numeric columns with zeroes
numeric_columns = df_whole.select_dtypes(include=['number']).columns

df_whole.to_csv('manga.csv', index=False)
