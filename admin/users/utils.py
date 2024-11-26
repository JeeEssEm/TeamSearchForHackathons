from datetime import datetime, timedelta, timezone

from django.conf import settings

from jwt import decode, encode


def generate_jwt_token(user_id: int) -> str:
    token = encode(
        {
            'user_id': user_id,
            'exp': (datetime.now(timezone.utc) +
                    timedelta(days=settings.JWT_EXPIRATION_DELTA_DAYS))
        }, algorithm=settings.JWT_ALGORITHM, key=settings.SECRET_KEY
    )
    return token


def decode_jwt_token(token: str) -> dict:
    return decode(token, key=settings.SECRET_KEY,
                  algorithms=[settings.JWT_ALGORITHM])
