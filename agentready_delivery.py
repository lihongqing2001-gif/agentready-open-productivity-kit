"""Explicit, idempotent delivery to the verified current user's Feishu DM only."""
import hashlib
import json
import os
from pathlib import Path

from agentready_lark import LarkError, run_lark


def publish_report(filename, profile, receipt, *, apply=False, execute=run_lark):
    path = Path(filename).expanduser().resolve()
    if not path.is_file() or path.stat().st_size > 24000:
        raise LarkError('Report missing or larger than the single-message limit (24000 bytes)')
    content = path.read_text('utf-8')
    if not content.strip():
        raise LarkError('Empty report cannot be sent')
    target = Path(receipt).expanduser()
    if target.resolve() == path:
        raise LarkError('Receipt must not replace the report')
    digest = hashlib.sha256(content.encode()).hexdigest()
    if not apply:
        return {'state': 'preview', 'sha256': digest, 'bytes': len(content.encode()),
                'destination': 'verified current user only', 'sent': False}
    auth = execute(['lark-cli', '--profile', profile, 'auth', 'status', '--json', '--verify'])
    user = auth.get('identities', {}).get('user', {})
    if auth.get('verified') is not True or user.get('status') != 'ready' or user.get('tokenStatus') != 'valid':
        raise LarkError('Verified user authentication required')
    identity = user.get('openId')
    if not isinstance(identity, str) or not identity.startswith('ou_'):
        raise LarkError('Current user identity unavailable')
    key = hashlib.sha256((profile + identity + digest).encode()).hexdigest()[:40]
    if target.exists():
        saved = json.loads(target.read_text('utf-8'))
        if saved.get('key') != key:
            raise LarkError('Receipt belongs to another report/account; preserve it and use a new receipt')
        if saved.get('state') == 'sent':
            return saved
        raise LarkError('Delivery previously attempted; reconcile Feishu with stored key before retrying')
    target.parent.mkdir(parents=True, exist_ok=True)
    with os.fdopen(os.open(str(target), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), 'w') as handle:
        json.dump({'state': 'attempting', 'key': key, 'sha256': digest}, handle)
    # Plain text preserves Markdown without CLI image expansion or media uploads.
    result = execute(['lark-cli', '--profile', profile, 'im', '+messages-send', '--user-id', identity,
                      '--text', '@' + str(path), '--idempotency-key', key, '--as', 'user', '--format', 'json'])
    data = result.get('data', result)
    message_id = data.get('message_id') if isinstance(data, dict) else None
    if not isinstance(message_id, str) or not message_id:
        raise LarkError('No message_id receipt; reconcile instead of blindly resending')
    saved = {'state': 'sent', 'key': key, 'sha256': digest, 'message_id': message_id}
    target.write_text(json.dumps(saved, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return saved
