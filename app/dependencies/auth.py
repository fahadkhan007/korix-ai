from fastapi import Security
import jwt
from pathlib import Path
from fastapi import HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials



_pem_path = Path(__file__).resolve().parents[2] / "public.pem"

try:
    PUBLIC_KEY = _pem_path.read_text()
except FileNotFoundError:
    PUBLIC_KEY=None
    print(f"PUBLIC_KEY file not found at {_pem_path}")

_security = HTTPBearer()

async def verify_token(cred:HTTPAuthorizationCredentials=Security(_security))-> dict:
    if not PUBLIC_KEY:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="server misconfiguration: public key is missing")
    try:
        token = cred.credentials
        payload=jwt.decode(token, PUBLIC_KEY, algorithms=["RS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="token has expired")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"invalid token: {e}")
    

