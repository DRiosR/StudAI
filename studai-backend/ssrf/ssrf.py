# ssrf.py
"""
Single-file FastAPI app that contains:
 - /vulnerable-fetch  (INTENTIONALLY VULNERABLE — for isolated local lab only)
 - /secure-fetch      (Hardened implementation with whitelist + DNS/IP checks)

Security features in /secure-fetch:
 - exact-hostname whitelist
 - DNS resolution -> IP checks (disallow private/link-local/loopback)
 - validated redirect-following (inspect Location, validate, then follow)
 - timeouts and response-size limits

Run (local dev):
    pip install fastapi uvicorn httpx
    python -m uvicorn ssrf:app --host 127.0.0.1 --port 8000 --reload
"""

from fastapi import FastAPI, HTTPException
from urllib.parse import urlparse
from pydantic import BaseModel, AnyHttpUrl
import httpx
from urllib.parse import urlparse, urljoin
import socket
import ipaddress
import os
import asyncio
from fastapi.middleware.cors import CORSMiddleware
from typing import List

app = FastAPI(title="SSRF Lab: vulnerable + secure endpoints")
print("SSRF Lab: vulnerable + secure endpoints")

# -----------------------------
# CORS (adjust if needed for frontend)
# -----------------------------
ALLOWED_ORIGINS = ["http://localhost:3000", "http://127.0.0.1:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=False,
)

# -----------------------------
# Config (adjust via env vars)
# -----------------------------
WHITELIST_HOSTNAMES = os.environ.get(
    "SSRF_WHITELIST", "https://grassy.codes,https://vervi.app"
).split(",")
WHITELIST_HOSTNAMES = [h.strip() for h in WHITELIST_HOSTNAMES if h.strip()]

MAX_RESPONSE_BYTES = int(os.environ.get("SSRF_MAX_BYTES", "200000"))  # bytes
REQUEST_TIMEOUT = float(os.environ.get("SSRF_TIMEOUT", "5"))  # seconds
MAX_REDIRECTS = int(os.environ.get("SSRF_MAX_REDIRECTS", "5"))  # hops


ALLOW_SUBDOMAINS = bool(os.environ.get("SSRF_ALLOW_SUBDOMAINS", "").lower() in ("1", "true", "yes"))

def normalize_whitelist(raw: str):
    """
    Accept comma separated values like:
      'example.com,https://grassy.codes,vervi.app:8080'
    and return normalized hostnames: ['example.com','grassy.codes','vervi.app']
    """
    from urllib.parse import urlparse
    out = []
    for part in raw.split(","):
        p = part.strip()
        if not p:
            continue
        # If it looks like a URL, use urlparse to extract hostname
        if p.startswith("http://") or p.startswith("https://"):
            hostname = urlparse(p).hostname
            if hostname:
                out.append(hostname)
            else:
                # fallback: strip scheme and path
                out.append(p.replace("http://", "").replace("https://", "").split("/")[0].split(":")[0])
        else:
            # strip optional port / path
            out.append(p.split("/")[0].split(":")[0])
    # dedupe, preserve order
    return list(dict.fromkeys(out))

# Replace your existing WHITELIST_HOSTNAMES initialization with:
_raw = os.environ.get(
    "SSRF_WHITELIST",
    "grassy.codes,vervi.app,http://fiad.ens.uabc.mx/,https://www.facebook.com/"
)
WHITELIST_HOSTNAMES = normalize_whitelist(_raw)

# WHITELIST_RAW = os.environ.get(
#     "SSRF_WHITELIST",
#     "internal-service,example.com,https://grassy.codes,https://vervi.app"
# ).split(",")
# WHITELIST_HOSTNAMES = _normalize_whitelist(WHITELIST_RAW)

# -----------------------------
# Request model
# -----------------------------
class FetchRequest(BaseModel):
    url: AnyHttpUrl

# -----------------------------
# Utilities
# -----------------------------
def is_private_ip(ip_str: str) -> bool:
    """Conservative: treat anything not global as private/unsafe."""
    try:
        ip = ipaddress.ip_address(ip_str)
    except ValueError:
        # invalid IP => consider unsafe
        return True
    # ip.is_global is True for public global unicast addresses
    return not ip.is_global


