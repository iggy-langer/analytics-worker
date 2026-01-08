import logging
import os
from typing import Dict, List, Optional

import boto3
from botocore.exceptions import ClientError
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class Config(BaseModel):
    AWS_REGION: str
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str

def get_config() -> Config:
    config = Config(
        AWS_REGION=os.environ.get('AWS_REGION'),
        AWS_ACCESS_KEY_ID=os.environ.get('AWS_ACCESS_KEY_ID'),
        AWS_SECRET_ACCESS_KEY=os.environ.get('AWS_SECRET_ACCESS_KEY'),
    )
    return config

def get_boto3_client(config: Config) -> boto3.client:
    try:
        client = boto3.client(
            's3',
            region_name=config.AWS_REGION,
            aws_access_key_id=config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
        )
        return client
    except ClientError as e:
        logger.error(e)
        raise

def upload_file_to_s3(client: boto3.client, bucket_name: str, file_path: str, file_name: str) -> str:
    try:
        client.upload_file(
            file_path,
            bucket_name,
            file_name,
            ExtraArgs={'ACL': 'public-read'},
        )
        return f's3://{bucket_name}/{file_name}'
    except ClientError as e:
        logger.error(e)
        raise

def list_files_in_s3(bucket_name: str, client: boto3.client) -> List[str]:
    try:
        response = client.list_objects_v2(Bucket=bucket_name)
        return [obj['Key'] for obj in response.get('Contents', [])]
    except ClientError as e:
        logger.error(e)
        raise

def get_file_from_s3(bucket_name: str, file_name: str, client: boto3.client) -> Optional[bytes]:
    try:
        response = client.get_object(Bucket=bucket_name, Key=file_name)
        return response['Body'].read()
    except ClientError as e:
        logger.error(e)
        return None