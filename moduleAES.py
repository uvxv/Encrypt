from Crypto.Cipher import AES
from Crypto.Util.Padding import pad,unpad
import base64

class AEStxt:

    @staticmethod
    def encrytion(key,text):
        key = key.encode()
        text = text.encode()
        aes = AES.new(key,AES.MODE_ECB)
        crypt = aes.encrypt(pad(text,AES.block_size))
        final_encode = base64.b64encode(crypt)

        return final_encode

    @staticmethod
    def decryption(key , text):
        key = key.encode()
        text = base64.b64decode(text)
        aes = AES.new(key,AES.MODE_ECB)
        crypt = unpad(aes.decrypt(text),AES.block_size).decode('utf=8')

        return crypt

class AESfile:

    @staticmethod
    def encryption(key,file):
        key = key.encode()
        aes = AES.new(key,AES.MODE_ECB)
        crypt = aes.encrypt(pad(file,AES.block_size))
        final_encode = base64.b64encode(crypt)

        return final_encode


    @staticmethod
    def decryption(key, file):
        key = key.encode()
        file = base64.b64decode(file)
        aes = AES.new(key,AES.MODE_ECB)
        crypt = unpad(aes.decrypt(file), AES.block_size)

        return crypt





