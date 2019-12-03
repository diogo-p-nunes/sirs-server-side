from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
import ast
import base64

def encrypt_private_key(a_message, private_key):
    encryptor = PKCS1_OAEP.new(private_key)
    encrypted_msg = encryptor.encrypt(a_message)
    print(encrypted_msg)
    encoded_encrypted_msg = base64.b64encode(encrypted_msg)
    print(encoded_encrypted_msg)
    return encoded_encrypted_msg

def decrypt_public_key(encoded_encrypted_msg, public_key):
    encryptor = PKCS1_OAEP.new(public_key)
    decoded_encrypted_msg = base64.b64decode(encoded_encrypted_msg)
    print(decoded_encrypted_msg)
    decoded_decrypted_msg = encryptor.decrypt(decoded_encrypted_msg)
    print(decoded_decrypted_msg)
    return decoded_decrypted_msg




#*****************
priv = RSA.importKey(open("CA_keys/private.key","r").read())
pub = RSA.importKey(open("CA_keys/public.key","r").read())

m = b"potato"
#h=SHA256.new(m).hexdigest()


encrypted = encrypt_private_key(m,priv)
decrypted = decrypt_public_key(encrypted, pub)
print(decrypted)

