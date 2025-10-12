from cryptography.fernet import Fernet
key = Fernet.generate_key()
# print(key)
print(key.decode())  # save this string securely, e.g. in .env or password manager

fernet = Fernet(key)

with open("stats_session.session", "rb") as f:
    data = f.read()

encrypted = fernet.encrypt(data)

with open("stats_session.session.enc", "wb") as f:
    f.write(encrypted)

print("Encrypted -> stats_session.session.enc")
