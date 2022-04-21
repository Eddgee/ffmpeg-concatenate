import boto3
from botocore.exceptions import ClientError

class S3:
    def __init__(self, bucket, aws_access_key_id, aws_secret_access_key):
        self.bucket = bucket
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key


    # uploads video to s3 bucket
    def upload(self, output_video):
        s3 = boto3.client('s3',
                          aws_access_key_id=self.aws_access_key_id,
                          aws_secret_access_key=self.aws_secret_access_key)
        try:
            s3.upload_file(output_video, self.bucket, output_video, ExtraArgs={'ACL': 'public-read'})
        except ClientError as e:
            print("An error while working with boto3: ", e)
