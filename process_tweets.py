import json
import os
from pprint import pprint
from datetime import datetime


import twitter
import boto3


from scripts.categorize import filter_entities, analyze_status, fetch_statuses
from scripts.get_env_vars import get_aws_db
from scripts.dynamodb import save_to_dynamodb
from scripts.db import DB
from scripts.queries import Query
from scripts.tweet import Tweet


def main(event, context):
    # event contains json with an MP's twitter handle
    sns_message = event['Records'][0]['Sns']
    mp = sns_message.get('Message', None)
    # if the event is not provided, return error
    if not mp:
        return { "statusCode": 400, "body": json.dumps("Did not provide MP name.") }
    # fetch tweets, parse using Comprehend and write to DB
    try:
        # fetch
        statuses = fetch_statuses(mp, 3)
        # open DB connection
        db_creds = get_aws_db()
        db = DB(*db_creds)
        q = Query(db)
        for status in statuses:
            comprehend_response, entities = analyze_status(status)
            # raw dump to DynamoDB. Saves all data as strings.
            save_to_dynamodb(status, comprehend_response, entities)
            # save tweet to RDS
            tweet = Tweet(status)
            timestamp = datetime.now().date()
            q.insert_tweet(tweet.serialize_mysql(timestamp))
            # TODO: save topic
    except Exception as e:
        print(str(e))
    # response
    response = {
        "statusCode": 200,
        "body": json.dumps(event)
    }
    return response


if __name__ == "__main__":
    # hardcoded
    m = main({ 'Records': [{ 'Sns': '@ABridgen' }] }, '')
    print(m)
