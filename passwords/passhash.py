import bcrypt

def hash_password(plain_password: str) -> str:
    # Hash the password and return it as a string
    hashed = bcrypt.hashpw(plain_password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8')  # Decode from bytes to string