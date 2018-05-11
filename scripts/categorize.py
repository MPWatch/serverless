import boto3


"""
Helper functions for processing tweets.
"""


def fetch_statuses(handle, limit):
    t = twitter.Api(consumer_key=os.environ['TWITTER_CONSUMER_KEY'],
                    consumer_secret=os.environ['TWITTER_CONSUMER_SECRET'],
                    access_token_key=os.environ['TWITTER_ACCESS_TOKEN_KEY'],
                    access_token_secret=os.environ['TWITTER_ACCESS_TOKEN_SECRET'])
    return t.GetUserTimeline(screen_name=handle, count=limit)


def analyze_status(status):
    """
    Using AWS Comprehend, returns List() of valid entities.
    A valid entity is defined as:
     - NOT a DATE
     - NOT a QUANTITY
     - NOT containing HTTP
     - >.8 confidence level
    """
    # TODO: remove hardcoded region
    comprehend = boto3.client(service_name='comprehend', region_name='us-east-1')
    response = comprehend.detect_entities(Text=status.text, LanguageCode='en')
    if response['Entities']:
        filtered_entities = _filter_entities(response['Entities'])
        return response, filtered_entities
    return None, None


def _filter_entities(entities):
    return [e['Text'] for e in entities if e['Score'] > 0.8 and '#' not in e['Text'] and 'http' not in e['Text'] and e['Type'] != 'DATE' and e['Type'] != 'QUANTITY']


def get_hashtags(status):
    return [h.text for h in status.hashtags if status.hashtags]