def hostname_allowed(candidate: str) -> bool:
    """
    Return True if candidate hostname is allowed by whitelist.
    If ALLOW_SUBDOMAINS is True, allow subdomains of whitelisted hosts.
    """
    if not WHITELIST_HOSTNAMES:
        return False
    # exact match fast path
    if candidate in WHITELIST_HOSTNAMES:
        print(f"[debug] hostname_allowed: exact match for '{candidate}' in {WHITELIST_HOSTNAMES}")
        return True
    # special-case: allow 'www.' subdomain if the apex/root is whitelisted
    if candidate.startswith("www.") and candidate[4:] in WHITELIST_HOSTNAMES:
        print(f"[debug] hostname_allowed: www-subdomain match for '{candidate}' maps to root '{candidate[4:]}'")
        return True
    if ALLOW_SUBDOMAINS:
        for allowed in WHITELIST_HOSTNAMES:
            if candidate.endswith(f".{allowed}"):
                print(f"[debug] hostname_allowed: subdomain match '{candidate}' endswith '.{allowed}'")
                return True
    print(f"[debug] hostname_allowed: '{candidate}' not allowed. WHITELIST_HOSTNAMES={WHITELIST_HOSTNAMES}, ALLOW_SUBDOMAINS={ALLOW_SUBDOMAINS}")
    return False

async def resolve_hostname_to_ips(hostname: str) -> List[str]:
    """Resolve hostname to unique IP strings (IPv4 + IPv6 if present)."""
    loop = asyncio.get_event_loop()
    def _sync_getaddrinfo():
        try:
            infos = socket.getaddrinfo(hostname, None, proto=socket.IPPROTO_TCP)
            ips = []
            for fam, _, _, _, sockaddr in infos:
                if fam == socket.AF_INET:
                    ips.append(sockaddr[0])
                elif fam == socket.AF_INET6:
                    ips.append(sockaddr[0])
            # preserve order but dedupe
            return list(dict.fromkeys(ips))
        except socket.gaierror:
            return []
    ips = await loop.run_in_executor(None, _sync_getaddrinfo)
    print(f"[debug] resolve_hostname_to_ips: hostname={hostname} -> ips={ips}")
    return ips

async def validate_and_resolve_hostname(hostname: str):
    """
    Validate hostname against whitelist and ensure all resolved IPs are public/global.
    Raises HTTPException on failure.
    """
    print(f"[debug] validate_and_resolve_hostname: start hostname={hostname}")
    if WHITELIST_HOSTNAMES:
        # exact-match whitelist
        if not hostname_allowed(hostname):
            print(f"[debug] validate_and_resolve_hostname: blocked by whitelist: {hostname}")
            raise HTTPException(status_code=403, detail=f"hostname not allowed by whitelist: {hostname}")
    ips = await resolve_hostname_to_ips(hostname)
    if not ips:
        print(f"[debug] validate_and_resolve_hostname: no DNS resolution for {hostname}")
        raise HTTPException(status_code=400, detail="hostname could not be resolved")
    for ip in ips:
        private = is_private_ip(ip)
        print(f"[debug] validate_and_resolve_hostname: ip={ip} is_private={private}")
        if private:
            print(f"[debug] validate_and_resolve_hostname: blocked private/non-global ip {ip} for {hostname}")
            raise HTTPException(status_code=403, detail=f"resolved to unsafe IP: {ip}")
    print(f"[debug] validate_and_resolve_hostname: success hostname={hostname} ips={ips}")
    return ips

# -----------------------------
# Vulnerable endpoint (lab only)
# -----------------------------
@app.post("/vulnerable-fetch")
async def vulnerable_fetch(payload: FetchRequest):
    """
    INTENTIONALLY VULNERABLE: fetches any user-supplied URL and returns a small slice of the body.
    This demonstrates SSRF. Do NOT enable in production or on networks reachable by attackers.
    """
    url = str(payload.url)
    try:
        # follow redirects here (vulnerable), short timeout, limited response returned
        async with httpx.AsyncClient(follow_redirects=True, timeout=REQUEST_TIMEOUT) as client:
            r = await client.get(url, timeout=REQUEST_TIMEOUT)
            content = r.text or ""
            return {"status_code": r.status_code, "content": content[:10000]}
    except httpx.RequestError as exc:
        raise HTTPException(status_code=400, detail=f"request error: {exc}")

