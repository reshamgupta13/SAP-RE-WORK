#!/usr/bin/env python3
"""
Local proxy server for testing the ZREWORK_SKILL_SRV OData service from a browser form.

Run:
    python create_skill_server.py

Then open in your browser:
    http://localhost:8766/

Why this exists: a browser tab enforces CORS and SameSite cookie rules that
curl doesn't have. This script does the actual SAP calls itself, in plain
Python -- no browser sandbox involved, exactly like curl. The browser only
ever talks to this local server, which is always same-origin with itself.

IMPORTANT -- SkillId is a CHAR key (string), not numeric. Every entity-key
URL below wraps the value in single quotes, e.g. SkillSet('SK001'), unlike
a numeric key which would be SkillSet(101) with no quotes. Get this wrong
and every Update/Delete/Get-by-ID call will 404.

Requires: create_skill.html in the same folder as this script.
"""

import http.server
import json
import ssl
import base64
import os
import urllib.request
import urllib.error
import http.cookiejar

PORT = 8766
HTML_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "create_skill.html")

# Skip certificate verification, same as curl's -k flag.
SSL_CONTEXT = ssl.create_default_context()
SSL_CONTEXT.check_hostname = False
SSL_CONTEXT.verify_mode = ssl.CERT_NONE


def _new_opener():
    cookie_jar = http.cookiejar.CookieJar()
    return urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(cookie_jar),
        urllib.request.HTTPSHandler(context=SSL_CONTEXT),
    )


def _key_url(base_url, skill_id):
    """Builds the entity-key URL for a CHAR/string key -- quotes are required."""
    escaped = str(skill_id).replace("'", "''")  # OData escapes an embedded quote by doubling it
    return f"{base_url}('{escaped}')"


def _get_csrf_token(opener, base_url, auth, log):
    """Fetches a CSRF token, returns (token_or_None, updated_log, error_detail_or_None)."""
    log.append(f"Step 1: GET {base_url}?$format=json")
    req = urllib.request.Request(
        base_url + "?$format=json",
        headers={
            "X-CSRF-Token": "Fetch",
            "Accept": "application/json",
            "Authorization": f"Basic {auth}",
        },
    )
    try:
        with opener.open(req, timeout=20) as resp:
            token = resp.headers.get("x-csrf-token")
            status = resp.status
    except urllib.error.HTTPError as e:
        return None, log + [f"Token request failed: HTTP {e.code} {e.reason}"], e.read().decode(errors="replace")
    except Exception as e:
        return None, log + [f"Token request failed: {e}"], ""

    log.append(f"Response status: {status}")
    if not token:
        return None, log + ["No X-CSRF-Token header came back in the response."], ""
    log.append(f"Token received: {token}")
    return token, log, None


def sap_get_entity(base_url, username, password, payload):
    """Fetches a single skill by key. No CSRF token needed for GET requests."""
    skill_id = payload.get("SkillId")
    if not skill_id:
        return {"ok": False, "log": ["Payload is missing SkillId — can't build the entity key URL."], "detail": ""}

    opener = _new_opener()
    auth = base64.b64encode(f"{username}:{password}".encode()).decode()

    url = _key_url(base_url, skill_id) + "?$format=json"
    log = [f"GET {url}"]

    req = urllib.request.Request(
        url,
        headers={"Accept": "application/json", "Authorization": f"Basic {auth}"},
    )
    try:
        with opener.open(req, timeout=20) as resp:
            status = resp.status
            body = resp.read().decode(errors="replace")
            return {"ok": True, "log": log + [f"Response status: {status}"], "detail": body}
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")
        return {"ok": False, "log": log + [f"Get failed: HTTP {e.code} {e.reason}"], "detail": detail}
    except Exception as e:
        return {"ok": False, "log": log + [f"Get failed: {e}"], "detail": ""}


def sap_get_entityset(base_url, username, password, payload):
    """Fetches the full list of skills. No CSRF token needed for GET requests."""
    opener = _new_opener()
    auth = base64.b64encode(f"{username}:{password}".encode()).decode()

    url = f"{base_url}?$format=json"
    log = [f"GET {url}"]

    req = urllib.request.Request(
        url,
        headers={"Accept": "application/json", "Authorization": f"Basic {auth}"},
    )
    try:
        with opener.open(req, timeout=20) as resp:
            status = resp.status
            body = resp.read().decode(errors="replace")
            return {"ok": True, "log": log + [f"Response status: {status}"], "detail": body}
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")
        return {"ok": False, "log": log + [f"Get all failed: HTTP {e.code} {e.reason}"], "detail": detail}
    except Exception as e:
        return {"ok": False, "log": log + [f"Get all failed: {e}"], "detail": ""}


