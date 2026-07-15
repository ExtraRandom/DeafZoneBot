from pymongo import MongoClient

import cogs.utils.IO as IO


url = IO.fetch_mongo_url_from_settings()
print(url)
client = MongoClient(url)

db = client['main']

col_practice = db['practice']


def check_for_existing_practice(user_id):
    practice = col_practice.find_one({'_id': str(user_id)})
    return practice
