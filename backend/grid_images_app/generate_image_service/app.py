"""
Generate Grid Image Service (Lambda Function)
"""

import os
import io
import json
import math
import tempfile
import boto3
from PIL import Image

source_bucket: str = os.getenv("SOURCE_BUCKET")
destination_bucket: str = os.getenv("DESTINATION_BUCKET")
s3 = boto3.client("s3")
dynamodb = boto3.client("dynamodb")
table_name: str = "GridBuilder"
tile_size: int = 100


def lambda_handler(event, context):
    """
    Main Lambda Handler
    """
    unique_grid_id = event["queryStringParameters"]["uniqueGridId"]

    # ask dynanodb for the list of images
    response = dynamodb.query(
        TableName=table_name,
        KeyConditions={
            "uniqueGridId": {
                "AttributeValueList": [{"S": unique_grid_id}], "ComparisonOperator": "EQ"
            }
        }
    )

    source_images = [item["s3Key"] for item in response["Items"]]
    image_count = len(source_images)

    print(f"Converting: {image_count} source images")

    # calculate the height, width of the grid.
    tiles_width = math.floor(math.sqrt(image_count))
    tiles_height = math.ceil(image_count / tiles_width)

    print(f"Creating: {tiles_width} x {tiles_height} grid")

    destination_image = Image.new(mode="RGB", size=(
        tiles_width * tile_size, tiles_height*tile_size)
    )

    for y in range(tiles_height):
        for x in range(tiles_width):
            if source_images:
                filename = source_images.pop()

                # Get the contents of an image in the bucket
                response = s3.get_object(Bucket=source_bucket, Key=filename)
                image_data = response["Body"].read()

                img = Image.open(io.BytesIO(image_data))
                img_width = img.size[0]
                img_height = img.size[1]

                # crop the image to square the length of the shorted side
                crop_square = min(img.size)

                img = img.crop((
                    (img_width - crop_square)//2,
                    (img_height - crop_square)//2,
                    (img_width + crop_square) // 2,
                    (img_height + crop_square)//2
                ))

                img = img.resize((tile_size, tile_size))
                # draw the image onto the destination grid
                destination_image.paste(img, (x*tile_size, y*tile_size))

    # save the output image to the temp file
    temp_file = tempfile.NamedTemporaryFile(suffix='.jpg').name
    destination_image.save(temp_file)
    print(f"Creating temp file {temp_file}")

    destination_key = os.urandom(16).hex()+".jpg"
    with open(temp_file, 'rb') as data:
        # copy  the grid image to a readonly named object in the destination bucket
        s3.put_object(
            Bucket=destination_bucket,
            Key=destination_key,
            Body=data,
            ContentType='image/jpg'
        )

    print(
        f"Saved file to S3 bucket: {destination_bucket}, Key: {destination_key}")

    # build a presigned URL for the S3 bucket
    presigned_url = s3.generate_presigned_url(
        "get_object",
        Params={
            "Bucket": destination_bucket,
            "Key": destination_key
        },
        ExpiresIn=5*60
    )

    return presigned_url
