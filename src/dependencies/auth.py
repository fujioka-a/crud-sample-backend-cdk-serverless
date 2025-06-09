# lambda_functions/user_info_handler.py
import json
import os
from urllib.request import urlopen

import jwt
from fastapi import HTTPException, Request, status
from jwt.exceptions import InvalidTokenError

REGION = os.environ.get("AWS_REGION", "ap-northeast-1")
USERPOOL_ID = os.environ.get("USER_POOL_ID")
APP_CLIENT_ID = os.environ.get("APP_CLIENT_ID")

jwks_url = f"https://cognito-idp.{REGION}.amazonaws.com/{USERPOOL_ID}/.well-known/jwks.json"
jwks = json.loads(urlopen(jwks_url).read())


class AuthService:
    def decode_token(self, token: str):
        try:
            headers = jwt.get_unverified_header(token)
            kid = headers["kid"]
            key = next(k for k in jwks["keys"] if k["kid"] == kid)
            public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(key))
            payload = jwt.decode(
                token,
                public_key,
                algorithms=["RS256"],
                audience=APP_CLIENT_ID,
                issuer=f"https://cognito-idp.{REGION}.amazonaws.com/{USERPOOL_ID}",
            )
            return payload
        except (InvalidTokenError, Exception) as e:
            print("JWT decode failed:", str(e))
            return None

    def get_current_user(self, request: Request) -> dict:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or invalid Authorization header"
            )
        token = auth_header.split(" ")[1]
        payload = self.decode_token(token)
        if not payload:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token")
        return payload
