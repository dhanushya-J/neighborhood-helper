import sys
import json
import base64
from http.cookies import SimpleCookie
from app import app

client = app.test_client()

# Indicate ready
sys.stdout.write("READY\n")
sys.stdout.flush()

for line in sys.stdin:
    if not line.strip():
        continue
    try:
        req = json.loads(line)
        method = req.get('method', 'GET')
        path = req.get('path', '/')
        headers = req.get('headers', {})
        body = req.get('body', '').encode('utf-8') if req.get('body') else None

        # CRITICAL: Clear internal test_client cookies so each HTTP request is isolated
        if hasattr(client, '_cookies'):
            client._cookies.clear()

        # Load cookies from incoming request headers for the active domains
        cookie_header = headers.get('cookie') or headers.get('Cookie')
        if cookie_header:
            c = SimpleCookie()
            c.load(cookie_header)
            host_header = headers.get('host') or headers.get('Host') or '127.0.0.1'
            req_domain = host_header.split(':')[0]
            for morsel_k, morsel_v in c.items():
                for d in {req_domain, '127.0.0.1', 'localhost'}:
                    client.set_cookie(morsel_k, morsel_v.value, domain=d)

        resp = client.open(
            path=path,
            method=method,
            headers=headers,
            data=body,
            follow_redirects=False
        )

        # Build headers preserving multiple Set-Cookie values
        resp_headers = {}
        for k, v in resp.headers:
            k_lower = k.lower()
            if k_lower == 'set-cookie':
                if 'set-cookie' not in resp_headers:
                    resp_headers['set-cookie'] = []
                resp_headers['set-cookie'].append(v)
            else:
                resp_headers[k] = v

        raw_body = resp.get_data()
        b64_body = base64.b64encode(raw_body).decode('ascii')

        out = {
            'status': resp.status_code,
            'headers': resp_headers,
            'body_b64': b64_body
        }
        sys.stdout.write(json.dumps(out) + "\n")
        sys.stdout.flush()
    except Exception as e:
        err_out = {
            'status': 500,
            'headers': {'Content-Type': 'text/plain'},
            'body_b64': base64.b64encode(f"Bridge error: {e}".encode('utf-8')).decode('ascii')
        }
        sys.stdout.write(json.dumps(err_out) + "\n")
        sys.stdout.flush()
