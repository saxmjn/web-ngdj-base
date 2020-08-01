import boto3
from app.settings import AWSAccessKeyID, AWSSecretAccessKey

s3_client = boto3.client( 's3', aws_access_key_id=AWSAccessKeyID, aws_secret_access_key=AWSSecretAccessKey)


def initialize_client():
    s3_client = boto3.client( 's3', aws_access_key_id=AWSAccessKeyID, aws_secret_access_key=AWSSecretAccessKey)
    return s3_client


def copy_obj(source_name, destination_name):
    initialize_client().copy_object(
        Bucket='cmn-product-thumbnail',
        CopySource='/cmn-product-image/{}'.format(source_name),
        Key=destination_name,
    )


def delete_obj(obj_name, bucket):
    initialize_client().delete_object(
        Bucket=bucket,
        Key=obj_name,
    )

def delete_objs(objects, bucket):
    initialize_client().delete_objects(
        Bucket=bucket,
        Delete={
            'Objects': objects,
            'Quiet': False,
        }
    )