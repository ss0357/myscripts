#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex


class prpcrypt():
    def __init__(self,key):
        self.key = key
        self.mode = AES.MODE_CBC

    #加密函数，如果text不足16位就用空格补足为16位，
    #如果大于16当时不是16的倍数，那就补足为16的倍数。
    def encrypt(self,text):
        cryptor = AES.new(self.key,self.mode,b'0000000000000000')
        #这里密钥key 长度必须为16（AES-128）,
        #24（AES-192）,或者32 （AES-256）Bytes 长度
        #目前AES-128 足够目前使用
        length = 16
        count = len(text)
        if count < length:
            add = (length-count)
            #\0 backspace
            text = text + ('\0' * add)
        elif count > length:
            add = (length-(count % length))
            text = text + ('\0' * add)
        self.ciphertext = cryptor.encrypt(text)
        #因为AES加密时候得到的字符串不一定是ascii字符集的，输出到终端或者保存时候可能存在问题
        #所以这里统一把加密后的字符串转化为16进制字符串
        #print(text)
        #print(self.ciphertext)
        #print(b2a_hex(self.ciphertext))
        return b2a_hex(self.ciphertext)

    #解密后，去掉补足的空格用strip() 去掉
    def decrypt(self,text):
        cryptor = AES.new(self.key,self.mode,b'0000000000000000')
        plain_text  = cryptor.decrypt(a2b_hex(text))
        #print(a2b_hex(text))
        #print(plain_text)
        return plain_text.rstrip('\0')



if __name__ == '__main__':
    '''[summary]
    sys.argv[1]: en/de
    sys.argv[2]: key
    sys.argv[3]: passwd/cryptedpasswd
    [description]
    '''
    pc = prpcrypt(sys.argv[2]) #初始化密钥

    if sys.argv[1]=='en':
        e = pc.encrypt(sys.argv[3]) #加密
        print('encrypted passwd: %s' % e)

    if sys.argv[1]=='de':
        d = pc.decrypt(sys.argv[3])
        print('passwd: %s' % d)
