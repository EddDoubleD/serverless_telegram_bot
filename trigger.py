def handler(event, _):
    body = event["body"]
    return {
        "statusCode": 200,
        "body": body,
    }
