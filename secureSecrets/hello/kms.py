# -*- coding: utf-8 -*-
import logging
import json
import time
import math
import os

from aliyunsdkcore import client
from aliyunsdkcore.acs_exception.exceptions import ServerException, ClientException
from aliyunsdkkms.request.v20160120 import DecryptRequest, EncryptRequest, DescribeKeyRequest
from aliyunsdkcore.auth.credentials import StsTokenCredential, AccessKeyCredential

class KMSClient(object):
    def __init__(self, access_key_id, access_key_secret, security_token, region):
        local = bool(os.getenv('local', ""))
        if local:
            acs_creds = AccessKeyCredential(access_key_id, access_key_secret)
        else:
            acs_creds = StsTokenCredential(access_key_id, access_key_secret, security_token)
        self.clt = client.AcsClient(region_id=region, credential=acs_creds)

    def decrypt(self, cipherblob):
        response = None
        retry_count = 15
        i = 0
        while retry_count > 0:
            try:
                request = DecryptRequest.DecryptRequest()
                request.set_CiphertextBlob(cipherblob)
                response = self.clt.do_action_with_exception(request)
                break
            except ClientException as e:
                time.sleep(math.pow(1.5, i))
                i += 1
                retry_count -= 1
            except ServerException as e:
                if e.http_status >= 500:
                    time.sleep(math.pow(1.5, i))
                    i += 1
                    retry_count -= 1
                else:
                    raise e

        if response is None:
            raise Exception("Decrypt failed after retry: %s times" % i)

        res = json.loads(response)
        if 'Plaintext' not in res:
            raise Exception('Invalid response get from KMS: %s', response)
        return res['Plaintext']

    def encrypt(self, key_id, plaintext):
        request = EncryptRequest.EncryptRequest()
        request.set_KeyId(key_id)
        request.set_Plaintext(plaintext)
        response = self.clt.do_action_with_exception(request)
        res = json.loads(response)
        return res['CiphertextBlob']
