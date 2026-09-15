import glob
import json
import logging
import os
import pandas as pd

import boto3
from botocore.exceptions import ClientError

s3 = boto3.client('s3')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

SRC_BUCKET = os.environ.get('SRC_BUCKET','dataobrii-645125774270')
SRC_KEY = os.environ.get('SRC_KEY','file.txt')
TASK_ROOT = os.environ.get('LAMBDA_TASK_ROOT', '.')

CSV_FRAMES = {
    os.path.basename(path): pd.read_csv(path)
    for path in glob.glob(os.path.join(TASK_ROOT, '*.csv'))
}


def handler(event, context):
    logger.info(json.dumps(event))

    try:
        file = s3.get_object(Bucket=SRC_BUCKET, Key=SRC_KEY)
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            logger.info('File does not exist')
        raise

    content_length = file['ContentLength']
    logger.info(f"file {SRC_KEY} ContentLength = {content_length}")

    keys = []
    for key in s3.list_objects_v2(Bucket=SRC_BUCKET)['Contents']:
        keys.append(key['Key'])

    logger.info("Keys: " + json.dumps(keys))

    rows_per_file = pd.Series({name: len(df) for name, df in CSV_FRAMES.items()}, name='rows', dtype='int64')
    logger.info(f"CSV rows per file:\n{rows_per_file.to_string()}")