import os

from cryptography.fernet import Fernet

SESSION_SESSION_ENC = "stats_session.session.enc"

STATS_SESSION_SESSION = "/tmp/stats_session.session"


class TelegramSession:

    def __init__(self, encryptionKeyString):
        self.encryptionKey = encryptionKeyString.encode()

    def __enter__(self):
        encrypted = TelegramSession.read_encrypted()
        decrypted = TelegramSession.decrypt(encrypted)
        TelegramSession.store_decrypted(decrypted)

    def __exit__(self, exc_type, exc_val, exc_tb):
        TelegramSession.delete_session()

    @staticmethod
    def read_encrypted():
        with open(SESSION_SESSION_ENC, "rb") as f:
            return f.read()

    def decrypt(self, encrypted):
        fernet = Fernet(self.encryptionKey)
        return fernet.decrypt(encrypted)

    @staticmethod
    def store_decrypted(decrypted):
        with open(STATS_SESSION_SESSION, "wb") as f:
            f.write(decrypted)

    @staticmethod
    def delete_session():
        os.remove(STATS_SESSION_SESSION)

    @staticmethod
    def get_session_file():
        return STATS_SESSION_SESSION
