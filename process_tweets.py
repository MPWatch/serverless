import json
import os


def main(event, context):
    response = {
        "statusCode": 200,
        "body": json.dumps(event)
    }

    return response


if __name__ == "__main__":
    m = main('', '')
    print(m)
