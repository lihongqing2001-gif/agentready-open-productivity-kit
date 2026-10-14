"""AgentReady v0.2 tests use only a synthetic loopback provider."""
import importlib.util
import json
import pathlib
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from unittest.mock import patch

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('agentready_connectors', ROOT / 'agentready_connectors.py')
connector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(connector)
spec = importlib.util.spec_from_file_location('agentready', ROOT / 'agentready.py')
agent = importlib.util.module_from_spec(spec)
spec.loader.exec_module(agent)


class FixtureService(BaseHTTPRequestHandler):
    hits = []

    def do_GET(self):
        self.hits.append(('GET', self.path))
        if self.path in ('/api/v1/status', '/api/app:getInfo'):
            response = {'ok': True, 'version': 'synthetic'}
            status = 200
        elif self.path == '/api/v1/users/self':
            status = 200 if self.headers.get('Authorization') == 'Bearer fake-token' else 401
            response = {'email': 'private-do-not-print@example.com'}
        elif self.path == '/redirect':
            self.send_response(302)
            self.send_header('Location', 'https://example.com/private')
            self.end_headers()
            return
        else:
            response, status = {}, 404
        data = json.dumps(response).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        self.hits.append(('POST', self.path))
        length = int(self.headers.get('Content-Length', '0'))
        submitted = json.loads(self.rfile.read(length))
        if self.path != '/api/mcp' or submitted.get('method') != 'initialize':
            self.send_response(404)
            self.end_headers()
            return
        result = {'jsonrpc': '2.0', 'id': 1,
                  'result': {'protocolVersion': '2025-03-26',
                             'serverInfo': {'name': 'fixture', 'version': '0.0.0'},
                             'capabilities': {}}}
        data = ('event: message\ndata: ' + json.dumps(result) + '\n\n').encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'text/event-stream')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *_):
        pass


class NetworkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.httpd = ThreadingHTTPServer(('127.0.0.1', 0), FixtureService)
        cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.thread.start()
        cls.origin = 'http://127.0.0.1:' + str(cls.httpd.server_port)

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()
        cls.thread.join(timeout=3)

    def setUp(self):
        FixtureService.hits = []

    def test_default_verify_never_requests(self):
        status = connector.verify('homebox', self.origin)
        self.assertFalse(status['network_executed'])
        self.assertEqual(FixtureService.hits, [])

    def test_homebox_status_does_not_read_items(self):
        status = connector.verify('homebox', self.origin, live=True)
        self.assertEqual(status['reachability'], 'passed')
        self.assertEqual(status['auth'], 'not_tested')
        self.assertEqual(FixtureService.hits, [('GET', '/api/v1/status')])

    def test_homebox_token_authenticated_without_data_output(self):
        with patch.dict('os.environ', {'AR_TEST_TOKEN': 'fake-token'}):
            status = connector.verify('homebox', self.origin, live=True, token_env='AR_TEST_TOKEN')
        self.assertEqual(status['auth'], 'passed')
        self.assertNotIn('private-do-not-print', json.dumps(status))
        self.assertNotIn('fake-token', json.dumps(status))
        self.assertEqual(FixtureService.hits, [('GET', '/api/v1/status'), ('GET', '/api/v1/users/self')])

    def test_nocobase_mcp_handshake_without_tools_call(self):
        status = connector.verify('nocobase', self.origin, live=True, mcp=True)
        self.assertEqual(status['reachability'], 'passed')
        self.assertEqual(status['mcp_handshake'], 'passed')
        self.assertEqual(FixtureService.hits, [('GET', '/api/app:getInfo'), ('POST', '/api/mcp')])

    def test_missing_env_prevents_network_request(self):
        with patch.dict('os.environ', {}, clear=True):
            status = connector.verify('homebox', self.origin, live=True, token_env='AR_FAKE_TOKEN')
        self.assertEqual(status['auth'], 'missing_local_env')
        self.assertEqual(FixtureService.hits, [])

    def test_remote_requires_explicit_https_and_opt_in(self):
        with self.assertRaisesRegex(ValueError, 'Remote probes'):
            connector.verify('homebox', 'https://example.org', live=False)
        with self.assertRaisesRegex(ValueError, 'Remote probes'):
            connector.verify('homebox', 'http://example.org', live=False, allow_remote=True)
        status = connector.verify('homebox', 'https://example.org', allow_remote=True)
        self.assertFalse(status['network_executed'])

    def test_reject_url_credentials_and_resources(self):
        for url in ['http://foo:bar@127.0.0.1:8888', self.origin + '/api/v1/entities',
                    self.origin + '?secret=1', 'file:///etc/passwd']:
            with self.subTest(url=url), self.assertRaises(ValueError):
                connector.verify('homebox', url)

    def test_reject_arbitrary_env_name(self):
        with self.assertRaises(ValueError):
            connector.verify('homebox', self.origin, token_env='AR_TOKEN;env')


class WizardAndCoverageTests(unittest.TestCase):
    def test_wizard_no_secrets_and_overrides(self):
        replies = iter(['n' if name == 'codex' else 'y' if name == 'homebox' else ''
                        for name in agent.catalog()])
        cfg = agent.create_wizard_config('starter', ask=lambda _: next(replies))
        self.assertIn('codex', cfg['disable'])
        self.assertIn('homebox', cfg['enable'])
        self.assertNotIn('api_key', json.dumps(cfg).lower())
        with tempfile.TemporaryDirectory() as td:
            path = str(pathlib.Path(td) / 'my-config.json')
            agent.write_new(path, json.dumps(cfg))
            items = agent.resolved('starter', path)
            self.assertIn('homebox', [key for key, _ in items])
            with self.assertRaisesRegex(RuntimeError, 'Refusing'):
                agent.write_new(path, '{}')

    def test_coverage_reveals_unselected_capabilities(self):
        coverage = agent.capability_coverage(agent.resolved('starter'))
        by_id = {c['capability']: c for c in coverage}
        self.assertEqual(by_id['household_inventory']['state'], 'not_selected')
        self.assertEqual(by_id['calendar']['selected_providers'], ['apple_calendar'])
        self.assertEqual(by_id['ai_agent']['state'], 'selected_not_verified')

    def test_report_is_offline_and_contains_truth_in_labeled_status(self):
        with patch.object(agent.subprocess, 'run') as run:
            content = agent.offline_report('starter', agent.resolved('starter'))
            run.assert_not_called()
        self.assertIn('selection ≠ verified connection', content)
        self.assertIn('## Next verification gates', content)


if __name__ == '__main__':
    unittest.main()
