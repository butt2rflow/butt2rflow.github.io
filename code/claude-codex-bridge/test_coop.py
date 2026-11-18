import json
import os
from pathlib import Path
import shutil
import subprocess
import signal
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

import coop


class BridgeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.project = self.root / 'project'
        self.project.mkdir()
        self.bridge = self.root / 'bridge'
        self.bridge.mkdir()
        shutil.copy(Path(coop.__file__), self.bridge / 'coop.py')
        self.models_cache = self.root / 'models_cache.json'
        source = self.bridge / 'coop.py'
        source.write_text(source.read_text().replace(
            "CODEX_MODELS_CACHE = Path.home() / '.codex/models_cache.json'",
            f'CODEX_MODELS_CACHE = Path({str(self.models_cache)!r})'))
        self.bin = self.root / 'bin'
        self.bin.mkdir()
        fake = self.bin / 'codex'
        fake.write_text('''#!/usr/bin/env python3
import sys, pathlib, os, time, json
args=sys.argv[1:]
prompt=sys.stdin.read()
pathlib.Path(args[args.index('--cd')+1], 'invocation.json').write_text(json.dumps({'args':args,'prompt':prompt}))
time.sleep(float(os.environ.get('FAKE_DELAY','0')))
if os.environ.get('FAKE_FAIL'):
    pathlib.Path(args[args.index('--cd')+1], 'partial.txt').write_text('partial')
    sys.exit(3)
if os.environ.get('FAKE_WRITE') and args[args.index('--sandbox')+1] == 'workspace-write':
    pathlib.Path(args[args.index('--cd')+1], 'generated.txt').write_text('created by fixture')
answer='Fixture completed; no paid API call.'
if os.environ.get('FAKE_HOST'):
    cwd=pathlib.Path(args[args.index('--cd')+1])
    if 'Fix add(a,b)' in prompt:
        (cwd/'calculator.py').write_text('def add(a, b):\\n    return a + b\\n')
        answer='PASS calculator.py'
    elif 'Review review_case.py' in prompt:
        answer='P1 review_case.py:3 REVIEW_ZERO_DIVISION'
    else:
        answer=(cwd/'input.txt').read_text()
pathlib.Path(args[args.index('--output-last-message')+1]).write_text(answer)
''')
        fake.chmod(0o755)
        gpu = self.bin / 'nvidia-smi'
        gpu.write_text('#!/bin/sh\nexit 1\n')
        gpu.chmod(0o755)
        self.env = dict(os.environ, PATH=str(self.bin) + os.pathsep + os.environ['PATH'])
        self.patches = [patch.object(coop, 'ROOT', self.bridge),
                        patch.object(coop, 'RUNS', self.bridge / 'runs'),
                        patch.object(coop, 'CODEX_MODELS_CACHE', self.models_cache)]
        for p in self.patches:
            p.start()

    def tearDown(self):
        for p in self.patches:
            p.stop()
        self.tmp.cleanup()

    def cli(self, *args, **env):
        p = subprocess.run([sys.executable, str(self.bridge / 'coop.py'), *args],
                           env=dict(self.env, **env), capture_output=True, text=True, timeout=10)
        self.assertEqual(p.returncode, 0, p.stderr)
        return json.loads(p.stdout)

    def wait(self, job):
        for _ in range(100):
            result = self.cli('result', job)
            if result['status'] not in ('queued', 'running'):
                return result
            time.sleep(.05)
        self.fail('Worker did not finish')

    def test_background_task_persists_after_launcher_exit(self):
        result = self.cli('start', '--cwd', str(self.project), '--task', 'Review', FAKE_DELAY='.2')
        state = self.wait(result['id'])
        self.assertEqual(state['status'], 'completed')
        self.assertIn('no paid API call', state['summary'])
        p = self.bridge / 'runs' / result['id']
        for name in ('request.json', 'before.json', 'after.json', 'HANDOFF.md'):
            self.assertTrue((p / name).exists(), name)
        invocation = json.loads((self.project / 'invocation.json').read_text())
        self.assertIn('read-only', invocation['args'])
        self.assertIn('never', invocation['args'])
        self.assertNotIn('-m', invocation['args'])
        self.assertNotIn('-c', invocation['args'])
        self.assertNotIn('--dangerously-bypass-approvals-and-sandbox', invocation['args'])
        self.assertIn('at most 8 short lines and 800 characters', invocation['prompt'])

    def test_model_cache_aliases_validation_and_reload(self):
        models = [{'slug': slug} for slug in
                  ('gpt-6.2-sol', 'gpt-6.10-sol', 'gpt-6-astra', 'gpt-6.1-terra')]
        models[1]['supported_reasoning_levels'] = [{'effort': 'medium'}, {'effort': 'max'}]
        coop.save(self.models_cache, {'models': models})
        for alias, slug in [('sol', 'gpt-6.10-sol'), ('astra', 'gpt-6-astra'),
                            ('terra', 'gpt-6.1-terra')]:
            self.assertEqual(coop.resolve_codex_selection(alias, None), {'model': slug})
        self.assertEqual(coop.resolve_codex_selection('sol', 'max'),
                         {'model': 'gpt-6.10-sol', 'effort': 'max'})
        with self.assertRaisesRegex(ValueError, 'Invalid Codex effort'):
            coop.resolve_codex_selection('sol', 'high')
        with self.assertRaisesRegex(ValueError, 'Unknown Codex model'):
            coop.resolve_codex_selection('gpt-7-sol', None)
        coop.save(self.models_cache, {'models': models[:1]})
        self.assertEqual(coop.resolve_codex_selection('sol', None), {'model': 'gpt-6.2-sol'})
        with self.assertRaisesRegex(ValueError, 'No Codex model found for alias'):
            coop.resolve_codex_selection('terra', None)

    def test_missing_model_cache_and_effort_only_validation(self):
        self.assertEqual(coop.resolve_codex_selection('gpt-7.astra', 'xhigh'),
                         {'model': 'gpt-7.astra', 'effort': 'xhigh'})
        for model in ('sol', 'o3', 'gpt-7 as', 'gpt-7;'):
            with self.subTest(model=model), self.assertRaisesRegex(ValueError, 'full gpt-'):
                coop.resolve_codex_selection(model, None)
        for effort in ('', 'max', 'HIGH'):
            with self.subTest(effort=effort), self.assertRaisesRegex(ValueError, 'Invalid Codex effort'):
                coop.resolve_codex_selection(None, effort)
        with self.assertRaisesRegex(ValueError, 'require target=codex'):
            coop.start(str(self.project), 'Review', target='qwen', effort='medium')

    def test_cli_model_and_effort_can_be_used_independently(self):
        for option, value, expected in [
            ('--model', 'gpt-7-sol', ['-m', 'gpt-7-sol']),
            ('--effort', 'medium', ['-c', 'model_reasoning_effort="medium"']),
        ]:
            with self.subTest(option=option):
                run = self.cli('start', '--cwd', str(self.project), '--task', 'Review', option, value)
                self.assertEqual(self.wait(run['id'])['status'], 'completed')
                args = json.loads((self.project / 'invocation.json').read_text())['args']
                self.assertEqual(args[args.index('--output-last-message') + 2:], expected + ['-'])

    def test_failure_preserves_partial_changes_and_requires_review(self):
        result = self.cli('start', '--cwd', str(self.project), '--task', 'Edit', '--write', FAKE_FAIL='1')
        state = self.wait(result['id'])
        self.assertEqual(state['status'], 'needs_review')
        self.assertEqual((self.project / 'partial.txt').read_text(), 'partial')
        self.assertIn('exit 3', state['error'])

    def test_write_execution_and_snapshots_preserve_preexisting_user_work(self):
        subprocess.run(['git', 'init', '-q', str(self.project)], check=True)
        (self.project / 'user-work.txt').write_text('preserve this')
        result = self.cli('start', '--cwd', str(self.project), '--task', 'Create generated.txt', '--write', FAKE_WRITE='1')
        self.assertEqual(self.wait(result['id'])['status'], 'completed')
        self.assertEqual((self.project / 'user-work.txt').read_text(), 'preserve this')
        self.assertEqual((self.project / 'generated.txt').read_text(), 'created by fixture')
        p = self.bridge / 'runs' / result['id']
        before = json.loads((p / 'before.json').read_text())
        after = json.loads((p / 'after.json').read_text())
        self.assertIn('user-work.txt', before['status'])
        self.assertNotIn('generated.txt', before['status'])
        self.assertIn('user-work.txt', after['status'])
        self.assertIn('generated.txt', after['status'])

    def test_duplicate_execution_rejected(self):
        result = self.cli('start', '--cwd', str(self.project), '--task', 'Review', FAKE_DELAY='.5')
        with self.assertRaisesRegex(ValueError, 'active bridge task'):
            coop.start(str(self.project), 'Duplicate')
        self.wait(result['id'])

    def test_unavailable_qwen_routes_before_execution_only(self):
        with patch.object(coop, 'project', return_value=self.project), \
             patch.object(coop, 'shell', return_value=subprocess.CompletedProcess([], 1, '', '')), \
             patch.object(coop, 'git_snapshot', return_value={}), \
             patch.object(coop, 'qwen_status', return_value={'available': False, 'reason': 'GPU busy'}), \
             patch('subprocess.Popen') as popen:
            result = coop.start(str(self.project), 'Analyze', target='auto')
            self.assertEqual(result['target'], 'codex')
            self.assertEqual(result['route'], 'GPU busy')
            self.assertEqual(popen.call_count, 1)

    def test_explicit_qwen_refuses_unavailable_gpu(self):
        with patch.object(coop, 'qwen_status', return_value={'available': False, 'reason': 'unavailable'}):
            with self.assertRaisesRegex(ValueError, 'unavailable'):
                coop.start(str(self.project), 'Analyze', target='qwen')
        self.assertFalse((self.bridge / 'runs').exists())

    def test_gpu_query_failure_does_not_call_ollama(self):
        with patch.object(coop, 'shell', return_value=subprocess.CompletedProcess([], 1, '', 'denied')), \
             patch.object(coop, 'ollama') as api:
            self.assertFalse(coop.qwen_status()['available'])
            api.assert_not_called()

    def test_other_gpu_process_blocks_even_small_allocations(self):
        with patch.object(coop, 'shell', return_value=subprocess.CompletedProcess([], 0, '123, 10, python3\n', '')), \
             patch.object(coop, 'ollama') as api:
            self.assertFalse(coop.qwen_status()['available'])
            api.assert_not_called()

    def test_model_must_already_be_loaded(self):
        with patch.object(coop, 'shell', return_value=subprocess.CompletedProcess([], 0, '', '')), \
             patch.object(coop, 'ollama', return_value={'models': []}) as api:
            self.assertFalse(coop.qwen_status()['available'])
            api.assert_called_once_with('/api/ps')

    def test_file_cannot_escape_project(self):
        outside = self.root / 'outside.txt'
        outside.write_text('not an input')
        with self.assertRaisesRegex(ValueError, 'inside cwd'):
            coop.start(str(self.project), 'Analyze', files=['../outside.txt'])

    def test_symlink_cannot_escape_project(self):
        outside = self.root / 'outside.txt'
        outside.write_text('not an input')
        (self.project / 'link.txt').symlink_to(outside)
        with self.assertRaisesRegex(ValueError, 'inside cwd'):
            coop.start(str(self.project), 'Analyze', files=['link.txt'])

    def test_subdirectory_keeps_cwd_but_shares_repository_lock(self):
        subprocess.run(['git', 'init', '-q', str(self.project)], check=True)
        sub = self.project / 'sub'
        sub.mkdir()
        (sub / 'input.txt').write_text('local input')
        result = self.cli('start', '--cwd', str(sub), '--file', 'input.txt', '--task', 'Review', FAKE_DELAY='.3')
        request = json.loads((self.bridge / 'runs' / result['id'] / 'request.json').read_text())
        self.assertEqual(request['cwd'], str(sub))
        self.assertEqual(request['files'], [str(sub / 'input.txt')])
        with self.assertRaisesRegex(ValueError, 'active bridge task'):
            with coop.lock(self.project):
                pass
        self.wait(result['id'])

    def test_poll_race_does_not_overwrite_just_finished_state(self):
        job_id = 'e' * 32
        p = self.bridge / 'runs' / job_id
        state = dict(id=job_id, cwd=str(self.project), target='codex', status='running')
        coop.save(p / 'state.json', state)
        original_lock = coop.lock
        def finish_just_before_lock(cwd):
            coop.save(p / 'state.json', dict(state, status='completed'))
            return original_lock(cwd)
        with patch.object(coop, 'lock', side_effect=finish_just_before_lock):
            self.assertEqual(coop.job_status(job_id)['status'], 'completed')
        self.assertEqual(json.loads((p / 'state.json').read_text())['status'], 'completed')

    def test_no_final_report_requires_review(self):
        fake = self.bin / 'codex'
        fake.write_text('#!/usr/bin/env python3\nimport sys\nsys.stdin.read()\n')
        result = self.cli('start', '--cwd', str(self.project), '--task', 'Review')
        state = self.wait(result['id'])
        self.assertEqual(state['status'], 'needs_review')
        self.assertIn('no final result', state['error'])

    def test_mcp_can_reconnect_after_delegation_without_restarting_work(self):
        def request(server, method, params, req_id):
            server.stdin.write(json.dumps(dict(jsonrpc='2.0', id=req_id, method=method, params=params)) + '\n')
            server.stdin.flush()
            return json.loads(server.stdout.readline())['result']
        server = subprocess.Popen([sys.executable, str(self.bridge / 'coop.py'), 'serve'],
                                  stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                  text=True, env=dict(self.env, FAKE_DELAY='.4'))
        try:
            request(server, 'initialize', {'protocolVersion': '2025-11-25'}, 1)
            result = request(server, 'tools/call', {'name': 'delegate_task',
                             'arguments': {'cwd': str(self.project), 'task': 'Review',
                                           'model': 'gpt-6.2-sol', 'effort': 'high'}}, 2)
            self.assertFalse(result['isError'])
            job_id = json.loads(result['content'][0]['text'])['id']
        finally:
            server.stdin.close()
            server.wait(timeout=5)
            server.stdout.close()
            server.stderr.close()
        self.assertEqual(self.wait(job_id)['status'], 'completed')
        request_record = json.loads((self.bridge / 'runs' / job_id / 'request.json').read_text())
        self.assertEqual(request_record['task'], 'Review')
        self.assertEqual((request_record['model'], request_record['effort']), ('gpt-6.2-sol', 'high'))
        self.assertEqual(len(list((self.bridge / 'runs').iterdir())), 1)

    def test_host_verifier_full_workflow_with_fake_codex_and_no_gpu(self):
        shutil.copy(Path(coop.__file__).parent / 'verify_host.py', self.bridge / 'verify_host.py')
        # Avoid recursive discovery of this harness inside the copied verifier.
        (self.bridge / 'test_coop.py').write_text('import unittest\nclass Fixture(unittest.TestCase):\n    def test_fixture(self): self.assertTrue(True)\n')
        p = subprocess.run([sys.executable, str(self.bridge / 'verify_host.py')],
                           env=dict(self.env, FAKE_HOST='1'), capture_output=True, text=True, timeout=40)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        records = list((self.bridge / 'verification').glob('host-*/results.json'))
        self.assertEqual(len(records), 1)
        checks = {c['check']: c['status'] for c in json.loads(records[0].read_text())}
        for name in ('mcp_protocol', 'codex_live_read_and_reconnect', 'codex_live_edit_and_tests', 'codex_live_review'):
            self.assertEqual(checks[name], 'PASS')
        self.assertEqual(checks['qwen_live_read'], 'SKIP')

    def test_worker_crash_does_not_unlock_while_child_is_running(self):
        result = self.cli('start', '--cwd', str(self.project), '--task', 'Review', FAKE_DELAY='.6')
        p = self.bridge / 'runs' / result['id']
        for _ in range(100):
            state = json.loads((p / 'state.json').read_text())
            if 'child_pid' in state and (self.project / 'invocation.json').exists():
                break
            time.sleep(.01)
        else:
            self.fail('Child did not start')
        os.kill(state['worker_pid'], signal.SIGKILL)
        with self.assertRaisesRegex(ValueError, 'active bridge task'):
            with coop.lock(self.project):
                pass
        terminal = self.wait(result['id'])
        self.assertEqual(terminal['status'], 'needs_review')
        self.assertTrue((p / 'HANDOFF.md').exists())

    def test_qwen_disabled_never_queries_gpu(self):
        (self.bridge / 'QWEN_DISABLED').write_text('disabled')
        with patch.object(coop, 'shell') as run, patch.object(coop, 'ollama') as api:
            self.assertFalse(coop.qwen_status()['available'])
            run.assert_not_called()
            api.assert_not_called()

    def test_qwen_ready_and_offloaded_cases(self):
        gpu = subprocess.CompletedProcess([], 0, '123, 18000, /usr/bin/ollama\n', '')
        for vram, expected in [(100, True), (99, False), (50, False)]:
            with self.subTest(vram=vram), patch.object(coop, 'shell', return_value=gpu), \
                 patch.object(coop, 'ollama', return_value={'models': [{'name': coop.MODEL, 'size': 100, 'size_vram': vram}]}):
                self.assertEqual(coop.qwen_status()['available'], expected)

    def test_malformed_gpu_or_model_metadata_fails_closed(self):
        with patch.object(coop, 'shell', return_value=subprocess.CompletedProcess([], 0, 'malformed csv', '')), \
             patch.object(coop, 'ollama') as api:
            self.assertFalse(coop.qwen_status()['available'])
            api.assert_not_called()
        for metadata in [{'name': coop.MODEL}, {'name': coop.MODEL, 'size': 0, 'size_vram': 0}]:
            with self.subTest(metadata=metadata), \
                 patch.object(coop, 'shell', return_value=subprocess.CompletedProcess([], 0, '', '')), \
                 patch.object(coop, 'ollama', return_value={'models': [metadata]}):
                self.assertFalse(coop.qwen_status()['available'])

    def test_qwen_worker_persists_analysis_without_modifying_project(self):
        job_id = 'f' * 32
        p = self.bridge / 'runs' / job_id
        (self.project / 'source.txt').write_text('Source text')
        coop.save(p / 'request.json', dict(id=job_id, cwd=str(self.project), target='qwen',
                  task='Summarize', files=[str(self.project / 'source.txt')], timeout=30))
        coop.save(p / 'state.json', dict(id=job_id, cwd=str(self.project), target='qwen', status='queued'))
        with coop.lock(self.project) as held, \
             patch.object(coop, 'qwen_status', return_value={'available': True}), \
             patch.object(coop, 'ollama', return_value={'message': {'content': 'Short summary'}}) as api:
            coop.worker(job_id, os.dup(held.fileno()))
        self.assertEqual(coop.job_status(job_id)['status'], 'completed')
        self.assertEqual(coop.job_status(job_id)['summary'], 'Short summary')
        self.assertEqual(list(self.project.iterdir()), [self.project / 'source.txt'])
        self.assertIn('Source text', api.call_args.args[1]['messages'][1]['content'])

    def test_qwen_becoming_unavailable_does_not_fall_back_mid_job(self):
        job_id = '1' * 32
        p = self.bridge / 'runs' / job_id
        coop.save(p / 'request.json', dict(id=job_id, cwd=str(self.project), target='qwen',
                  task='Summarize', files=[], timeout=30))
        coop.save(p / 'state.json', dict(id=job_id, cwd=str(self.project), target='qwen', status='queued'))
        with coop.lock(self.project) as held, \
             patch.object(coop, 'qwen_status', return_value={'available': False, 'reason': 'GPU became busy'}), \
             patch.object(coop, 'git_snapshot', return_value={}), \
             patch.object(coop, 'ollama') as api, patch('subprocess.Popen') as popen:
            coop.worker(job_id, os.dup(held.fileno()))
        self.assertEqual(coop.job_status(job_id)['status'], 'needs_review')
        api.assert_not_called()
        popen.assert_not_called()

    def test_abnormal_worker_exit_is_not_completion(self):
        job_id = 'a' * 32
        coop.save(self.bridge / 'runs' / job_id / 'state.json',
                  dict(id=job_id, cwd=str(self.project), target='codex', status='running'))
        self.assertEqual(coop.job_status(job_id)['status'], 'needs_review')

    def test_compact_return_keeps_full_report_on_disk(self):
        job_id = 'c' * 32
        p = self.bridge / 'runs' / job_id
        coop.save(p / 'state.json', dict(id=job_id, cwd=str(self.project), target='codex',
                                       status='completed', worker_pid=123))
        report = 'FAIL: important finding first\n' + '상세 설명 ' * 2000
        (p / 'result.md').write_text(report)
        compact = coop.job_status(job_id)
        self.assertEqual(len(compact['summary']), coop.RETURN_CHARS)
        self.assertTrue(compact['summary_truncated'])
        self.assertTrue(compact['summary'].startswith('FAIL:'))
        self.assertNotIn('worker_pid', compact)
        self.assertEqual((p / 'result.md').read_text(), report)
        self.assertGreater(len(coop.job_status(job_id, detail=True)['summary']), coop.RETURN_CHARS)

    def test_running_poll_does_not_repeat_partial_report(self):
        job_id = 'd' * 32
        p = self.bridge / 'runs' / job_id
        coop.save(p / 'state.json', dict(id=job_id, cwd=str(self.project), target='codex', status='running'))
        (p / 'result.md').write_text('partial output should not be repeated')
        with coop.lock(self.project):
            state = coop.job_status(job_id)
        self.assertEqual(set(state), {'id', 'target', 'status'})

    def test_mcp_initialize_discovery_status_and_error(self):
        messages = [
            {'id': 1, 'method': 'initialize', 'params': {'protocolVersion': '2025-11-25', 'capabilities': {}, 'clientInfo': {'name': 'test', 'version': '1'}}},
            {'method': 'notifications/initialized'},
            {'id': 2, 'method': 'tools/list'},
            {'id': 3, 'method': 'tools/call', 'params': {'name': 'cooperation_status', 'arguments': {}}},
            {'id': 4, 'method': 'tools/call', 'params': {'name': 'job_result', 'arguments': {'job_id': '../escape'}}},
            {'id': 5, 'method': 'ping'},
        ]
        for m in messages:
            m['jsonrpc'] = '2.0'
        p = subprocess.run([sys.executable, str(self.bridge / 'coop.py'), 'serve'],
                           input='\n'.join(json.dumps(m) for m in messages) + '\n',
                           env=self.env, capture_output=True, text=True, timeout=15)
        self.assertEqual(p.returncode, 0, p.stderr)
        responses = [json.loads(line) for line in p.stdout.splitlines()]
        self.assertEqual([r['id'] for r in responses], [1, 2, 3, 4, 5])
        self.assertEqual(responses[0]['result']['protocolVersion'], '2025-11-25')
        self.assertEqual(len(responses[1]['result']['tools']), 3)
        delegation = next(t for t in responses[1]['result']['tools'] if t['name'] == 'delegate_task')
        for option in ('model', 'effort'):
            self.assertEqual(delegation['inputSchema']['properties'][option]['type'], 'string')
            self.assertNotIn(option, delegation['inputSchema']['required'])
        self.assertFalse(responses[2]['result']['isError'])
        self.assertTrue(responses[3]['result']['isError'])

    def test_timeout_stops_worker_child_and_records_review_state(self):
        job_id = 'b' * 32
        p = self.bridge / 'runs' / job_id
        request = dict(id=job_id, cwd=str(self.project), target='codex', write=False,
                       task='Review', files=[], timeout=.1)
        coop.save(p / 'request.json', request)
        coop.save(p / 'state.json', dict(id=job_id, cwd=str(self.project), target='codex', status='queued'))
        with coop.lock(self.project) as held:
            child = subprocess.Popen([sys.executable, str(self.bridge / 'coop.py'), '_worker', job_id, str(held.fileno())],
                                     pass_fds=(held.fileno(),), env=dict(self.env, FAKE_DELAY='30'),
                                     stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            _, err = child.communicate(timeout=10)
        self.assertEqual(child.returncode, 0, err)
        state = coop.job_status(job_id)
        self.assertEqual(state['status'], 'needs_review')
        self.assertIn('timed out', state['error'])


if __name__ == '__main__':
    unittest.main()
