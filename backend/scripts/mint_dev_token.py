"""Mints a self-issued HS256 JWT for local/dev testing against JWT_SECRET.
There is no external identity provider for this project — see
backend/app/auth/dependencies.py.

Usage:
    python backend/scripts/mint_dev_token.py --user demo-educator --permitted "*"
    python backend/scripts/mint_dev_token.py --user demo-educator --permitted course:neural-networks-101
"""
import argparse
import os
import sys
import time
from pathlib import Path

import jwt
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / "backend" / ".env")


def mint(user_id: str, roles: list[str], permitted_sources: list[str], ttl_seconds: int) -> str:
    secret = os.environ.get("JWT_SECRET")
    if not secret:
        print("ERROR: JWT_SECRET is not set in backend/.env", file=sys.stderr)
        sys.exit(1)

    now = int(time.time())
    payload = {
        "sub": user_id,
        "roles": roles,
        "permitted_sources": permitted_sources,
        "iat": now,
        "exp": now + ttl_seconds,
    }
    return jwt.encode(payload, secret, algorithm="HS256")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--user", default="demo-educator")
    parser.add_argument("--roles", nargs="*", default=["educator"])
    parser.add_argument("--permitted", nargs="*", default=["*"], help="permission_scope strings, or '*' for all")
    parser.add_argument("--ttl", type=int, default=86400, help="seconds until expiry, default 24h")
    args = parser.parse_args()

    token = mint(args.user, args.roles, args.permitted, args.ttl)
    print(token)


if __name__ == "__main__":
    main()
