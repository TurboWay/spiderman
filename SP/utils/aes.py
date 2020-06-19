#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2020/5/19 19:47
# @Author : way
# @Site : 
# @Describe:  AES 加密解密

import Crypto.Cipher.AES
import Crypto.Random
import base64
import binascii
import json


class Cipher_AES:
    cipher = getattr(Crypto.Cipher, "AES")
    pad = {"default": lambda x, y: x + (y - len(x) % y) * " ".encode("utf-8"),
           "PKCS5Padding": lambda x, y: x + (y - len(x) % y) * chr(y - len(x) % y).encode("utf-8")}
    unpad = {"default": lambda x: x.rstrip(),
             "PKCS5Padding": lambda x: x[:-ord(x[-1])]}
    encode = {"base64": base64.encodebytes,
              "hex": binascii.b2a_hex}
    decode = {"base64": base64.decodebytes,
              "hex": binascii.a2b_hex}

    def __init__(self, key=None, iv=None, cipher_method=None, pad_method="default", code_method=None):
        self.__key = key if key else "abcdefgh12345678"  # 密钥（长度必须为16、24、32）
        self.__iv = iv if iv else Crypto.Random.new().read(Cipher_AES.cipher.block_size)  # 向量（长度与密钥一致，ECB模式不需要）
        self.__cipher_method = cipher_method.upper() if cipher_method and isinstance(cipher_method,
                                                                                     str) else "MODE_ECB"  # 加密方式，["MODE_ECB"|"MODE_CBC"|"MODE_CFB"]等
        self.__pad_method = pad_method  # 填充方式，解决 Java 问题选用"PKCS5Padding"
        self.__code_method = code_method  # 编码方式，目前只有"base64"、"hex"两种
        if self.__cipher_method == "MODE_CBC":
            self.__cipher = Cipher_AES.cipher.new(self.__key.encode("utf-8"), Cipher_AES.cipher.MODE_CBC,
                                                  self.__iv.encode("utf-8"))
        else:
            self.__cipher = Cipher_AES.cipher.new(self.__key.encode("utf-8"), Cipher_AES.cipher.MODE_ECB)

    def __getitem__(self, item):
        def get3value(item):
            return item.start, item.stop, item.step

        type_, method, _ = get3value(item)
        dict_ = getattr(Cipher_AES, type_)
        return dict_[method] if method in dict_ else dict_["default"]

    def encrypt(self, text):
        cipher_text = b"".join([self.__cipher.encrypt(i) for i in self.text_verify(text.encode("utf-8"))])
        encode_func = Cipher_AES.encode.get(self.__code_method)
        if encode_func:
            cipher_text = encode_func(cipher_text)
        return cipher_text.decode("utf-8").rstrip()

    def decrypt(self, cipher_text):
        cipher_text = cipher_text.encode("utf-8")
        decode_func = Cipher_AES.decode.get(self.__code_method)
        if decode_func:
            cipher_text = decode_func(cipher_text)
        return self.pad_or_unpad("unpad", self.__cipher.decrypt(cipher_text).decode("utf-8"))

    def text_verify(self, text):
        while len(text) > len(self.__key):
            text_slice = text[:len(self.__key)]
            text = text[len(self.__key):]
            yield text_slice
        else:
            if len(text) == len(self.__key):
                yield text
            else:
                yield self.pad_or_unpad("pad", text)

    def pad_or_unpad(self, type_, contents):
        lambda_func = self[type_: self.__pad_method]
        return lambda_func(contents, len(self.__key)) if type_ == "pad" else lambda_func(contents)


if __name__ == "__main__":
    key = "123456781234567G"
    iv = "ABCDEF1G34123412"
    cipher_method = "MODE_CBC"
    pad_method = "PKCS5Padding"
    code_method = "base64"
    # cipher_text = Cipher_AES(key, iv, cipher_method, pad_method, code_method).encrypt(text)
    # print(cipher_text)
    cipher_text = "X/T1y9HCjV1+5w0nUKlAefJKLVSCrlzgapCRMpGdyzp60Qc/ERAt7Q3p7+/KkfSnjQu0Wx0t1VR6USm05EuaPseTjgbvdPNS0OxhQEBiR6ptEsD2/s0C1xu/xGIE+6WmB2UB/h82ff00RsPQAu+J4OeT2tLvdzCksdTWD2s5iXgIl7rDqWnkK5SS6Tpq9Id7bBAkOaFVZnhS/E0zU0oOAA95Rxh0hw3N6L9f82b7h9w2D4jvx86ffALWVO0EBRZVZGFoVcl6A1CoI8hV2rAAszj8+vGNPxBTIoYCyb9es+M8xYy5AK2oYLnXH4jUCg0twAYVSVMDAJjBtdue+n5mcYLUzRbYz0vdiDvUOzZWmtb0ZHgJPMcM27DMxk4ZZarE+LuEKeOtZo1VvQeh8h1Gopgfbz0yATGP2hNI8z8FCRKI8+KxdaRA6LUYOCEHDqxerhoGXsXFTao4gqn3cUIR4ANQBuCxzAs5a2k3uNnwFSQTZAIUPp8J4xxAc8zBWY1GL9bJL9l9paDyGh7B/hK84dmVqe1Io5RVVmhbzowhSDuQO/jnRDLmc7LYOF3sm82LGgIPdZncbW4x2ZMgD3WNr9uK80pMCMlPHe3rwyF03Qo9c60t8yk4xdIIoEenx8tOKXTvGpNFj23c1OkZNzHObgi1LfN4LCQnW3JnjlySEsPqjBp+NZysdiM95tqXW1LNxKdQHJjwTn97FaVFgfuSVzwm9iKl4EMVlYf7Wv9KLa+9C28awxRrUTGCIPe9KVR4XBkcjdWXnmjQzk6aQjUEXAFg3HmN8nZy8tFBMQzDq1T47EA6+7dYM0D8kr1sCiTe8Wg1vPNhtXZJfROKGlM0UIAB+4ldqzGLAeMXZOGxcmtMawUK8VoyZi6FRvhV502pLsNQbdLQ/chHlDcWf6PwHjJaI9Q1Tm7OzmzxqnAFS3X5+ipPP7I22X5BFvyejHI2UyfFw+qBbKm9BSBABQIPjN3EQ9TZRycNEF4ZlmHLilSWf9NHFPqgR9KZJr9kZUxctxIfsmkg5tZNJAGF9+/NLRCu2lqDzx6nPngMpfyyVftWzPuEcjEgVLhLMhIMupJbvWSDwa/OmsckZqNTmtU2gQ=="
    text = Cipher_AES(key, iv, cipher_method, pad_method, code_method).decrypt(cipher_text)
    img_urls = json.loads(text)
    print(img_urls)