# -----------------------------
# Secure endpoint (hardened)
# -----------------------------
@app.post("/secure-fetch")
async def secure_fetch(payload: FetchRequest):
    """
    Secure fetch:
      - only http/https
      - exact-hostname whitelist (configurable)
      - resolve hostname -> block private IPs
      - validate redirect targets before following (up to MAX_REDIRECTS)
      - timeouts & max response size
    """
    url = str(payload.url)
    parsed = urlparse(url)
    print(f"url: {url}")
    print(f"parsed: {parsed}")
    print(f"WHITELIST_HOSTNAMES: {WHITELIST_HOSTNAMES}")

    # Scheme check
    if parsed.scheme not in ("http", "https"):
        raise HTTPException(status_code=400, detail="only http(s) URLs allowed")

    hostname = parsed.hostname
    if not hostname:
        raise HTTPException(status_code=400, detail="invalid hostname")

    # 1) Validate hostname (exact whitelist) + resolve initial hostname IPs
    initial_ips = await validate_and_resolve_hostname(hostname)

    print(f"hostname: {hostname}")
    print(f"[debug] initial target: hostname={hostname} ips={initial_ips} path={parsed.path!r} query={parsed.query!r}")

    # 2) Perform requests manually, validating redirects before following
    try:
        async with httpx.AsyncClient(follow_redirects=False, timeout=REQUEST_TIMEOUT) as client:
            current_url = url
            redirect_count = 0

            while True:
                print(f"[debug] request: GET {current_url} (redirect_count={redirect_count})")
                r = await client.get(current_url, timeout=REQUEST_TIMEOUT)
                print(f"[debug] response: status={r.status_code} url={current_url}")

                # If redirect, validate Location, resolve + IP check, then follow (manually)
                if 300 <= r.status_code < 400:
                    if redirect_count >= MAX_REDIRECTS:
                        raise HTTPException(status_code=400, detail="too many redirects")

                    location = r.headers.get("location")
                    if not location:
                        raise HTTPException(status_code=400, detail=f"redirects are not allowed (status {r.status_code})")

                    # Resolve relative Location to absolute URL (urljoin handles relative paths)
                    next_url = urljoin(current_url, location)
                    print(f"[debug] redirect: location={location!r} -> next_url={next_url}")
                    parsed_next = urlparse(next_url)
                    next_hostname = parsed_next.hostname
                    if not next_hostname:
                        raise HTTPException(status_code=400, detail="redirect location invalid")

                    # Validate redirect target hostname + resolved IP(s)
                    next_ips = await validate_and_resolve_hostname(next_hostname)
                    print(f"[debug] redirect target allowed: hostname={next_hostname} ips={next_ips} path={parsed_next.path!r} query={parsed_next.query!r}")

                    # Safe to follow to next_url
                    current_url = next_url
                    redirect_count += 1
                    continue

                # Non-redirect response — return truncated body
                body = r.text or ""
                if len(body.encode('utf-8')) > MAX_RESPONSE_BYTES:
                    body = body.encode('utf-8')[:MAX_RESPONSE_BYTES].decode('utf-8', errors='ignore')

                print(f"[debug] final response: status={r.status_code}, bytes={len((r.text or '').encode('utf-8'))}")
                return {"status_code": r.status_code, "content": body}
    except httpx.RequestError as exc:
        print(f"[debug] request error: {exc}")
        raise HTTPException(status_code=400, detail=f"request error: {exc}")

# -----------------------------
# Health / config endpoints
# -----------------------------
@app.get("/config")
async def config():
    return {
        "whitelist": WHITELIST_HOSTNAMES,
        "max_bytes": MAX_RESPONSE_BYTES,
        "timeout_seconds": REQUEST_TIMEOUT,
        "max_redirects": MAX_REDIRECTS,
    }

@app.get("/")
async def root():
    return {"message": "SSRF lab app: /vulnerable-fetch (lab) and /secure-fetch (hardened)"}

# -----------------------------
# Run with "python -m uvicorn ssrf:app ..." or call this file directly
# -----------------------------
if __name__ == '__main__':
    import uvicorn
    # Use uvicorn.run(app, ...) instead of module string to avoid naming issues
    uvicorn.run("ssrf:app", host="127.0.0.1", port=8000, reload=True)


