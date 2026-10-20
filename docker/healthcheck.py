"""Healthcheck Docker : interroge /healthz/ comme le ferait Traefik (Host + HTTPS)."""
import os
import sys
import urllib.request

host = os.environ.get('ALLOWED_HOSTS', 'localhost').split(',')[0].strip()
req = urllib.request.Request(
    'http://127.0.0.1:8000/healthz/',
    headers={'Host': host, 'X-Forwarded-Proto': 'https'},
)
try:
    with urllib.request.urlopen(req, timeout=4) as res:
        sys.exit(0 if res.status == 200 else 1)
except Exception:
    sys.exit(1)
