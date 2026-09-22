import logging
from hashlib import sha256
from hmac import compare_digest

from starlette.requests import Request

from nephthys.database.tables import APIKey


class InvalidAPIKeyError(Exception):
    """Raised when a request provided an API key that isn't valid."""


def extract_api_key(req: Request) -> str | None:
    """Extracts a Bearer API key from the request's Authorization header.

    Returns None when no Authorization header was sent (anonymous request), or
    an empty string when a header was sent but did not contain a valid Bearer
    token (i.e. an invalid API key was provided).
    """
    header = req.headers.get("authorization")
    if header is None:
        return None
    scheme, _, token = header.partition(" ")
    if scheme.lower() != "bearer":
        return ""
    return token.strip()


async def find_api_key(api_key: str) -> APIKey | None:
    """Looks up an API key by its SHA-256 hash, returning None if not found."""
    digest = sha256(api_key.encode("utf-8")).digest()
    key = await APIKey.objects().where(APIKey.api_key_hash == digest).first()
    if key is None:
        return None
    if not compare_digest(bytes(key.api_key_hash), digest):
        return None
    return key


async def authenticate_request(req: Request) -> bool:
    """Checks a request's optional API key.

    Returns whether the request may see sensitive fields (ticket
    descriptions). Requests without an API key are served anonymously, and
    requests with an invalid API key raise InvalidAPIKeyError.
    """
    api_key = extract_api_key(req)
    if api_key is None:
        return False
    if not api_key or await find_api_key(api_key) is None:
        logging.info(f"Rejected API request with invalid API key path={req.url.path}")
        raise InvalidAPIKeyError()
    return True
