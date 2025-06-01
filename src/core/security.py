import jwt
from fastapi import HTTPException, status
from jwt import InvalidTokenError, PyJWKClient

from .config import get_settings

settings = get_settings()
_JWKS_URL = f"https://cognito-idp.{settings.region}.amazonaws.com/{settings.user_pool_id}/.well-known/jwks.json"
_jwks_client = PyJWKClient(_JWKS_URL)


def decode_cognito_token(token: str):
    try:
        signing_key = _jwks_client.get_signing_key_from_jwt(token).key
        payload = jwt.decode(
            token,
            signing_key,
            audience=settings.app_client_id,
            issuer=f"https://cognito-idp.{settings.region}.amazonaws.com/{settings.user_pool_id}",
            algorithms=["RS256"],
        )
        return payload
    except InvalidTokenError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
