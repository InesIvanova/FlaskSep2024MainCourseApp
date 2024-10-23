import boto3
from botocore.exceptions import ClientError
from decouple import config
from werkzeug.exceptions import BadRequest


class SESService:
    def __init__(self):
        self.aws_key = config("AWS_ACCESS_KEY")
        self.aws_secret = config("AWS_SECRET")
        self.region = config("AWS_REGION")
        self.ses = boto3.client(
            'ses',
            aws_access_key_id=self.aws_key,
            aws_secret_access_key=self.aws_secret,
            region_name=self.region
        )

    def send_email(self, recipient, subject, content):
        sender = config("EMAIL_SENDER")
        try:
            resp = self.ses.send_email(
                Source=sender,
                Destination={
                    'ToAddresses': [recipient]
                },
                Message={
                    'Subject': {
                        'Data': subject,
                        'Charset': 'UTF-8'
                    },
                    'Body': {
                        'Text': {
                            'Data': content,
                            'Charset': 'UTF-8'
                        }
                    }
                }
            )
            return resp

        except ClientError:
            raise BadRequest(f"Can not send email")

