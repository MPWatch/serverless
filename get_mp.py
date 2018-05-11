import json
import os
from datetime import datetime


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
    for mp in mp_list:
        client.invoke(
            FunctionName=os.environ['PROCESS_TWEETS_ARN'],
            Payload=json.dumps({'mp': mp.twitter_handle})
        )
    response = {
        "statusCode": 200,
        "body": "On " + str(datetime.utcnow()) + ", all " + str(len(mp_list)) + " MPs were crawled."
    }

    return response

if __name__ == "__main__":
    m = main('', '')
    print(m)
