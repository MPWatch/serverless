import json
import os
from pprint import pprint

import twitter
import boto3


def fetch_tweets(handle, limit):
    t = twitter.Api(consumer_key=os.environ['TWITTER_CONSUMER_KEY'],
                    consumer_secret=os.environ['TWITTER_CONSUMER_SECRET'],
                    access_token_key=os.environ['TWITTER_ACCESS_TOKEN_KEY'],
                    access_token_secret=os.environ['TWITTER_ACCESS_TOKEN_SECRET'])
    return t.GetUserTimeline(screen_name=handle, count=limit)


def filter_entities(entities):
    return [e['Text'] for e in entities if e['Score'] > 0.8 and '#' not in e['Text'] and 'http' not in e['Text'] and e['Type'] != 'DATE' and e['Type'] != 'QUANTITY']


def analyze_tweets(tweet):
    """
    Using AWS Comprehend, returns List() of valid entities.
    A valid entity is defined as:
     - NOT a DATE
     - NOT a QUANTITY
     - NOT containing HTTP
     - >.8 confidence level
    """
    comprehend = boto3.client(service_name='comprehend', region_name='us-east-1')
    response = comprehend.detect_entities(Text=tweet.text, LanguageCode='en')
    if response['Entities']:
        filtered_entities = filter_entities(response['Entities'])
        return response, filtered_entities
    return None, None


def save_to_dynamodb(tweet, comprehend_response, classified_entities):
    # TODO: this is hardcoded, change to dynamodb object
    dynamodb_client = boto3.client('dynamodb', region_name='eu-west-1')
    dynamodb_client.put_item(
        TableName="tweets",
        Item={
            "tweetId": { "S": str(tweet.id) },
            "tweet": { "S": json.dumps(tweet._json) },
            "comprehend": { "S": json.dumps(comprehend_response) },
            "classified_entities": { "S": json.dumps(classified_entities) } ,
        }
    )


def main(event, context):
    # event contains json with an MP's twitter handle
    mp = event.get('mp', None)
    # if the event is not provided, return error
    if not mp:
        return { "statusCode": 400, "body": json.dumps("Did not provide MP name.") }
    # fetch tweets, parse using Comprehend and write to DB
    try:
        tweets = fetch_tweets(mp, 3)
        for tweet in tweets:
            comprehend_response, entities = analyze_tweets(tweet)
            save_to_dynamodb(tweet, comprehend_response, entities)
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
    m = main({ 'mp': '@ABridgen' }, '')
    print(m)
