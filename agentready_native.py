"""Opt-in personal reads through installed native CLIs; no capture or mutations."""
import datetime as dt
import json
import shutil
import subprocess
from agentready_lark import LarkError, MAX_OUTPUT


def run_native(command):
    if not shutil.which(command[0]):
        raise LarkError(command[0] + ' not installed; reuse a trusted native connector')
    try:
        proc = subprocess.run(command, capture_output=True, text=True, timeout=15, shell=False)
    except (subprocess.TimeoutExpired, OSError) as exc:
        raise LarkError(command[0] + ' unavailable or permission prompt pending') from exc
    if proc.returncode:
        raise LarkError(command[0] + ' read blocked; inspect local permission or native app')
    if len(proc.stdout.encode('utf-8')) > MAX_OUTPUT:
        raise LarkError('Response too large; narrow the native query')
    try:
        return json.loads(proc.stdout)
    except ValueError as exc:
        raise LarkError(command[0] + ' returned malformed JSON') from exc


def build_personal_brief(day, *, live=False, execute=run_native):
    date = dt.date.fromisoformat(day)
    if date.isoformat() != day:
        raise ValueError('Date must be YYYY-MM-DD')
    commands = {
        'calendar': ['ekctl', 'list', 'events', '--from', day, '--to', (date + dt.timedelta(days=1)).isoformat()],
        'reminders': ['remindctl', 'show', day, '--json'],
        'activity': ['dayflow', 'timeline', day, '--json'],
    }
    if not live:
        return {'date': day, 'mode': 'offline_plan', 'state': 'not_tested', 'commands': commands}
    report = {'date': day, 'mode': 'live', 'status': 'complete', 'sources': {},
              'privacy': 'Personal counts only; no work sources, raw screenshots, titles or uploads'}
    for source, command in commands.items():
        try:
            payload = execute(command)
            key = {'calendar': 'events', 'reminders': 'reminders', 'activity': 'cards'}[source]
            if isinstance(payload, dict) and (payload.get('error') or payload.get('status') == 'error'):
                raise LarkError(source + ' reported failure')
            rows = payload if source == 'reminders' and isinstance(payload, list) else payload.get(key) if isinstance(payload, dict) else None
            if not isinstance(rows, list) or not all(isinstance(r, dict) for r in rows):
                raise LarkError(source + ' unknown response schema')
            if source == 'reminders':
                rows = [r for r in rows if r.get('isCompleted') is not True and r.get('completed') is not True]
            report['sources'][source] = {'state': 'ok', 'observed_count': len(rows)}
        except (LarkError, OSError, ValueError) as exc:
            report['sources'][source] = {'state': 'blocked', 'reason': str(exc)}
            report['status'] = 'partial'
    return report
