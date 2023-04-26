""" Encryption for API KEYS """

from flask import current_app
from cryptography.fernet import Fernet

def encrypt_api_key(api_key: str) -> bytes:
    """ Obfuscate API KEY before storing in database """
    fernet_obj = create_fernet_object()

    key_bytes = api_key.encode('utf-8')     # str to bytes
    encrypted_key = fernet_obj.encrypt(key_bytes)
    return encrypted_key


def decrypt_api_key(api_key: bytes) -> str:
    """ Decrypt API KEY using cipher from .env """
    fernet_obj = create_fernet_object()

    decrypted_bytes = fernet_obj.decrypt(api_key)
    decrypted_key = decrypted_bytes.decode('utf-8')

    return decrypted_key


def create_fernet_object() -> Fernet:
    encryption_key = current_app.config.get('ENCRYPTION_KEY')
    fernet_obj = Fernet(encryption_key)
    return fernet_obj
