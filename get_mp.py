import json
import os


import twitter
import boto3


from scripts.db import DB
from scripts.queries import Query
from scripts.get_env_vars import get_aws_db


def main(event, context):
    # retrieve MP list
    db_creds = get_aws_db()
    db = DB(*db_creds)
    q = Query(db)
    mp_list = q.get_mps()
    # lambda client
    client = boto3.client('lambda')
    # crawl Twitter
    t = twitter.Api(consumer_key=os.environ['TWITTER_CONSUMER_KEY'],
                    consumer_secret=os.environ['TWITTER_CONSUMER_SECRET'],
                    access_token_key=os.environ['TWITTER_ACCESS_TOKEN_KEY'],
                    access_token_secret=os.environ['TWITTER_ACCESS_TOKEN_SECRET'])
    statuses = []
    for mp in mp_list[:20]:
        break
        # # TODO: POST request to other lambda function
        # print('Fetching ' + str(mp) + '\'s timeline...')
        # try:
        #     # TODO: break for-loop into different lambda function
        #     # TODO: iterate through database, one call to Twitter API per handle one call to comprehend
        #     statuses.append(t.GetUserTimeline(screen_name=mp.twitter_handle, count=5))
        # except Exception as e:
        #     print(str(e))
    client.invoke(FunctionName=os.environ['PROCESS_TWEETS_ARN'])
    response = {
        "statusCode": 200,
        "body": json.dumps(os.environ['PROCESS_TWEETS_ARN'])
    }

    return response

if __name__ == "__main__":
    m = main('', '')
    print(m)
