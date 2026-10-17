import os
from datetime import datetime, timedelta, timezone
import jwt
from pwdlib import PasswordHash

hasher = PasswordHash.recommended()
ALGORITHM = 'HS256'

def hash_password(password: str) -> str:
    return hasher.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    try:
        return hasher.verify(password, hashed)
    except Exception:
        return False

def create_token(user_id: int) -> str:
    secret = os.getenv('JWT_SECRET_KEY')
    if not secret or len(secret) < 32:
        raise RuntimeError('Set JWT_SECRET_KEY (at least 32 characters)')
    now = datetime.now(timezone.utc)
    return jwt.encode({'sub': str(user_id), 'iat': now, 'exp': now + timedelta(minutes=60)}, secret, algorithm=ALGORITHM)

def decode_token(token: str) -> int:
    secret = os.getenv('JWT_SECRET_KEY')
    if not secret:
        raise ValueError('JWT secret missing')
    payload = jwt.decode(token, secret, algorithms=[ALGORITHM])
    return int(payload['sub'])
