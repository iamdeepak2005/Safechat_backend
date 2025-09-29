import boto3
from botocore.exceptions import ClientError
from flask import current_app
import uuid


def make_s3_client():
    return boto3.client(
        's3',
        aws_access_key_id=current_app.config.get('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=current_app.config.get('AWS_SECRET_ACCESS_KEY'),
        region_name=current_app.config.get('AWS_REGION')
        )




def generate_presigned_put(bucket, key, expires_in=3600):
    s3 = make_s3_client()
    try:
        url = s3.generate_presigned_url('put_object', Params={'Bucket': bucket, 'Key': key}, ExpiresIn=expires_in)
        return url
    except ClientError as e:
        current_app.logger.error('S3 presign error: %s', e)
        return None




def generate_presigned_get(bucket, key, expires_in=3600):
    s3 = make_s3_client()
    try:
        url = s3.generate_presigned_url('get_object', Params={'Bucket': bucket, 'Key': key}, ExpiresIn=expires_in)
        return url
    except ClientError as e:
        current_app.logger.error('S3 presign error: %s', e)
        return None
def generate_presigned_get(bucket, key, expires_in=3600):
    s3 = make_s3_client()
    try:
        url = s3.generate_presigned_url('get_object', Params={'Bucket': bucket, 'Key': key}, ExpiresIn=expires_in)
        return url
    except ClientError as e:
        current_app.logger.error('S3 presign error: %s', e)
        return None


# helper to build an s3 key
def build_s3_key(owner_id, filename):
    ext = filename.split('.')[-1] if '.' in filename else ''
    key = f"documents/{owner_id}/{uuid.uuid4().hex}.{ext}"
    return key