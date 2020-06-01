# -*- coding: utf-8 -*-

from cryptography.fernet import Fernet     #生成密钥的第三方库，Fernet对称加密算法
#Django cookie加密cryptography
class prpcrypt:
    # 密钥 获取密钥
    key = 'P30cMRRBa9kF3YNYpeKNmlUquLsX6ssOuBdy4yZe8wU='

    @classmethod     #定义加密方法
    def encrypt(cls, password):
        fn = Fernet(cls.key)                 #定义加密对象
        password_encode = password.encode()  #先编码
        token = fn.encrypt(password_encode)  #定义token
        return token.decode()                #解码

    @classmethod    #定义解密方法
    def decrypt(cls, password):
        fn = Fernet(cls.key)                 #定义加密对象
        password_encode = password.encode()  #先编码
        token = fn.decrypt(password_encode)  #定义token
        return token.decode()                #解码
