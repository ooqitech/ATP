# -*- coding:utf-8 -*-

import json
import sys

from atp.utils.remoteBridge import RemoteBridge
from atp.api.comm_log import logger


class Encryption(RemoteBridge):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def map_to_sign(self, params):
        if isinstance(params, str):
            params_dict = eval(params)
        else:
            params_dict = params
        body = {
            "map_info": params_dict,
        }

        response = self.remote_http_post(self.map_to_sign_url, body)

        r_dict = json.loads(response)
        return r_dict

    def map_to_sign_common(self, params, key='122111111'):
        # params_dict = eval(params)
        if isinstance(params, str):
            params_dict = eval(params)
        else:
            params_dict = params
        body = {
            "secrectKey": key,
            "map_info": params_dict,
        }

        response = self.remote_http_post(self.map_to_sign_common_url, body)

        return response

    def map_to_sign_new(self, params):
        # params_dict = eval(params)
        body = {
            "map_info": params,
        }

        response = self.remote_http_post(self.map_to_sign_url, body)
        r_dict = json.loads(response)
        return r_dict

    def map_to_sign_sdk(self, params, key="111+W111MBs="):
        if isinstance(params, str):
            params_dict = eval(params)
        else:
            params_dict = params
        body = {
            "secrectKey": key,
            "map_info": params_dict,
        }

        response = self.remote_http_post(self.map_to_sign_sdk_url, body)

        r_dict = json.loads(response)
        return r_dict

    def map_to_sign_capital_hub(self, params):
        if isinstance(params, str):
            params_dict = eval(params)
        else:
            params_dict = params
        body = {
            "map_info": params_dict,
        }

        response = self.remote_http_post(self.map_to_sign_capital_hub_url, body)

        r_dict = json.loads(response)
        return r_dict

    def encrypt_public_key(self, plainText, publicKeyText):
        body = {
            "publicKey": publicKeyText,
            "plainText": plainText,
        }

        response = self.remote_http_post(self.encrypt_public_key_url, body)

        r_dict = json.loads(response)
        try:
            content = r_dict["content"]
        except KeyError:
            raise KeyError("调用{func_name}方法后, 解析返回内容失败, 缺少content".format(func_name=sys._getframe().f_code.co_name))

        return content

    def encrypt_public_key_df(self, plainText, publicKeyText):
        body = {
            "publicKey": publicKeyText,
            "plainText": plainText,
        }

        response = self.remote_http_post(self.encrypt_public_key_url_df, body)

        r_dict = json.loads(response)
        try:
            content = r_dict["content"]
        except KeyError:
            raise KeyError("调用{func_name}方法后, 解析返回内容失败, 缺少content".format(func_name=sys._getframe().f_code.co_name))

        return content

    def encryptByPublicKey(self, content, keyPair):
        body = {
            "publicKey": keyPair,
            "plainText": content,
        }

        response = self.remote_http_post(self.encrypt_public_key_url, body)

        r_dict = json.loads(response)
        try:
            content = r_dict["content"]
        except KeyError:
            raise KeyError("调用{func_name}方法后, 解析返回内容失败, 缺少content".format(func_name=sys._getframe().f_code.co_name))

        return content

    def aes(self, jsKey, text):
        body = {
            "publicKey": jsKey,
            "plainText": text,
        }

        response = self.remote_http_post(self.aes_url, body)

        r_dict = json.loads(response)
        try:
            content = r_dict["content"]
        except KeyError:
            raise KeyError("调用{func_name}方法后, 解析返回内容失败, 缺少content".format(func_name=sys._getframe().f_code.co_name))

        return content

    def encrypt(self, params_source, key="lV9pp312312312jYHkg=="):
        body = {
            "publicKey": key,
            "plainText": params_source,
        }

        response = self.remote_http_post(self.encrypt_url, body)

        r_dict = json.loads(response)
        try:
            content = r_dict["content"]
        except KeyError:
            raise KeyError("调用{func_name}方法后, 解析返回内容失败, 缺少content".format(func_name=sys._getframe().f_code.co_name))

        return content

    def decript(self, Key, cipherText, ec=None):
        if ec:
            body = {
                "cipherText": cipherText,
                "password": Key,
                "ec": int(ec),
            }
        else:
            body = {
                "cipherText": cipherText,
                "password": Key,
            }

        response = self.remote_http_post(self.decrypt_url, body)

        return response


if __name__ == '__main__':
    '''
    test cases
    '''
    e = Encryption()

    result = e.map_to_sign_common(json.dumps({
        "content": "13213",
        "timestamp": "1465802761723",
        "contact": "13585662222"
    }))
    print(result)
