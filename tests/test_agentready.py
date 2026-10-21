import importlib.util
import json
import pathlib
import subprocess
import sys
import unittest
from unittest.mock import patch

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('agentready', ROOT / 'agentready.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class AgentReadyTests(unittest.TestCase):
    def test_all_profiles_resolve(self):
        for name in mod.profiles():
            self.assertGreater(len(mod.resolved(name)), 0)

    def test_brewfile_is_curated_and_deduplicated(self):
        lines = mod.bundle(mod.resolved('power')).splitlines()
        self.assertIn('cask "codex"', lines)
        self.assertIn('cask "feishu"', lines)
        self.assertEqual(lines.count('cask "codex"'), 1)
        self.assertFalse(any('curl ' in l for l in lines))

    def test_no_install_without_apply(self):
        with patch.object(mod, 'apply_brewfile') as execute:
            self.assertEqual(mod.main(['install', '--profile', 'starter']), 0)
            execute.assert_not_called()

    def test_read_commands_never_run_subprocess(self):
        with patch.object(mod.subprocess, 'run') as execute:
            for cmd in ['doctor', 'plan', 'permissions', 'inventory', 'brewfile']:
                self.assertEqual(mod.main([cmd, '--profile', 'starter']), 0)
            execute.assert_not_called()

    def test_unknown_adapter_rejected(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            config = pathlib.Path(tmp) / 'config.json'
            config.write_text(json.dumps({'enable': ['made-up-provider']}))
            with self.assertRaisesRegex(ValueError, 'Unknown adapters'):
                mod.resolved('starter', str(config))

    def test_never_execute_registry_commands(self):
        selected = [('unsafe', {'label': 'Unsafe', 'category': 'misc', 'purpose': 'test',
                                'macos_install': {'brew': ['x";rm -rf /']}})]
        with self.assertRaisesRegex(ValueError, 'Unsafe package'):
            mod.bundle(selected)

    def test_skill_frontmatter_present_and_named(self):
        for f in (ROOT / '.agents' / 'skills').glob('*/SKILL.md'):
            data = f.read_text()
            self.assertTrue(data.startswith('---\n'))
            self.assertIn('name: ' + f.parent.name, data)
            self.assertIn('\ndescription:', data)

    def test_downloadable_workflow_skill_covers_setup_and_acceptance(self):
        data = (ROOT / '.agents' / 'skills' / 'agentready-workflow' / 'SKILL.md').read_text().lower()
        for term in ('dayflow', 'codex', 'feishu', 'daily', 'weekly', 'deduplicated', 'readback'):
            self.assertIn(term, data)

    def test_public_source_contains_no_private_example_hosts(self):
        registry = (ROOT / 'registry' / 'adapters.json').read_text()
        self.assertNotIn('bluefocus', registry.lower())
        self.assertNotIn('trycloudflare', registry.lower())
        self.assertNotIn('api_key', registry.lower())


if __name__ == '__main__':
    unittest.main()
