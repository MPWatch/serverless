import boto3


def save_to_dynamodb(status, comprehend_response, classified_entities):
    """
    Saves a tweet to DynamoDB.
    """
    # TODO: this is hardcoded, change to dynamodb object
    dynamodb_client = boto3.client('dynamodb', region_name='eu-west-1')
    dynamodb_client.put_item(
        TableName="tweets",
        Item={
            "tweetId": { "S": str(status.id) },
            "tweet": { "S": json.dumps(status._json) },
            "comprehend": { "S": json.dumps(comprehend_response) },
            "classified_entities": { "S": json.dumps(classified_entities) } ,
        }
    )
