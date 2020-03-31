# -*- coding:utf-8 -*-

import hashlib

salt = b'ceb20772e0c9d240c75eb26b0e37abee'


def md5(*args):
    """
    MD5加密，固定salt
    :param args:
    :return:
    """
    m = hashlib.md5()
    m.update(salt)
    for arg in args:
        m.update(arg.encode(encoding='UTF-8'))

    return m.hexdigest()


if __name__ == '__main__':
    pass
