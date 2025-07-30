# src/app.py
import os
import boto3

# Get the S3 bucket name from the environment variables
OUTPUT_BUCKET = os.environ.get("OUTPUT_BUCKET")
s3_client = boto3.client("s3")


def lambda_handler(event, context):
    """
    A simple handler to test writing a file to S3.
    """
    try:
        file_content = "Hello from Lambda! The connection to S3 is working."
        file_path = "/tmp/test.txt"

        # Lambda functions can only write to the /tmp directory
        with open(file_path, "w") as f:
            f.write(file_content)

        # Upload the file to our S3 bucket
        s3_client.upload_file(file_path, OUTPUT_BUCKET, "test-output.txt")

        return {
            "statusCode": 200,
            "body": "Successfully created and uploaded test.txt to S3.",
        }

    except Exception as e:
        print(e)
        raise e
