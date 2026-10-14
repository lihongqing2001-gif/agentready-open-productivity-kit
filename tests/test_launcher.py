import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class LauncherTests(unittest.TestCase):
    def test_dry_run_keeps_provider_and_no_bypass(self):
        with tempfile.TemporaryDirectory() as tmp:
            cli = Path(tmp)/'codex'
            cli.write_text('#!/bin/sh\nif [ "$1" = "--help" ]; then echo "--sandbox --ask-for-approval"; else exit 99; fi\n')
            cli.chmod(0o755)
            env = {**os.environ, 'PATH':tmp+os.pathsep+os.environ['PATH']}
            r = subprocess.run(['bash',str(ROOT/'scripts/launch_codex_pilot.sh'),str(ROOT/'docs/prompts/GENERIC_AUTONOMOUS_PILOT.md')],env=env,capture_output=True,text=True)
            self.assertEqual(r.returncode,0,r.stderr)
            self.assertIn('DRY RUN',r.stdout)
            source=(ROOT/'scripts/launch_codex_pilot.sh').read_text()
            self.assertNotIn('--ignore-user-config',source)
            self.assertNotIn('--dangerously-bypass',source)
