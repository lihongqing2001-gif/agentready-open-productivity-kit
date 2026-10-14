import importlib.util
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('audit',ROOT/'scripts/audit_public.py')
audit=importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)

class PublicationTests(unittest.TestCase):
    def test_private_path_denied(self):
        with self.assertRaises(ValueError): audit.inspect('.reports/report.json',b'{}')
    def test_secret_pattern_sanitized(self):
        value=b'gh'+b'p_'+b'A'*30
        with self.assertRaises(ValueError) as ctx: audit.inspect('README.md',value)
        self.assertNotIn(value.decode(),str(ctx.exception))
    def test_safe_public_fixture(self):
        audit.inspect('examples/tasks.json',b'{"summary":"Synthetic only"}')
