"""Hermes-free lark-cli provider contract. No real Feishu account/network needed."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import agentready
from agentready_lark import LarkError, build_brief, commands_for_day, markdown_brief


class LarkFirstV03Tests(unittest.TestCase):
    def test_team_provider_is_cli_first(self):
        self.assertIn('lark_cli', [name for name, _ in agentready.resolved('team')])

    def test_hermes_is_optional_in_team(self):
        self.assertNotIn('hermes', [name for name, _ in agentready.resolved('team')])

    def test_default_brief_offline(self):
        result = build_brief('2026-10-15')
        self.assertEqual(result['mode'], 'offline_plan')
        self.assertEqual(result['state'], 'not_tested')

    def test_read_only_explicit_user_commands(self):
        commands = commands_for_day('2026-10-15', '待办')
        for cmd in commands.values():
            self.assertEqual(cmd[0], 'lark-cli')
            self.assertEqual(cmd[-2:], ['--as','user'])
            self.assertNotIn('create', ' '.join(cmd))
        self.assertEqual(len(commands), 3)

    def test_no_full_message_ingest_by_default(self):
        self.assertNotIn('messages', commands_for_day('2026-10-15'))

    def test_reject_query_option_injection(self):
        with self.assertRaises(LarkError):
            commands_for_day('2026-10-15', '--as bot')
        with self.assertRaises(LarkError):
            commands_for_day('2026-10-15', 'a\n-b')

    def test_fixture_success_with_provenance(self):
        report = build_brief('2026-10-15', fixture_dir='examples/fixtures', message_query='计划',details=True)
        self.assertEqual(report['status'], 'complete')
        self.assertEqual(report['sources']['tasks']['observed_count'],2)
        self.assertEqual(report['sources']['calendar']['observed_count'],1)
        self.assertNotIn('Synthetic task discussion', str(report))
        self.assertIn('https://example.org/task/1',markdown_brief(report))

    def test_scope_failure_is_blocked_not_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)
            (path/'tasks.json').write_text('{"ok":false,"code":99991672}')
            (path/'calendar.json').write_text('{"code":0,"data":{"events":[]}}')
            report=build_brief('2026-10-15',fixture_dir=tmp)
            self.assertEqual(report['status'],'partial')
            self.assertEqual(report['sources']['tasks']['state'],'blocked')
            self.assertEqual(report['sources']['calendar']['observed_count'],0)

    def test_unknown_schema_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)
            (path/'tasks.json').write_text('{"ok":true,"data":{"username":"Alice"}}')
            (path/'calendar.json').write_text('{"code":0,"data":{"events":[]}}')
            report=build_brief('2026-10-15',fixture_dir=tmp)
            self.assertEqual(report['sources']['tasks']['state'],'blocked')

    def test_no_live_in_fixture_or_shell(self):
        with patch('agentready_lark.subprocess.run') as proc:
            result=build_brief('2026-10-15',fixture_dir='examples/fixtures')
            proc.assert_not_called()
        self.assertEqual(result['mode'],'fixture')

    def test_empty_has_more_marks_partial(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)
            (path/'tasks.json').write_text('{"data":{"tasks":[],"has_more":true}}')
            (path/'calendar.json').write_text('{"data":{"events":[]}}')
            report=build_brief('2026-10-15',fixture_dir=tmp)
            self.assertEqual(report['status'],'partial')

    def test_live_future_blocked_before_runner(self):
        import datetime as dt
        tomorrow=(dt.date.today()+dt.timedelta(days=1)).isoformat()
        with self.assertRaisesRegex(LarkError,'today'):
            build_brief(tomorrow,live=True,execute=lambda c:self.fail('should never execute'))

    def test_reject_mixed_modes(self):
        import datetime as dt
        today=dt.date.today().isoformat()
        with self.assertRaises(LarkError):
            build_brief(today,live=True,fixture_dir='examples/fixtures')

    def test_write_new_report_never_overwrites(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/'report.md'; out.write_text('mine')
            with self.assertRaises(RuntimeError): agentready.write_new(str(out),'changed')
            self.assertEqual(out.read_text(),'mine')


if __name__ == '__main__':
    unittest.main()
