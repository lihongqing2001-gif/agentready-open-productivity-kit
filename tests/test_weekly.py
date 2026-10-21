import datetime as dt
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from agentready_lark import LarkError
from agentready_weekly import build_weekly_review, week_bounds, read_config, _codex

ROOT = Path(__file__).resolve().parents[1]
CONFIG = {'lark_profile': 'synthetic', 'daily_chat_ids': ['oc_daily'],
          'weekend_chat_ids': ['oc_team'], 'work_categories': ['Work']}


class WeeklyTests(unittest.TestCase):
    def test_previous_week_including_year_boundary(self):
        self.assertEqual(tuple(map(str, week_bounds('2026-10-21'))), ('2026-10-12', '2026-10-18'))
        self.assertEqual(tuple(map(str, week_bounds('2026-01-01'))), ('2025-12-22', '2025-12-28'))
        self.assertEqual(tuple(map(str, week_bounds('2026-10-19'))), ('2026-10-12', '2026-10-18'))

    def test_offline_no_reads_and_live_fixture_conflict(self):
        def fail(*args): self.fail('must not execute')
        self.assertEqual(build_weekly_review('2026-10-21', lark_execute=fail, native_execute=fail)['status'], 'not_tested')
        with self.assertRaises(LarkError):
            build_weekly_review('2026-10-21', live=True, fixture_dir='examples/fixtures')

    def test_success_real_contract_time_windows_and_boundaries(self):
        commands = []
        def lark(c):
            commands.append(c)
            if 'auth' in c:
                return {'verified': True, 'identities': {'user': {'status': 'ready', 'tokenStatus': 'valid'}}}
            chat = c[c.index('--chat-id') + 1]
            return {'data': {'messages': [{'message_id': 'om_test', 'chat_id': chat,
                                          'content': 'Synthetic delivery completed', 'create_time': '2026-10-17'}], 'has_more': False}}
        def native(c):
            commands.append(c)
            return {'date': c[2], 'cards': [{'category': 'Work', 'title': 'Synthetic code review'},
                                          {'category': 'Personal', 'title': 'PRIVATE PERSONAL'}]}
        with tempfile.TemporaryDirectory() as tmp:
            notes = Path(tmp) / 'notes.json'
            notes.write_text(json.dumps([{'date': '2026-10-14', 'source_id': 'codex://threads/synthetic', 'text': 'Synthetic test passed'},
                                         {'date': '2026-10-20', 'source_id': 'later', 'text': 'EXCLUDED DATE'}]))
            config = {**CONFIG, 'codex_notes_file': str(notes)}
            r = build_weekly_review('2026-10-21', config=config, live=True, lark_execute=lark, native_execute=native)
        self.assertEqual(r['status'], 'complete')
        self.assertEqual(len(r['sources']['dayflow']['items']), 7)
        self.assertNotIn('PRIVATE PERSONAL', str(r))
        self.assertNotIn('EXCLUDED DATE', str(r))
        weekend = [c for c in commands if c[0] == 'lark-cli' and 'oc_team' in c][0]
        self.assertTrue(weekend[weekend.index('--start') + 1].startswith('2026-10-17T00:00'))
        self.assertTrue(weekend[weekend.index('--end') + 1].startswith('2026-10-19T00:00'))
        self.assertEqual(weekend[1:3], ['--profile', 'synthetic'])
        self.assertEqual(weekend[weekend.index('--as') + 1], 'user')

    def test_partial_pages_and_failure_not_zero_other_sources_continue(self):
        def lark(c):
            if 'auth' in c:
                return {'verified': True, 'identities': {'user': {'status': 'ready', 'tokenStatus': 'valid'}}}
            if 'oc_daily' in c: raise LarkError('private diagnostic')
            return {'data': {'messages': [], 'has_more': True}}
        r = build_weekly_review('2026-10-21', config=CONFIG, live=True, lark_execute=lark,
                                native_execute=lambda c: {'date': c[2], 'cards': []})
        self.assertEqual(r['status'], 'partial')
        self.assertEqual(r['sources']['daily_reports']['state'], 'blocked')
        self.assertNotIn('private diagnostic', str(r))
        self.assertTrue(r['sources']['weekend_messages']['has_more'])
        self.assertEqual(r['sources']['dayflow']['state'], 'ok')
        self.assertEqual(r['sources']['codex']['state'], 'blocked')

    def test_wrong_chat_and_dayflow_date_rejected(self):
        r = build_weekly_review('2026-10-21', config=CONFIG, live=True,
                               lark_execute=lambda c: {'messages': [{'message_id': 'om_x', 'chat_id': 'oc_other', 'content': 'wrong scope'}]},
                               native_execute=lambda c: {'date': '2026-10-20', 'cards': []})
        self.assertEqual(r['sources']['dayflow']['state'], 'blocked')
        self.assertEqual(r['sources']['daily_reports']['state'], 'blocked')

    def test_partial_saved_daily_evidence_is_not_complete(self):
        with tempfile.TemporaryDirectory() as tmp:
            for key in ('daily_reports', 'weekend_messages', 'dayflow', 'codex'):
                (Path(tmp) / (key + '.json')).write_text(json.dumps({'state': 'partial' if key == 'daily_reports' else 'ok', 'items': []}))
            self.assertEqual(build_weekly_review('2026-10-21', fixture_dir=tmp)['status'], 'partial')

    def test_git_dates_are_exact_and_not_attributed_to_codex(self):
        with tempfile.TemporaryDirectory() as tmp:
            proc = subprocess.CompletedProcess([], 0, 'abc\t2026-10-14T12:00:00+08:00\tSynthetic fix\ndef\t2026-10-20T12:00:00+08:00\tOutside\n', '')
            with patch('agentready_weekly.subprocess.run', return_value=proc) as run:
                r = _codex(dt.date(2026,10,12), dt.date(2026,10,19), {'codex_projects': [tmp]})
            self.assertEqual(len(r['items']), 1)
            self.assertEqual(r['items'][0]['kind'], 'git_commit_not_agent_attribution')
            self.assertIn('--since=', str(run.call_args))

    def test_config_rejects_flag_injection_and_wrong_lists(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'config.json'
            for config in ({**CONFIG, 'daily_chat_ids': ['--bad']}, {**CONFIG, 'work_categories': 'Work'}, {**CONFIG, 'lark_profile': '--bad'}):
                p.write_text(json.dumps(config))
                with self.assertRaises(LarkError): read_config(p)

    def test_cli_e2e_fixture_and_private_no_overwrite_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            outfile = Path(tmp) / 'weekly.md'
            cmd = [sys.executable, str(ROOT/'agentready.py'), 'weekly-review', '--date', '2026-10-21',
                   '--fixture-dir', str(ROOT/'examples/review-fixtures'), '--output', str(outfile)]
            p = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertIn('Synthetic', outfile.read_text())
            self.assertEqual(outfile.stat().st_mode & 0o777, 0o600)
            self.assertEqual(subprocess.run(cmd, capture_output=True).returncode, 2)

    def test_live_cli_synthetic_handshakes_reads_and_delivery(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cli = root/'lark-cli'
            cli.write_text('#!' + sys.executable + '\n' + '''import json,sys
args=sys.argv[1:]
assert args[args.index('--profile')+1]=='synthetic'
if 'auth' in args:
 print(json.dumps({'verified':True,'identities':{'user':{'status':'ready','tokenStatus':'valid','openId':'ou_synthetic'}}}))
elif '+messages-send' in args:
 assert args[args.index('--as')+1]=='user'
 assert args[args.index('--user-id')+1]=='ou_synthetic'
 assert '--idempotency-key' in args
 print(json.dumps({'data':{'message_id':'om_synthetic_delivery'}}))
else:
 assert args[args.index('--as')+1]=='user'
 chat=args[args.index('--chat-id')+1]
 print(json.dumps({'data':{'messages':[{'message_id':'om_synthetic_daily','chat_id':chat,'content':'Synthetic delivered outcome'}],'has_more':False}}))
''')
            cli.chmod(0o755)
            dayflow = root/'dayflow'
            dayflow.write_text('#!' + sys.executable + '\n' + '''import json,sys
assert sys.argv[1]=='timeline'
print(json.dumps({'date':sys.argv[2],'cards':[{'category':'Work','title':'Synthetic work observed'}]}))
''')
            dayflow.chmod(0o755)
            notes = root/'notes.json'
            notes.write_text(json.dumps([{'date':'2026-10-14','source_id':'synthetic-checkpoint','text':'Synthetic accepted outcome'}]))
            config = root/'config.json'
            config.write_text(json.dumps({**CONFIG,'codex_notes_file':str(notes)}))
            env = {**os.environ,'HOME':tmp,'PATH':tmp + os.pathsep + os.environ['PATH']}
            base = [sys.executable,str(ROOT/'agentready.py')]
            p = subprocess.run(base+['weekly-review','--date','2026-10-21','--live','--config',str(config),'--format','json'],env=env,capture_output=True,text=True,timeout=15)
            self.assertEqual(p.returncode,0,p.stderr)
            report = json.loads(p.stdout)
            self.assertEqual(report['status'],'complete')
            self.assertEqual(len(report['sources']['dayflow']['items']),7)
            markdown = root/'weekly.md'
            markdown.write_text('Synthetic report; fixture only')
            p = subprocess.run(base+['publish-report','--input',str(markdown),'--lark-profile','synthetic','--receipt',str(root/'receipt.json'),'--apply'],env=env,capture_output=True,text=True,timeout=15)
            self.assertEqual(p.returncode,0,p.stderr)
            self.assertEqual(json.loads(p.stdout)['message_id'],'om_synthetic_delivery')
