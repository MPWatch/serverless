import json
import os


import twitter


from scripts.db import DB
from scripts.queries import Query
from scripts.get_env_vars import get_aws_db


def main(event, context):

    t = twitter.Api(consumer_key=os.environ['TWITTER_CONSUMER_KEY'],
                    consumer_secret=os.environ['TWITTER_CONSUMER_SECRET'],
                    access_token_key=os.environ['TWITTER_ACCESS_TOKEN_KEY'],
                    access_token_secret=os.environ['TWITTER_ACCESS_TOKEN_SECRET'])
    db_creds = get_aws_db()
    db = DB(*db_creds)
    q = Query(db)
    l = [mp.to_json() for mp in q.get_mps()]
    response = {
        "statusCode": 200,
        "body": json.dumps(l)
    }

    return response

if __name__ == "__main__":
    main('', '')
