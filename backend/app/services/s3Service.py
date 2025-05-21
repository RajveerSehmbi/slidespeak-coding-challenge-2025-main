import os
import boto3
from botocore.exceptions import ClientError
from botocore.client import Config


class S3Service:

    def __init__(self, logger=None):
        region = os.getenv("AWS_DEFAULT_REGION")
        endpoint = f"https://s3.{region}.amazonaws.com"
        self.s3 = boto3.client("s3",
                               region_name=region,
                               endpoint_url=endpoint)
        self.BUCKET = os.getenv("S3_BUCKET_NAME")
        self.logger = logger

    def upload_file_to_s3(self, file_obj, key):
        try:
            self.s3.upload_fileobj(file_obj, self.BUCKET, key)
        except ClientError as e:
            self.logger.error(e)
            return False
        return True

    def generate_presigned_url(self, key, expiry=1800):
        try:
            response = self.s3.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.BUCKET, "Key": key},
                ExpiresIn=expiry,
            )
        except ClientError as e:
            self.logger.error(e)
            return None
        return response

    def delete_file_from_s3(self, key):
        try:
            self.s3.delete_object(Bucket=self.BUCKET, Key=key)
        except ClientError as e:
            self.logger.error(e)
