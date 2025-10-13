import os

from cryptography.fernet import Fernet

SESSION_SESSION_ENC = "stats_session.session.enc"

STATS_SESSION_SESSION = "/tmp/stats_session.session"


class TelegramSession:

    def __init__(self, encryptionKeyString):
        self.session_encrypted = SESSION_SESSION_ENC
        self.session_decrypted = STATS_SESSION_SESSION
        self.encryptionKey = encryptionKeyString.encode()

    def __enter__(self):
        encrypted = self.read_encrypted()
        decrypted = self.decrypt(encrypted)
        self.store_decrypted(decrypted)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.delete_session()

    def read_encrypted(self):
        with open(self.session_encrypted, "rb") as f:
            return f.read()

    def decrypt(self, encrypted):
        fernet = Fernet(self.encryptionKey)
        return fernet.decrypt(encrypted)

    def store_decrypted(self, decrypted):
        with open(self.session_decrypted, "wb") as f:
            f.write(decrypted)

    def delete_session(self):
        os.remove(self.session_decrypted)

    def get_session_file(self):
        return self.session_decrypted
