import datetime as dt
import json
import subprocess
import unittest
from unittest.mock import patch
from agentready_lark import LarkError, commands_for_day, _extract, run_lark, build_brief

class V04Tests(unittest.TestCase):
    def test_profile_and_day_range(self):
        commands = commands_for_day('2026-10-14', lark_profile='work')
        for c in commands.values():
            self.assertEqual(c[1:3], ['--profile', 'work'])
        self.assertIn('--start', commands['calendar'])
        self.assertIn('--end', commands['calendar'])
        self.assertIn('--page-limit', commands['tasks'])

    def test_invalid_profile(self):
        with self.assertRaises(LarkError): commands_for_day('2026-10-14', lark_profile='--bad')

    def test_nested_failure_is_blocked(self):
        with self.assertRaises(LarkError): _extract({'ok': True, 'data': {'code': 999, 'items': []}}, 'tasks')

    def test_parent_pagination(self):
        rows, more, _ = _extract({'has_more': True, 'data': {'items': []}}, 'tasks')
        self.assertTrue(more)

    def test_calendar_list_envelope(self):
        rows, more, key = _extract({'ok': True, 'data': [{'summary': 'Synthetic event'}], 'meta': {'count': 1}}, 'calendar')
        self.assertEqual(rows, [{'summary': 'Synthetic event'}])
        self.assertFalse(more)
        self.assertEqual(key, 'data')

    def test_empty_list_envelope_preserves_pagination(self):
        rows, more, _ = _extract({'ok': True, 'data': [], 'has_more': True}, 'calendar')
        self.assertEqual(rows, [])
        self.assertTrue(more)

    def test_list_envelope_rejects_malformed_records(self):
        with self.assertRaises(LarkError):
            _extract({'ok': True, 'data': ['not an event']}, 'calendar')

    def test_bad_pagination_blocked(self):
        with self.assertRaises(LarkError): _extract({'items': [], 'has_more': 'false'}, 'tasks')

    def test_error_scope_preserved_without_payload(self):
        payload = {'ok': False, 'error': {'type': 'authorization', 'missing_scopes': ['calendar:calendar.event:read'], 'message': 'private text'}}
        with patch('agentready_lark.shutil.which', return_value='/bin/lark-cli'):
            with self.assertRaisesRegex(LarkError, 'calendar:calendar.event:read') as ctx:
                run_lark(['lark-cli'], runner=lambda *a, **kw: subprocess.CompletedProcess(a, 3, '', json.dumps(payload)))
        self.assertNotIn('private text', str(ctx.exception))

    def test_timeout_then_next_source_recovers(self):
        def execute(c):
            if 'task' in c: raise LarkError('timeout')
            return {'items': []}
        r = build_brief(dt.date.today().isoformat(), live=True, execute=execute)
        self.assertEqual(r['sources']['tasks']['state'], 'blocked')
        self.assertEqual(r['sources']['calendar']['state'], 'ok')

    def test_completed_tasks_do_not_count_pending(self):
        r = build_brief(dt.date.today().isoformat(), live=True, execute=lambda c: {'items': [{'completed': True}, {'completed': False}]} if 'task' in c else {'items': []})
        self.assertEqual(r['sources']['tasks']['observed_count'], 1)

    def test_cancelled_events_not_counted(self):
        r = build_brief(dt.date.today().isoformat(), live=True, execute=lambda c: {'items': [{'status': 'cancelled'}, {'status': 'confirmed'}]} if 'calendar' in c else {'items': []})
        self.assertEqual(r['sources']['calendar']['observed_count'], 1)

class NativeTests(unittest.TestCase):
    def test_offline_native_never_executes(self):
        from agentready_native import build_personal_brief
        r = build_personal_brief('2026-10-14', execute=lambda c: self.fail('must be offline'))
        self.assertEqual(r['mode'], 'offline_plan')

    def test_native_denied_not_zero_and_other_source_continues(self):
        from agentready_native import build_personal_brief
        def execute(c):
            if c[0] == 'ekctl': raise LarkError('Permission required')
            if c[0] == 'remindctl': return [{'id': 'test', 'title': 'PRIVATE', 'isCompleted': False}]
            return {'cards': [], 'date': '2026-10-14'}
        r = build_personal_brief('2026-10-14', live=True, execute=execute)
        self.assertEqual(r['sources']['calendar']['state'], 'blocked')
        self.assertEqual(r['sources']['reminders']['observed_count'], 1)
        self.assertNotIn('PRIVATE', str(r))

    def test_no_company_or_capture_commands(self):
        from agentready_native import build_personal_brief
        r = build_personal_brief('2026-10-14')
        self.assertEqual(set(r['commands']), {'calendar', 'reminders', 'activity'})
        self.assertNotIn('lark-cli', str(r))
        self.assertNotIn('record', str(r['commands']))

    def test_malformed_native_blocked(self):
        from agentready_native import build_personal_brief
        r = build_personal_brief('2026-10-14', live=True, execute=lambda c: {'unexpected': []})
        self.assertTrue(all(x['state'] == 'blocked' for x in r['sources'].values()))

class MoreErrorTests(unittest.TestCase):
    def test_process_timeout_sanitized(self):
        with patch('agentready_lark.shutil.which', return_value='/bin/lark-cli'):
            with self.assertRaisesRegex(LarkError, 'timed out'):
                run_lark(['lark-cli'], runner=lambda *a, **kw: (_ for _ in ()).throw(subprocess.TimeoutExpired('private-command',25)))

    def test_oversized_output_rejected(self):
        with patch('agentready_lark.shutil.which', return_value='/bin/lark-cli'):
            with self.assertRaisesRegex(LarkError, 'cap'):
                run_lark(['lark-cli'],runner=lambda *a, **kw: subprocess.CompletedProcess(a,0,'x'*(1024*1024+1),''))

    def test_non_json_error_is_generic(self):
        with patch('agentready_lark.shutil.which', return_value='/bin/lark-cli'):
            with self.assertRaises(LarkError) as ctx:
                run_lark(['lark-cli'],runner=lambda *a, **kw: subprocess.CompletedProcess(a,2,'','PRIVATE diagnostic'))
        self.assertNotIn('PRIVATE',str(ctx.exception))

    def test_date_range_timezone_offset_present(self):
        command=commands_for_day('2026-10-14')['calendar']
        start=dt.datetime.fromisoformat(command[command.index('--start')+1])
        end=dt.datetime.fromisoformat(command[command.index('--end')+1])
        self.assertIsNotNone(start.utcoffset())
        self.assertEqual((end.date()-start.date()).days,1)
