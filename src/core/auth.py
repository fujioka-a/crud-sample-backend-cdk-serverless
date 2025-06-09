from abc import ABC, abstractmethod

import jwt
from fastapi import HTTPException, Request, status
from jwt import InvalidTokenError, PyJWKClient

from .config import get_settings

settings = get_settings()

# トークンデコーダーのインターフェース
class TokenDecoder(ABC):
    @abstractmethod
    def decode_token(self, token: str):
        pass

# Cognito用のトークンデコーダー
class CognitoTokenDecoder(TokenDecoder):
    def __init__(self):
        self._jwks_url = (
            f"https://cognito-idp.{settings.region}.amazonaws.com/{settings.user_pool_id}/.well-known/jwks.json"
        )
        self._jwks_client = PyJWKClient(self._jwks_url)

    def decode_token(self, token: str):
        try:
            signing_key = self._jwks_client.get_signing_key_from_jwt(token).key
            payload = jwt.decode(
                token,
                signing_key,
                audience=settings.app_client_id,
                issuer=f"https://cognito-idp.{settings.region}.amazonaws.com/{settings.user_pool_id}",
                algorithms=["RS256"],
            )
            return payload
        except InvalidTokenError as e:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e)) from e

# デフォルトのデコーダーをCognitoに設定
token_decoder: TokenDecoder = CognitoTokenDecoder()

def decode_token(token: str):
    return token_decoder.decode_token(token)

# FastAPIのDependsで直接使える認証関数
def get_current_user(request: Request) -> dict:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or invalid Authorization header"
        )
    token = auth_header.split(" ")[1]
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token")
    return payload
