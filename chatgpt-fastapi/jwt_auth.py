import jwt
import os

from fastapi import Request,HTTPException
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials


JWT_SECRET = os.getenv('JWT_SECRET')
JWT_ALGORITHMS = [os.getenv('JWT_ALGORITHMS')]




def decode_jwt(token: str):
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=JWT_ALGORITHMS)
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, req: Request):
        credentials: HTTPAuthorizationCredentials = await super().__call__(req)
        if credentials:
            if credentials.scheme != "Bearer":
                raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(status_code=403, detail="Invalid or expired token.")
            return credentials.credentials
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")


    def verify_jwt(self, jwtoken) -> bool:
        is_token_valid: bool = False
        try:
            payload = decode_jwt(jwtoken)
        except:
            payload = None
        if payload:
            is_token_valid = True
        return is_token_valid



