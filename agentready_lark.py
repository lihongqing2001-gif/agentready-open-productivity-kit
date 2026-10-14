"""AgentReady's optional lark-cli-first, Hermes-independent Feishu daily brief.

Live reads require explicit --live and a pre-authenticated *user* lark-cli profile.
Does not call OAuth login, edit records, schedule jobs, or upload content.
No messages are retrieved unless the caller supplies an explicit search query.
"""
from __future__ import annotations

import datetime as dt
import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

MAX_OUTPUT = 1024 * 1024
MAX_RECORDS = 500


class LarkError(Exception):
    pass


COMMANDS = {
    'tasks': ['task', '+get-my-tasks', '--complete=false', '--as', 'user'],
    'calendar': ['calendar', '+agenda', '--as', 'user'],
}


def commands_for_day(day: str, message_query: str | None = None, lark_profile: str | None = None) -> dict[str, list[str]]:
    """Build an allowlisted set of *read-only* lark-cli commands, no shell."""
    try:
        date = dt.date.fromisoformat(day)
    except ValueError as error:
        raise LarkError('Date must be YYYY-MM-DD') from error
    if date.isoformat() != day:
        raise LarkError('Date must be YYYY-MM-DD')
    result = {key: ['lark-cli', *args[:-2], '--format', 'json', *args[-2:]] for key, args in COMMANDS.items()}
    if lark_profile is not None:
        if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,63}', lark_profile):
            raise LarkError('Invalid lark-cli profile name')
        result = {key: [cmd[0], '--profile', lark_profile, *cmd[1:]] for key, cmd in result.items()}
    tomorrow = date + dt.timedelta(days=1)
    start = dt.datetime.combine(date, dt.time.min).astimezone().isoformat(timespec='seconds')
    end = dt.datetime.combine(tomorrow, dt.time.min).astimezone().isoformat(timespec='seconds')
    result['calendar'][-2:-2] = ['--start', start, '--end', end]
    result['tasks'][-2:-2] = ['--page-limit', '1']
    if message_query is not None:
        query = message_query.strip()
        if not 1 <= len(query) <= 100 or '\n' in query or '\r' in query or query.startswith('-'):
            raise LarkError('Message query must be nonempty, single-line, <=100 chars, not a flag')
        # Search only the chosen day in caller's existing CLI timezone.
        tomorrow = date + dt.timedelta(days=1)
        start = dt.datetime.combine(date, dt.time.min).astimezone().isoformat(timespec='seconds')
        end = dt.datetime.combine(tomorrow, dt.time.min).astimezone().isoformat(timespec='seconds')
        result['messages'] = [
            'lark-cli', *(['--profile', lark_profile] if lark_profile else []), 'im', '+messages-search', '--query', query,
            '--start', start, '--end', end, '--format', 'json', '--as', 'user'
        ]
    return result


def _read_json(text: str) -> Any:
    """Fail closed rather than parsing incidental log lines as business records."""
    try:
        return json.loads(text)
    except json.JSONDecodeError as err:
        raise LarkError('CLI did not return parseable JSON; check installed lark-cli output mode') from err


def _assert_success(payload: Any, source: str):
    if isinstance(payload, dict):
        if payload.get('ok') is False or payload.get('success') is False:
            raise LarkError(f'{source}: API reported failure (often scope or resource ACL)')
        if isinstance(payload.get('code'), int) and payload['code'] != 0:
            raise LarkError(f'{source}: API code {payload["code"]} (scope/ACL/data issue)')
        if 'error' in payload and payload['error']:
            raise LarkError(f'{source}: API returned error (details suppressed)')


def _extract(payload: Any, source: str) -> tuple[list[dict], bool, str]:
    """Known Feishu-style wrappers, strict unknown-shape behavior.

    No arbitrary recursive tree traversal: prevents accidentally counting a person's
    nested data or confusing a calendar metadata payload for event records.
    """
    _assert_success(payload, source)
    if isinstance(payload, list):
        if all(isinstance(x, dict) for x in payload):
            return payload[:MAX_RECORDS], len(payload) > MAX_RECORDS, 'list'
        raise LarkError(f'{source}: unexpected list members')
    if not isinstance(payload, dict):
        raise LarkError(f'{source}: unknown response schema')
    wrappers = [payload]
    for key in ('data', 'result'):
        child = payload.get(key)
        if isinstance(child, dict):
            wrappers.append(child)
    # Real-world CLI shapes vary between versions; never count an object as one task.
    search_keys = {'tasks': ['tasks', 'items', 'task_items', 'list'],
                   'calendar': ['events', 'items', 'event_list', 'list'],
                   'messages': ['messages', 'items', 'list']}
    more = False
    for wrapper in wrappers:
        _assert_success(wrapper, source)
        for flag in ('has_more', 'hasMore'):
            if flag in wrapper:
                if not isinstance(wrapper[flag], bool):
                    raise LarkError(f'{source}: malformed pagination flag')
                more = more or wrapper[flag]
    for wrapper in wrappers:
        for key in search_keys[source]:
            rows = wrapper.get(key)
            if isinstance(rows, list):
                if not all(isinstance(x, dict) for x in rows):
                    raise LarkError(f'{source}: malformed records')
                has_more = more
                if len(rows) > MAX_RECORDS:
                    has_more = True
                return rows[:MAX_RECORDS], has_more, key
    raise LarkError(f'{source}: unknown response schema; no totals inferred')


