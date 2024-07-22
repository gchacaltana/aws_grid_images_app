"""
Add Image Service (Lambda Function)
"""
import os
import json
import boto3
import base64

s3 = boto3.client("s3")
dynamodb = boto3.client("dynamodb")
table_name: str = "GridBuilder"
source_bucket: str = os.getenv("SOURCE_BUCKET")


def lambda_handler(event, context):
    """
    Main Lambda Handler
    """
    event_body = base64.b64decode(
        event["body"]) if event["isBase64Encoded"] else event["body"]
    unique_grid_id = event["queryStringParameters"]["uniqueGridId"]

    # save the s3 object with random name
    object_key = os.urandom(16).hex() + ".jpg"
    print(f"Saving to bucket: {source_bucket} key: {object_key}")
    s3.put_object(
        Bucket=source_bucket,
        Key=object_key,
        Body=event_body,
        ContentType='image/jpg'
    )

    # save the mapping from uniqueGridId to s3 object
    dynamodb.put_item(
        TableName=table_name,
        Item={
            "uniqueGridId": {"S": unique_grid_id},
            "s3Key": {"S", object_key}
        }
    )

    return {
        "statusCode": 200,
        "headers": {"access-control-allow-origin": "*"},
        "body": json.dumps({
            "message": "image saved",
            "image_size": len(event_body)
        })
    }
