import boto3
from botocore.client import Config
from django.conf import settings

AWS_S3_REGION_NAME = settings.AWS_S3_REGION_NAME
AWS_STORAGE_BUCKET_NAME = settings.AWS_STORAGE_BUCKET_NAME
AWS_SECRET_ACCESS_KEY = settings.AWS_SECRET_ACCESS_KEY
AWS_ACCESS_KEY_ID = settings.AWS_ACCESS_KEY_ID


def generate_presigned_upload_url(file_name, content_type, user_id):
    s3 = boto3.client(
      's3',
      region_name=AWS_S3_REGION_NAME,
      aws_access_key_id=AWS_ACCESS_KEY_ID,
      aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )

    key = f"recordings/{user_id}/{file_name}"
    url = s3.generate_presigned_url('put_object', Params={
        'Bucket': AWS_STORAGE_BUCKET_NAME,
        'Key': key,
        'ContentType': content_type
    }, ExpiresIn=3600)

    return url, key

def generate_presigned_download_url(key):
    s3 = boto3.client(
        's3',
        region_name=AWS_S3_REGION_NAME,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )

    url = s3.generate_presigned_url('get_object', Params={
        'Bucket': AWS_STORAGE_BUCKET_NAME,
        'Key': key,
    }, ExpiresIn=3600)

    return url

def delete_s3_file(key):
    s3 = boto3.client(
        's3',
        region_name=AWS_S3_REGION_NAME,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )
    s3.delete_object(Bucket=AWS_STORAGE_BUCKET_NAME, Key=key)