import os
import logging
import jsonpickle
import boto3
import _json
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all

logger = logging.getLogger()
logger.setLevel(logging.INFO)
patch_all()

client = boto3.client('lambda')
client.get_account_settings()

def lambda_handler(event, context):
    logger.info('## ENVIRONMENT VARIABLES\r' + jsonpickle.encode(dict(**os.environ)))
    logger.info('## EVENT\r' + jsonpickle.encode(event))
    logger.info('## CONTEXT\r' + jsonpickle.encode(context))
    account_settings = client.get_account_settings()
    response_json = [{"description":"The first Widget","id":1,"name":"Widget 1"},{"description":"The second Widget","id":2,"name":"Widget 2"},{"description":"The third Widget","id":3,"name":"Widget 3"}]
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type":"application/json"
        },
        "body": jsonpickle.dumps(account_settings["AccountUsage"]),
        "isBase64Encoded": False
    }
   
     
