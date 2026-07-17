"""
Per-user OAuth2 (authorization_code + PKCE) for the Buildly MCP server.

Flow:
  1. Client calls the `buildly_login` tool -> we mint a PKCE pair + state,
     remember which MCP session started it, and return an authorize URL.
  2. User opens the URL, logs in as themselves, approves.
  3. Buildly redirects to  <PUBLIC_BASE_URL>/oauth/callback?code=..&state=..
     which the HTTP server routes to `handle_callback` here.
  4. We exchange the code (confidential client: client_id+secret, server-side
     only) for an access token and bind it to the originating MCP session.
  5. All subsequent data tools read the token for THAT session.

Tokens are held in memory keyed by MCP session id -> no shared token file,
so each user is authenticated as themselves.

Config (env):
  LABS_BASE_URL          default https://labs.buildly.io
  LABS_OAUTH_CLIENT_ID       (required to enable OAuth login)
  LABS_OAUTH_CLIENT_SECRET   (required; server-side only)
  PUBLIC_BASE_URL        externally reachable base, e.g. http://bb-agent.home
                         (used to build redirect_uri). Falls back to
                         http://localhost:8765
"""
from __future__ import annotations

import base64
import hashlib
import os
import secrets
import time
from dataclasses import dataclass, field

import httpx


def _b64url(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


@dataclass
class _PendingAuth:
    session_id: str
    code_verifier: str
    created: float = field(default_factory=time.time)


@dataclass
class _Token:
    access_token: str
    refresh_token: str | None
    expires_at: float | None


class OAuthManager:
    """Holds pending auth requests and per-session tokens (in memory)."""

    STATE_TTL = 600  # seconds a login link stays valid

    def __init__(self) -> None:
        self.base = os.getenv("LABS_BASE_URL", "https://labs.buildly.io").rstrip("/")
        self.client_id = os.getenv("LABS_OAUTH_CLIENT_ID", "")
        self.client_secret = os.getenv("LABS_OAUTH_CLIENT_SECRET", "")
        self.public_base = os.getenv("PUBLIC_BASE_URL", "http://localhost:8765").rstrip("/")
        self._pending: dict[str, _PendingAuth] = {}       # state -> pending
        self._tokens: dict[str, _Token] = {}              # session_id -> token

    # -- config ---------------------------------------------------------------
    @property
    def enabled(self) -> bool:
        return bool(self.client_id and self.client_secret)

    @property
    def redirect_uri(self) -> str:
        return f"{self.public_base}/oauth/callback"

    # -- login start ----------------------------------------------------------
    def build_authorize_url(self, session_id: str) -> str:
        self._gc()
        verifier = _b64url(secrets.token_bytes(48))
        challenge = _b64url(hashlib.sha256(verifier.encode()).digest())
        state = secrets.token_urlsafe(24)
        self._pending[state] = _PendingAuth(session_id=session_id, code_verifier=verifier)

        from urllib.parse import urlencode
        q = urlencode({
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": "read write",
            "state": state,
            "code_challenge": challenge,
            "code_challenge_method": "S256",
        })
        return f"{self.base}/oauth/authorize?{q}"

    # -- callback -> token ----------------------------------------------------
    async def exchange_code(self, code: str, state: str) -> tuple[bool, str]:
        pending = self._pending.pop(state, None)
        if pending is None:
            return False, "Invalid or expired login state. Start over with buildly_login."

        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code_verifier": pending.code_verifier,
        }
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                r = await client.post(f"{self.base}/oauth/token", data=data)
                r.raise_for_status()
                tok = r.json()
        except httpx.HTTPStatusError as exc:
            return False, f"Token exchange failed: HTTP {exc.response.status_code} {exc.response.text[:200]}"
        except Exception as exc:  # noqa: BLE001
            return False, f"Token exchange error: {exc}"

        access = tok.get("access_token")
        if not access:
            return False, f"No access_token in response: {tok}"
        expires_in = tok.get("expires_in")
        self._tokens[pending.session_id] = _Token(
            access_token=access,
            refresh_token=tok.get("refresh_token"),
            expires_at=(time.time() + expires_in) if expires_in else None,
        )
        return True, pending.session_id

    # -- token access ---------------------------------------------------------
    def get_token(self, session_id: str | None) -> str | None:
        if not session_id:
            return None
        t = self._tokens.get(session_id)
        return t.access_token if t else None

    def logout(self, session_id: str | None) -> bool:
        return self._tokens.pop(session_id, None) is not None if session_id else False

    def _gc(self) -> None:
        now = time.time()
        expired = [s for s, p in self._pending.items() if now - p.created > self.STATE_TTL]
        for s in expired:
            self._pending.pop(s, None)


# module-level singleton shared by the tool layer and the HTTP callback route
manager = OAuthManager()
