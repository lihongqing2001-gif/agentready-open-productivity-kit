import json
import tempfile
import unittest
from pathlib import Path
from agentready_delivery import publish_report
from agentready_lark import LarkError


class DeliveryTests(unittest.TestCase):
    def test_preview_never_authenticates_or_sends(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'report.md'
            path.write_text('Synthetic report')
            result = publish_report(path, 'synthetic', Path(tmp)/'receipt', execute=lambda c: self.fail('no calls'))
            self.assertFalse(result['sent'])

    def test_verified_self_only_delivery_and_repeat_is_not_resent(self):
        with tempfile.TemporaryDirectory() as tmp:
            path, receipt = Path(tmp)/'report.md', Path(tmp)/'receipt.json'
            path.write_text('Synthetic ![image](https://example.org/image.png)')
            calls = []
            def execute(c):
                calls.append(c)
                if 'auth' in c:
                    return {'verified': True, 'identities': {'user': {'status': 'ready', 'tokenStatus': 'valid', 'openId': 'ou_synthetic'}}}
                return {'data': {'message_id': 'om_synthetic'}}
            result = publish_report(path, 'synthetic', receipt, apply=True, execute=execute)
            self.assertEqual(result['state'], 'sent')
            self.assertEqual(receipt.stat().st_mode & 0o777, 0o600)
            self.assertIn('--as', calls[-1])
            self.assertIn('--text', calls[-1])
            self.assertNotIn('--markdown', calls[-1])
            self.assertEqual(calls[-1][calls[-1].index('--user-id')+1], 'ou_synthetic')
            self.assertEqual(publish_report(path, 'synthetic', receipt, apply=True, execute=execute), result)
            self.assertEqual(len([c for c in calls if 'im' in c]), 1)
            path.write_text('Other report')
            with self.assertRaises(LarkError): publish_report(path, 'synthetic', receipt, apply=True, execute=execute)

    def test_timeout_leaves_attempt_for_reconciliation_not_retry(self):
        with tempfile.TemporaryDirectory() as tmp:
            path, receipt = Path(tmp)/'report.md', Path(tmp)/'receipt.json'
            path.write_text('Synthetic')
            def execute(c):
                if 'auth' in c:
                    return {'verified': True, 'identities': {'user': {'status': 'ready', 'tokenStatus': 'valid', 'openId': 'ou_synthetic'}}}
                raise LarkError('timeout')
            with self.assertRaises(LarkError): publish_report(path, 'synthetic', receipt, apply=True, execute=execute)
            self.assertEqual(json.loads(receipt.read_text())['state'], 'attempting')
            with self.assertRaisesRegex(LarkError, 'reconcile'): publish_report(path, 'synthetic', receipt, apply=True, execute=execute)

    def test_unverified_or_missing_id_never_sends(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'report.md'
            path.write_text('Synthetic')
            with self.assertRaises(LarkError):
                publish_report(path, 'synthetic', Path(tmp)/'receipt', apply=True, execute=lambda c: {'verified': False})
            self.assertFalse((Path(tmp)/'receipt').exists())
