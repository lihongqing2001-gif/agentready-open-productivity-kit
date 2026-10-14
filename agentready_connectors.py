"""Opt-in, fixed-route connector probes. Never fetch user records or print tokens.

No external dependency. Network access occurs ONLY on explicit `verify --live`.
The supported connector routes are intentionally curated and non-extensible by
untrusted JSON configuration: adding a connector requires code review/tests.
"""
from __future__ import annotations

import ipaddress
import json
import os
import urllib.error
import urllib.parse
import urllib.request

PROBES = {
    'homebox': {'status': '/api/v1/status', 'identity': '/api/v1/users/self'},
    'nocobase': {'status': '/api/app:getInfo', 'mcp': '/api/mcp'},
}
MAX_BODY = 65536


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def validate_origin(raw, allow_remote=False):
    """Accept bare http(s) origin only; avoid SSRF by default.

    Remote hosts require explicit opt-in AND HTTPS. Credential-bearing URLs,
    embedded paths and query strings are never accepted.
    """
    parsed = urllib.parse.urlsplit(raw)
    if (parsed.scheme not in ('http', 'https') or not parsed.hostname or
            parsed.username or parsed.password or parsed.path not in ('', '/') or
            parsed.query or parsed.fragment):
        raise ValueError('Provide a bare http(s) service origin without path, userinfo or query')
    try:
        port = parsed.port
    except ValueError:
        raise ValueError('Invalid port')
    host = parsed.hostname
    try:
        local = ipaddress.ip_address(host).is_loopback
    except ValueError:
        local = host.lower() == 'localhost'
    if not local and (not allow_remote or parsed.scheme != 'https'):
        raise ValueError('Remote probes require an HTTPS origin and --allow-remote')
    if port is not None and not 1 <= port <= 65535:
        raise ValueError('Invalid port')
    return raw.rstrip('/')


def _send(opener, url, *, token=None, method='GET', body=None):
    headers = {'Accept': 'application/json'}
    if token:
        # HomeBox logins sometimes return the prefix in their token string.
        value = token if token.lower().startswith('bearer ') else 'Bearer ' + token
        headers['Authorization'] = value
    if body is not None:
        headers['Content-Type'] = 'application/json'
        headers['Accept'] = 'application/json, text/event-stream'
    request = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with opener.open(request, timeout=5) as response:
            if response.status != 200:
                return {'ok': False, 'http': response.status}
            content = response.read(MAX_BODY + 1)
            if len(content) > MAX_BODY:
                return {'ok': False, 'error': 'response_too_large'}
            return {'ok': True, 'http': response.status, 'body': content}
    except urllib.error.HTTPError as error:
        # Don't read body: providers may echo private or secret data in errors.
        return {'ok': False, 'http': error.code}
    except (urllib.error.URLError, TimeoutError, ConnectionError, OSError):
        return {'ok': False, 'error': 'network_or_tls_error'}


def _is_mcp_response(data):
    """Check a JSON-RPC initialize response in JSON or SSE encoding."""
    raw = data.decode('utf-8', errors='replace')
    possible = [raw]
    possible.extend(line[5:].strip() for line in raw.splitlines() if line.startswith('data:'))
    for text in possible:
        try:
            payload = json.loads(text)
        except ValueError:
            continue
        if isinstance(payload, dict) and isinstance(payload.get('result'), dict):
            result = payload['result']
            if 'serverInfo' in result and 'protocolVersion' in result:
                return True
    return False


def verify(service, url, *, live=False, allow_remote=False, token_env=None, mcp=False):
    if service not in PROBES:
        raise ValueError('Unsupported service. Choices: ' + ', '.join(sorted(PROBES)))
    if mcp and service != 'nocobase':
        raise ValueError('--mcp is supported only for nocobase')
    if token_env and (not token_env.isidentifier() or not token_env.isascii()):
        raise ValueError('Token environment variable name must be an identifier')
    origin = validate_origin(url, allow_remote=allow_remote)
    result = {'service': service, 'network_executed': False,
              'reachability': 'not_tested', 'auth': 'not_tested',
              'mcp_handshake': 'not_tested', 'note': 'No business record was read or changed'}
    if not live:
        return result
    result['network_executed'] = True
    token = os.environ.get(token_env, '') if token_env else ''
    if token_env and not token:
        result['auth'] = 'missing_local_env'
        return result
    opener = urllib.request.build_opener(NoRedirect)
    status = _send(opener, origin + PROBES[service]['status'])
    result['reachability'] = 'passed' if status['ok'] else 'failed'
    if not status['ok']:
        result['http_status'] = status.get('http')
        result['error'] = status.get('error', 'non_200')
        return result
    if service == 'homebox' and token:
        identity = _send(opener, origin + PROBES[service]['identity'], token=token)
        result['auth'] = 'passed' if identity['ok'] else 'failed'
        if not identity['ok']:
            result['auth_http_status'] = identity.get('http')
    if service == 'nocobase' and mcp:
        payload = json.dumps({
            'jsonrpc': '2.0', 'id': 1, 'method': 'initialize',
            'params': {'protocolVersion': '2025-03-26', 'capabilities': {},
                       'clientInfo': {'name': 'agentready-probe', 'version': '0.2.0'}}
        }).encode('utf-8')
        init = _send(opener, origin + PROBES[service]['mcp'], token=token,
                     method='POST', body=payload)
        result['mcp_handshake'] = ('passed' if init['ok'] and _is_mcp_response(init['body'])
                                   else 'failed')
        # A successful initialize may be public; it is NOT proof of RBAC.
        if not init['ok']:
            result['mcp_http_status'] = init.get('http')
    return result
