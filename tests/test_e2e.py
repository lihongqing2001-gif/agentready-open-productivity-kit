"""Subprocess E2E: synthetic executable CLIs, isolated HOME, no real accounts."""
import datetime as dt
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class CLIE2E(unittest.TestCase):
    def test_synthetic_cli_roundtrip_and_scope_recovery(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cli = root / 'lark-cli'
            cli.write_text('#!' + sys.executable + '\n' + '''import json, os, sys
args = sys.argv[1:]
assert '--as' in args and args[args.index('--as')+1] == 'user'
assert '--profile' in args and args[args.index('--profile')+1] == 'synthetic'
if 'calendar' in args and os.getenv('TEST_DENY'):
    print(json.dumps({'ok': False, 'error': {'missing_scopes': ['calendar:calendar.event:read']}}), file=sys.stderr)
    sys.exit(3)
key = 'events' if 'calendar' in args else 'messages' if 'im' in args else 'items'
rows = [{'summary':'Synthetic only','url':'https://example.org/source'}]
print(json.dumps({'ok': True, 'data': rows if 'calendar' in args else {key: rows, 'has_more':False}}))
''')
            cli.chmod(0o755)
            env = {**os.environ, 'HOME': tmp, 'PATH': tmp + os.pathsep + os.environ['PATH']}
            command = [sys.executable, str(ROOT/'agentready.py'), 'brief', '--live', '--lark-profile', 'synthetic', '--format', 'json', '--message-query', 'test']
            result = subprocess.run(command, env=env, capture_output=True, text=True, timeout=15)
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(set(report['sources']), {'tasks', 'calendar', 'messages'})
            self.assertNotIn('Synthetic only', result.stdout)
            env['TEST_DENY'] = '1'
            result = subprocess.run(command, env=env, capture_output=True, text=True, timeout=15)
            self.assertEqual(result.returncode, 1)
            report = json.loads(result.stdout)
            self.assertEqual(report['sources']['calendar']['state'], 'blocked')
            self.assertEqual(report['sources']['tasks']['observed_count'], 1)
            self.assertIn('calendar:calendar.event:read', result.stdout)
            for cmd in [['doctor','--profile','starter'], ['coverage','--json'], ['install','--profile','starter'], ['personal-brief']]:
                result = subprocess.run([sys.executable,str(ROOT/'agentready.py'),*cmd],env=env,capture_output=True,text=True,timeout=15)
                self.assertEqual(result.returncode, 0, result.stderr)
