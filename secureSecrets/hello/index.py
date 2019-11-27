# -*- coding: utf-8 -*-
import logging
import os

from kms import KMSClient

user_name = ''
password = ''

def initializer(context):
    logger = logging.getLogger()
    logger.info('Decrypting secure secrets')
    global user_name
    global password

    creds = context.credentials
    kms_client = KMSClient(creds.access_key_id, creds.access_key_secret, creds.security_token, context.region)
    try:
        user_name = kms_client.decrypt(os.environ['SecureUserName'])
        password = kms_client.decrypt(os.environ['SecurePassword'])
        logger.info('Successfully decrypted secrets')
    except KeyError as e:
        logger.exception('Key not found')
        raise e

def handler(event, context):
    logger = logging.getLogger()
    # DO NOT log secrets in production
    logger.info('Decrypted user name: %s, password: %s', user_name, password)
    return {}

