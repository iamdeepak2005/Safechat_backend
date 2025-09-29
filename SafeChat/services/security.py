from cryptography.fernet import Fernet

# For demo: use a single app-wide key
SECRET_KEY = Fernet.generate_key()
cipher = Fernet(SECRET_KEY)

def encrypt_file(data: bytes) -> bytes:
    return cipher.encrypt(data)

def decrypt_file(data: bytes) -> bytes:
    return cipher.decrypt(data)

def notify_owner(user, message: str):
    # For now just print (can integrate email/WS notification later)
    print(f"🔔 Notification for {user.username}: {message}")
