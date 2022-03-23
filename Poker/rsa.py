from Crypto.Hash import MD5
from Crypto import Random
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
from Crypto.Signature import PKCS1_v1_5 as Signature_pkcs1_v1_5
from Crypto.PublicKey import RSA
import base64

class GameRSA:
    def __init__(self, public_key, private_key):
        #self.public_key = public_key
        #self.private_key = private_key
        self.random_generator = Random.new().read
        self.signer = Signature_pkcs1_v1_5.new(RSA.importKey(private_key))
        self.verifier = Signature_pkcs1_v1_5.new(RSA.importKey(public_key))
        self.cipher_en = Cipher_pkcs1_v1_5.new(RSA.importKey(public_key))
        self.cipher_de = Cipher_pkcs1_v1_5.new(RSA.importKey(private_key))

    def rsa_sign(self, plaintext, hash_algorithm = MD5):
        #signer = Signature_pkcs1_v1_5.new(RSA.importKey(self.private_key))
        hash_value = hash_algorithm.new(plaintext.encode('utf-8'))
        signature = self.signer.sign(hash_value)
        signature = base64.b64encode(signature)
        return signature.decode()


    def rsa_verify(self, sign, plaintext, hash_algorithm = MD5):
        sign = base64.b64decode(sign)
        hash_value = hash_algorithm.new(plaintext.encode('utf-8'))
        #verifier = Signature_pkcs1_v1_5.new(RSA.importKey(self.public_key))
        return verifier.verify(hash_value, sign)

    def rsa_encrpt(self, plaintext):
        #cipher = Cipher_pkcs1_v1_5(RSA.importKey(self.public_key))
        cipher_text = base64.b64encode(self.cipher_en.encrypt(plaintext.encode('utf-8')))
        return cipher_text.decode('utf-8')

    def rsa_decrpt(self, encrypt_text):
        # cipher = Cipher_pkcs1_v1_5(RSA.importKey(self.private_key))
        text = self.cipher_de.decrypt(base64.b64decode(encrypt_text), self.random_generator)
        return text.decode("utf-8")

if __name__ == "__main__":
    a = "0"

    p = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDw7f72WH+4rP+LTKlDlQyQI6fr
a+aFv6kMwLGkvX3A3pP4FUX3QTyCUMo9DDpdu20H+6joBGhw0kWHxkIGn/VK4zqR
DMHqAEHPPI9kuh19KfztvjlWdEg5WKInARass1GWJVikP1PjZcQ2qwTEY5ErndID
HHxSkckuwEy5jNPpXwIDAQAB
-----END PUBLIC KEY-----"""
    q = """-----BEGIN RSA PRIVATE KEY-----
MIICXAIBAAKBgQDw7f72WH+4rP+LTKlDlQyQI6fra+aFv6kMwLGkvX3A3pP4FUX3
QTyCUMo9DDpdu20H+6joBGhw0kWHxkIGn/VK4zqRDMHqAEHPPI9kuh19KfztvjlW
dEg5WKInARass1GWJVikP1PjZcQ2qwTEY5ErndIDHHxSkckuwEy5jNPpXwIDAQAB
AoGAILu1EDMl5ylZ7ssTlCMD+fFeNxYJ09IeXaUwfXlhRHr5D5OUVet/FRV05KZs
p593SMZgRGWU6v8mgzPkdJH2+VozSNBEfD5Pd6wKxfP04zkBfIvkpfXtg5iJ3u9z
RTCLPsb3oIFWQnwjIRb8vbBkr8EXObTMw8MI/D/ca7TiTcECQQD/Z+3PN6VcrymC
j4iO/8aGVRPg5fQdRFH8JOdnPudTVCQ/8typk+gAGB4erXy8txJOFZ7c0glFpZ9V
9GemlmL7AkEA8X1ymzs+zvAWykKBWfTLoXM/1XiXoL+MGoysllRNbjzyaFGN0zKl
iO6l8WCTaDig2cVIEmW6PNJjOrbARCQl7QJAd1p39VgJvLBWc57jr/+zJF9ptLWB
SJP+xBfy03q/2178ua2ilNR7nF+o46krG31p3neYD5VPo+5r8V0PevfYNQJAPTgW
I7AjPgazYFb3v7xFGwrCdfV6SvAELn7XCc0ZTAb7VOLH13CRcmM9gjF/bP5eGJbg
rHlJez3ClhHaL+wSCQJBAMnGmv8Zj6vo3AzjQ6zaBNY6LejxCcnbeHv9Kwo68k2O
D/RCfm0mtrmyRAbqmx+8M7E1jnyMKu0qjBHQG2Jj2Rs=
-----END RSA PRIVATE KEY-----
"""
    b = GameRSA(p, q)
    h = "EtMtW+h/zeWwZDLXKXpgT7AeEQcFQywD7rOhmMT0Qp6A7/HrSVozdJa/fKL53El9/sZjLGAFjIsd5gexz+fRaAtv0D+OOKh3rx+Jo/i7FvewCAoO5NCgABuIlWxsFkG2P1WA2d5w3nK/YGI8A2a23zahRKsirSIYd+qDMNBV8ZU="
    print(b.rsa_decrpt(h))
    print(b.rsa_decrpt(h))
