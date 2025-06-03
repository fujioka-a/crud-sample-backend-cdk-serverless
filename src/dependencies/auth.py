# lambda_functions/user_info_handler.py
import json
import os
from urllib.request import urlopen

import boto3
import jwt
from jwt.exceptions import InvalidTokenError

REGION = os.environ.get("AWS_REGION", "ap-northeast-1")
USERPOOL_ID = os.environ.get("USER_POOL_ID")
APP_CLIENT_ID = os.environ.get("APP_CLIENT_ID")

# === JWKSのキャッシュ ===
cognito_client = boto3.client("cognito-idp", region_name=REGION)
jwks_url = f"https://cognito-idp.{REGION}.amazonaws.com/{USERPOOL_ID}/.well-known/jwks.json"

# 1. JWKS取得（Lambda起動時に1度だけ）
jwks = json.loads(urlopen(jwks_url).read())


# 2. JWTデコード用関数
def decode_token(token):
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


# 3. Lambdaハンドラ
def lambda_handler(event, context):
    auth_header = event["headers"].get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return {"statusCode": 401, "body": json.dumps({"message": "Missing or invalid Authorization header"})}

    token = auth_header.split(" ")[1]
    payload = decode_token(token)

    if not payload:
        return {"statusCode": 403, "body": json.dumps({"message": "Invalid token"})}

    return {"statusCode": 200, "body": json.dumps({"message": "Token verified", "username": payload["username"]})}
