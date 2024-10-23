import boto3
from botocore.exceptions import ClientError
from decouple import config
from werkzeug.exceptions import BadRequest


class S3Service:
    def __init__(self):
        self.aws_key = config("AWS_ACCESS_KEY")
        self.aws_secret = config("AWS_SECRET")
        self.region = config("AWS_REGION")
        self.bucket_name = config("AWS_BUCKET")
        self.s3 = boto3.client(
            "s3",
            aws_access_key_id=self.aws_key,
            aws_secret_access_key=self.aws_secret,
        )

    def upload_photo(self, path, key, extension):
        try:
            self.s3.upload_file(
                path,
                self.bucket_name,
                key,
                ExtraArgs={'ContentType': f'image/{extension}'}
            )
            return f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{key}"
        except ClientError:
            raise BadRequest("Unable to upload photo")
