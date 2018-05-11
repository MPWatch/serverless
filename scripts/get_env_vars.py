import os


def get_aws_db():
    db_name = os.environ.get('AWS_DB', None)
    user = os.environ.get('AWS_DB_USER', None)
    password = os.environ.get('AWS_DB_PASSWORD', None)
    host = os.environ.get('AWS_DB_HOST', None)
    return db_name, user, password, host


def get_aws_dynamodb():
    table = os.environ.get('AWS_DYNAMODB_TABLE', None)
    region = os.environ.get('AWS_DYNAMODB_REGION', None)
    return table, region


if __name__ == "__main__":
    print('AWS DynamoDB credentials: ' + str(get_aws_dynamodb()))
    print('AWS DB credentials: ' + str(get_aws_db()))
