import base64
from Crypto.Cipher import AES
from binascii import b2a_hex,a2b_hex
 
 
class GameAES(object):
    def __init__(self,key):
        #有iv是CBC加密，无偏移量是ECB加密
        self.key = bytes.fromhex(key)
        #self.mode=AES.MODE_CBC
        #self.iv=iv.encode('utf-8')
 
    def pad_byte(self, b):
        '''
        1 先计算所传入bytes类型文本与16的余数
        2 在将此余数转成bytes 当然用0补位也可以
        3 已知了 余数 那么就用余数*被转成的余数，就得到了需要补全的bytes
        4 拼接原有文本和补位
        :param b: bytes类型的文本
        :return: 返回补全后的bytes文本
        '''
        bytes_num_to_pad = AES.block_size - (len(b) % AES.block_size)
        # python3 中默认unicode转码
        # 实际上byte_to_pad 就已经 将 数字转成了unicode 对应的字符  即使你的入参正好是16的倍数，那么bytes也是把列表整体的转码也是有值的
        # 后边解密的匿名函数 拿到最后一个数字后，就知道应该截取的长度，在反着切片就行了
        # 这样保证了数据的完整性
        byte_to_pad = bytes([bytes_num_to_pad])
        padding = byte_to_pad * bytes_num_to_pad
        padded = b + padding
        return padded
 
    def text_encrypt(self,text,iv = ''):
        if iv:
            iv = iv.encode("utf-8")
            cryptor = AES.new(self.key,AES.MODE_CBC,iv)
        else:
            cryptor = AES.new(self.key,AES.MODE_ECB)
        text = text.encode('utf-8')
        text = self.pad_byte(text)
        ciphertext = cryptor.encrypt(text)
        ciphertext = ciphertext.hex()
        return ciphertext
 
 
    def text_decrypt(self,text,iv = ''):
        unpad = lambda s: s[:-ord(s[len(s) - 1:])]
        text = bytes.fromhex(text)
        if iv:
            iv = iv.encode("utf-8")
            cryptor = AES.new(self.key, AES.MODE_CBC, iv)
        else:
            cryptor = AES.new(self.key,AES.MODE_ECB)
        aesStr = cryptor.decrypt(text)
        aesStr = str(unpad(aesStr), encoding='utf8')
        return aesStr

