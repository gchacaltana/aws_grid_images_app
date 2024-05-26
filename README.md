# Grid Images APP using AWS

Grid Images App using AWS Services (Lambda, DynamoDB, API Gateway)

## Objetives

* Create a DynamoDB table.
* Update the application to save the mapping from uniqueGridId to an S3 object by using dynamodb.put_item.
* Deploy the application.
* Create an API by using API Gateway.
* Run the API to create the grid image and an S3 presigned URL.

## Technical Knowledge Prerequisites

* You should be familiar with basic navigation of the AWS Management Console.
* You should be comfortable editing and running scripts by using an AWS Cloud9 code editor and terminal.
* You should have a basic understanding of and familiarity with Amazon S3.
* You should have a basic understanding of and familiarity with Amazon API Gateway.


##  Utils Commands

* Create table "GridBuilder" en AWS DynamoDB

```bash
aws dynamodb create-table \
  --table-name GridBuilder \
  --attribute-definitions \
      AttributeName=uniqueGridId,AttributeType=S \
      AttributeName=s3Key,AttributeType=S \
  --key-schema \
      AttributeName=uniqueGridId,KeyType=HASH \
      AttributeName=s3Key,KeyType=RANGE \
  --provisioned-throughput \
      ReadCapacityUnits=5,WriteCapacityUnits=5
```
* Create Lambda Function "Add Image"

```bash
aws lambda create-function \
--function-name add_image \
--runtime python3.9 \
--timeout 30 \
--handler app.lambda_handler \
--role $LAMBDA_ROLE \
--environment Variables={SOURCE_BUCKET=$SOURCE_BUCKET} \
--zip-file fileb://~/environment/api-backend-manual/add_image.zip
```

* Create Lambda Function "Generate Grid Image"

```bash
aws lambda create-function \
--function-name generate_image \
--runtime python3.9 \
--timeout 30 \
--handler app.lambda_handler \
--role $LAMBDA_ROLE \
--environment Variables={SOURCE_BUCKET=$SOURCE_BUCKET, DESTINATION_BUCKET=$DESTINATION_BUCKET} \
--zip-file fileb://~/environment/api-backend-manual/generate_image.zip
```

* View entries that were created in DynamoDB

```bash
aws dynamodb scan --table-name GridBuilder
```