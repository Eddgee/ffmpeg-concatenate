import os
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv
load_dotenv()


# uploads video to s3 bucket
def upload(output_video, bucket):
    s3 = boto3.client('s3',
                      aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                      aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"))
    try:
        s3.upload_file(output_video, bucket, output_video, ExtraArgs={'ACL': 'public-read'})
    except ClientError as e:
        print("An error while working with boto3: ", e)