def _safe_title(row: dict, source: str) -> str:
    options = {
        'tasks': ('summary', 'title', 'name', 'task_title'),
        'calendar': ('summary', 'title', 'subject', 'name'),
        'messages': ('message_id',),
    }[source]
    for key in options:
        value = row.get(key)
        if isinstance(value, str) and value.strip():
            return re.sub(r'[\r\n\t]+', ' ', value.strip())[:100]
    return '(no title)'


def _safe_link(row: dict) -> str | None:
    for key in ('message_app_link', 'app_link', 'applink', 'url'):
        value = row.get(key)
        if isinstance(value, str) and value.startswith('https://') and len(value) < 2048:
            return value
    return None


def load_fixture(path: Path, source: str) -> Any:
    path = path.resolve()
    filename = path / (source + '.json')
    if not filename.is_file() or filename.stat().st_size > MAX_OUTPUT:
        raise LarkError(f'Missing or oversized fixture for {source}')
    return _read_json(filename.read_text('utf-8'))


def run_lark(command: list[str], *, runner=subprocess.run) -> Any:
    if not shutil.which('lark-cli'):
        raise LarkError('lark-cli not in PATH. Install and authorize the existing official/organization CLI first')
    # Untrusted command output stays memory-only and is never written to reports.
    try:
        proc = runner(command, shell=False, capture_output=True, text=True,
                      timeout=25, check=False)
    except (subprocess.TimeoutExpired, OSError) as error:
        raise LarkError('lark-cli invocation failed or timed out') from error
    if proc.returncode != 0:
        try:
            error = _read_json(proc.stderr).get('error', {})
            scopes = error.get('missing_scopes', [])
            if isinstance(scopes, list) and scopes and all(isinstance(x, str) and re.fullmatch(r'[A-Za-z0-9_.:]+', x) for x in scopes):
                raise LarkError('Missing scope(s): ' + ', '.join(scopes))
        except (AttributeError, TypeError):
            pass
        except LarkError as exc:
            if str(exc).startswith('Missing scope(s):'): raise
        raise LarkError('lark-cli returned nonzero; check login, scopes or CLI arguments locally')
    if len(proc.stdout.encode('utf-8')) > MAX_OUTPUT:
        raise LarkError('lark-cli output exceeds safety cap; narrow query/time range')
    return _read_json(proc.stdout)


def build_brief(day: str, *, live=False, fixture_dir: str | None = None,
                message_query: str | None = None, details=False, lark_profile=None,
                execute=run_lark) -> dict:
    commands = commands_for_day(day, message_query, lark_profile)
    if live and day != dt.datetime.now().date().isoformat():
        raise LarkError('Live --date currently supports only system-local today (calendar +agenda date flags not verified)')
    if live and fixture_dir:
        raise LarkError('Choose --live OR --fixture-dir, never both')
    if not live and not fixture_dir:
        return {'date': day, 'mode': 'offline_plan', 'state': 'not_tested',
                'commands': commands,
                'note': 'No commands executed. Live calls require --live; data access may need OAuth.'}
    report = {'date': day, 'mode': 'live' if live else 'fixture',
              'sources': {}, 'status': 'complete',
              'privacy': 'raw API payloads not persisted; user content hidden unless --details'}
    for source, command in commands.items():
        try:
            payload = execute(command) if live else load_fixture(Path(fixture_dir), source)
            rows, more, shape = _extract(payload, source)
            if source == 'tasks':
                rows = [r for r in rows if r.get('completed') is not True and r.get('completed_at') in (None, '', '0', 0)]
            elif source == 'calendar':
                rows = [r for r in rows if r.get('status') not in ('cancelled', 'canceled')]
            item = {'state': 'ok', 'observed_count': len(rows),
                    'has_more': more, 'response_list_key': shape}
            if details:
                item['items'] = [{'title': _safe_title(row, source),
                                  **({'link': link} if (link := _safe_link(row)) else {})}
                                 for row in rows[:30]]
            report['sources'][source] = item
            if more:
                report['status'] = 'partial'
        except LarkError as exc:
            report['sources'][source] = {'state': 'blocked', 'reason': str(exc)}
            report['status'] = 'partial'
    return report


def markdown_brief(report: dict) -> str:
    lines = [f'# Daily Brief / 每日简报 — {report["date"]}', '',
             f'**Mode:** {report["mode"]}  |  **Status:** {report.get("status", report.get("state"))}', '']
    if report['mode'] == 'offline_plan':
        lines += ['Read-only commands planned (not executed):', '']
        for source, command in report['commands'].items():
            # Human-readable; never shell executes this representation.
            lines.append(f'- **{source}**: `{" ".join(command)}`')
        return '\n'.join(lines) + '\n'
    for source, item in report['sources'].items():
        if item['state'] != 'ok':
            lines.append(f'- **{source}**: BLOCKED — {item["reason"]}')
            continue
        lines.append(f'- **{source}**: {item["observed_count"]} fetched' +
                     (' (more pages exist; NOT a complete total)' if item['has_more'] else ''))
        for value in item.get('items', []):
            if value.get('link'):
                lines.append(f'  - {value["title"]} — {value["link"]}')
            else:
                lines.append('  - ' + value['title'])
    lines += ['', '**Interpretation:** Items are source records, not AI-inferred commitments.',
              'Review deadlines and ownership in the native Lark app. This command does not create tasks or notifications.']
    return '\n'.join(lines) + '\n'