def sap_create_skill(base_url, username, password, payload):
    opener = _new_opener()
    auth = base64.b64encode(f"{username}:{password}".encode()).decode()
    log = []

    token, log, err_detail = _get_csrf_token(opener, base_url, auth, log)
    if not token:
        return {"ok": False, "log": log, "detail": err_detail or ""}

    body_bytes = json.dumps(payload).encode()
    log.append(f"Step 2: POST {base_url}")
    log.append(json.dumps(payload, indent=2))

    req2 = urllib.request.Request(
        base_url,
        data=body_bytes,
        method="POST",
        headers={
            "X-CSRF-Token": token,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Basic {auth}",
        },
    )
    try:
        with opener.open(req2, timeout=20) as resp2:
            status2 = resp2.status
            resp_body = resp2.read().decode(errors="replace")
            return {
                "ok": True,
                "log": log + [f"Response status: {status2}", "Skill created successfully."],
                "detail": resp_body,
            }
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")
        return {"ok": False, "log": log + [f"Create failed: HTTP {e.code} {e.reason}"], "detail": detail}
    except Exception as e:
        return {"ok": False, "log": log + [f"Create failed: {e}"], "detail": ""}


def sap_update_skill(base_url, username, password, payload):
    skill_id = payload.get("SkillId")
    if not skill_id:
        return {"ok": False, "log": ["Payload is missing SkillId — can't build the entity key URL."], "detail": ""}

    opener = _new_opener()
    auth = base64.b64encode(f"{username}:{password}".encode()).decode()
    log = []

    token, log, err_detail = _get_csrf_token(opener, base_url, auth, log)
    if not token:
        return {"ok": False, "log": log, "detail": err_detail or ""}

    url = _key_url(base_url, skill_id)
    body_bytes = json.dumps(payload).encode()
    log.append(f"Step 2: PUT {url}")
    log.append(json.dumps(payload, indent=2))

    req2 = urllib.request.Request(
        url,
        data=body_bytes,
        method="PUT",
        headers={
            "X-CSRF-Token": token,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Basic {auth}",
        },
    )
    try:
        with opener.open(req2, timeout=20) as resp2:
            status2 = resp2.status
            resp_body = resp2.read().decode(errors="replace") if status2 != 204 else ""
            return {
                "ok": True,
                "log": log + [f"Response status: {status2}", "Skill updated successfully."],
                "detail": resp_body,
            }
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")
        return {"ok": False, "log": log + [f"Update failed: HTTP {e.code} {e.reason}"], "detail": detail}
    except Exception as e:
        return {"ok": False, "log": log + [f"Update failed: {e}"], "detail": ""}


def sap_delete_skill(base_url, username, password, payload):
    skill_id = payload.get("SkillId")
    if not skill_id:
        return {"ok": False, "log": ["Payload is missing SkillId — can't build the entity key URL."], "detail": ""}

    opener = _new_opener()
    auth = base64.b64encode(f"{username}:{password}".encode()).decode()
    log = []

    token, log, err_detail = _get_csrf_token(opener, base_url, auth, log)
    if not token:
        return {"ok": False, "log": log, "detail": err_detail or ""}

    url = _key_url(base_url, skill_id)
    log.append(f"Step 2: DELETE {url}")

    req2 = urllib.request.Request(
        url,
        method="DELETE",
        headers={
            "X-CSRF-Token": token,
            "Accept": "application/json",
            "Authorization": f"Basic {auth}",
        },
    )
    try:
        with opener.open(req2, timeout=20) as resp2:
            status2 = resp2.status
            return {
                "ok": True,
                "log": log + [f"Response status: {status2}", f"Skill {skill_id} deleted successfully."],
                "detail": "",
            }
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")
        return {"ok": False, "log": log + [f"Delete failed: HTTP {e.code} {e.reason}"], "detail": detail}
    except Exception as e:
        return {"ok": False, "log": log + [f"Delete failed: {e}"], "detail": ""}


class Handler(http.server.BaseHTTPRequestHandler):
    def _send_json(self, obj, status=200):
        body = json.dumps(obj).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path in ("/", "/create_skill.html"):
            try:
                with open(HTML_FILE, "rb") as f:
                    content = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
            except FileNotFoundError:
                self._send_json({"error": f"create_skill.html not found next to this script ({HTML_FILE})"}, 404)
        else:
            self._send_json({"error": "not found"}, 404)

    def do_POST(self):
        routes = {
            "/api/create-skill": sap_create_skill,
            "/api/update-skill": sap_update_skill,
            "/api/delete-skill": sap_delete_skill,
            "/api/get-skill": sap_get_entity,
            "/api/get-skills": sap_get_entityset,
        }
        handler_fn = routes.get(self.path)

        if handler_fn:
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length)
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                self._send_json({"ok": False, "log": ["Invalid JSON received from the browser."], "detail": ""}, 400)
                return

            result = handler_fn(
                data["url"], data["username"], data["password"], data["payload"]
            )
            self._send_json(result)
        else:
            self._send_json({"error": "not found"}, 404)

    def log_message(self, fmt, *args):
        print("[proxy]", *args)


if __name__ == "__main__":
    server = http.server.ThreadingHTTPServer(("localhost", PORT), Handler)
    print(f"Serving at http://localhost:{PORT}   (Ctrl+C to stop)")
    print(f"Reading page from: {HTML_FILE}")
    server.serve_forever()
