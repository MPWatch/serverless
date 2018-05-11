import json
import os
from pprint import pprint

import twitter
import boto3


from scripts.categorize import filter_entities, analyze_status, fetch_statuses, get_hashtags
from scripts.dynamodb import save_to_dynamodb
from scripts.tweet import Tweet, TweetEncoder


def main(event, context):
    # event contains json with an MP's twitter handle
    sns_message = event['Records'][0]['Sns']
    mp = sns_message.get('Message', None)
    # if the event is not provided, return error
    if not mp:
        return { "statusCode": 400, "body": json.dumps("Did not provide MP name.") }
    # fetch tweets, parse using Comprehend and write to DB
    try:
        statuses = fetch_statuses(mp, 3)
        for status in statuses:
            comprehend_response, entities = analyze_status(status)
            hashtags = get_hashtags(status)
            # raw dump to DynamoDB. Saves all data as strings.
            save_to_dynamodb(status, comprehend_response, entities)
            # make Tweet object, save to MySQL
            # TODO: save to MySQL db on RDS
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
