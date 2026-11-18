#!/usr/bin/env python3
"""Verify the bridge with live model calls and disposable fixtures.

Run in the host terminal. Uses three small real Codex tasks through MCP and,
only when already available, one Qwen task. All edits stay in new fixtures.
"""
import datetime as dt
import hashlib
import json
from pathlib import Path
import select
import subprocess
import sys
import time
import uuid

import coop


class Client:
    def __init__(self):
        self.process = subprocess.Popen(
            [sys.executable, str(coop.ROOT / 'coop.py'), 'serve'],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            text=True, bufsize=1)
        self.seq = 0
        try:
            self.rpc('initialize', {'protocolVersion': '2025-11-25', 'capabilities': {},
                                   'clientInfo': {'name': 'ai-coop-host-verifier', 'version': '1'}})
            self.process.stdin.write(json.dumps({'jsonrpc': '2.0', 'method': 'notifications/initialized'}) + '\n')
            self.process.stdin.flush()
        except Exception:
            self.close()
            raise

    def rpc(self, method, params):
        self.seq += 1
        self.process.stdin.write(json.dumps(dict(jsonrpc='2.0', id=self.seq, method=method, params=params)) + '\n')
        self.process.stdin.flush()
        if not select.select([self.process.stdout], [], [], 20)[0]:
            raise RuntimeError('MCP response timed out')
        line = self.process.stdout.readline()
        if not line:
            raise RuntimeError('MCP connection closed')
        response = json.loads(line)
        if response.get('id') != self.seq or 'error' in response:
            raise RuntimeError('Invalid MCP response: ' + str(response)[:500])
        return response['result']

    def call(self, name, **arguments):
        result = self.rpc('tools/call', dict(name=name, arguments=arguments))
        if result.get('isError'):
            raise RuntimeError(result['content'][0]['text'])
        return json.loads(result['content'][0]['text'])

    def close(self):
        if self.process.stdin and not self.process.stdin.closed:
            self.process.stdin.close()
        try:
            self.process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.process.terminate()
            self.process.wait(timeout=5)
        self.process.stdout.close()


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def execute(client, directory, task, write=False, target='codex', files=None):
    job = client.call('delegate_task', cwd=str(directory), task=task,
                      target=target, write=write, files=files or [], timeout=180)
    print(f"  {target} job: {job['id']}", flush=True)
    # A new MCP connection must recover the same task, without resubmission.
    client.close()
    client.__init__()
    for _ in range(46):
        state = client.call('job_result', job_id=job['id'])
        if state['status'] not in ('queued', 'running'):
            if len(state.get('summary', '')) > coop.RETURN_CHARS:
                raise RuntimeError('Compact return budget exceeded')
            return client, job, state
        time.sleep(5)
    raise RuntimeError('Verifier wait expired; task ID is printed above. Inspect it before retrying.')


def main():
    stamp = dt.datetime.now().strftime('%Y%m%d-%H%M%S') + '-' + uuid.uuid4().hex[:6]
    directory = coop.ROOT / 'verification' / ('host-' + stamp)
    directory.mkdir(parents=True)
    checks = []
    client = None

    def record(name, status, evidence):
        checks.append(dict(check=name, status=status, evidence=evidence))
        coop.save(directory / 'results.json', checks)
        print(f'{status}: {name}: {str(evidence)[:220]}', flush=True)

    try:
        with (directory / 'unit-tests.log').open('w') as log:
            result = subprocess.run([sys.executable, '-m', 'unittest', '-v', 'test_coop.py'],
                                    cwd=coop.ROOT, stdout=log, stderr=log, timeout=60)
        record('automated_tests', 'PASS' if result.returncode == 0 else 'FAIL', 'unit-tests.log')
        if result.returncode:
            return 1

        client = Client()
        tools = client.rpc('tools/list', {})['tools']
        names = {tool['name'] for tool in tools}
        if names != {'cooperation_status', 'delegate_task', 'job_result'}:
            raise RuntimeError('Unexpected MCP tool discovery')
        record('mcp_protocol', 'PASS', sorted(names))
        availability = client.call('cooperation_status')['qwen']
        record('qwen_preflight', 'PASS' if availability['available'] else 'SKIP', availability['reason'])

        read_dir = directory / 'read'
        read_dir.mkdir()
        marker = 'COOP_READ_' + uuid.uuid4().hex
        source = read_dir / 'input.txt'
        source.write_text('verification-marker: ' + marker + '\n')
        before = digest(source)
        client, job, state = execute(client, read_dir,
            'Read input.txt and report its exact verification-marker. Do not edit any files. Maximum two short lines.',
            files=['input.txt'])
        if state['status'] != 'completed':
            record('codex_live_read', 'BLOCKED', dict(job=job['id'], error=state.get('error'), log=job['directory'] + '/codex.log'))
            return 2  # No point spending further Codex calls after startup failure.
        if marker not in state.get('summary', '') or digest(source) != before:
            raise RuntimeError('Live read marker missing or input changed')
        record('codex_live_read_and_reconnect', 'PASS', job['id'])

        edit_dir = directory / 'edit'
        edit_dir.mkdir()
        (edit_dir / 'calculator.py').write_text('def add(a, b):\n    return a - b\n')
        tests = edit_dir / 'test_calculator.py'
        tests.write_text('import unittest\nfrom calculator import add\nclass Addition(unittest.TestCase):\n    def test_add(self):\n        self.assertEqual(add(2, 3), 5)\n        self.assertEqual(add(-2, 3), 1)\n')
        test_hash = digest(tests)
        client, job, state = execute(client, edit_dir,
            'Fix add(a,b) in calculator.py to return the sum. Allowed modification: calculator.py only. '
            'Do not edit test_calculator.py. Run python3 -m unittest -v. Report PASS/FAIL and changed path.', write=True)
        if state['status'] != 'completed':
            record('codex_live_edit', 'BLOCKED', dict(job=job['id'], error=state.get('error')))
            return 2
        test_run = subprocess.run([sys.executable, '-m', 'unittest', '-v'], cwd=edit_dir,
                                  capture_output=True, text=True, timeout=15)
        (directory / 'live-edit-tests.log').write_text(test_run.stdout + test_run.stderr)
        if test_run.returncode or digest(tests) != test_hash:
            raise RuntimeError('Live edit failed its independent acceptance checks')
        record('codex_live_edit_and_tests', 'PASS', job['id'])

        review_dir = directory / 'review'
        review_dir.mkdir()
        source = review_dir / 'review_case.py'
        source.write_text('def ratio(a, b):\n    """Return None when b is zero, otherwise a / b."""\n    return a / b\n')
        before = digest(source)
        client, job, state = execute(client, review_dir,
            'Review review_case.py against its docstring contract; no edits. Report actionable issues with severity '
            'and file:line. If the zero-denominator contract is violated include REVIEW_ZERO_DIVISION; '
            'otherwise REVIEW_OK. Maximum four short lines.', files=['review_case.py'])
        if state['status'] != 'completed':
            record('codex_live_review', 'BLOCKED', dict(job=job['id'], error=state.get('error')))
            return 2
        if 'REVIEW_ZERO_DIVISION' not in state.get('summary', '') or digest(source) != before:
            raise RuntimeError('Review missed the seeded contract defect or modified its input')
        record('codex_live_review', 'PASS', job['id'])

        # Readiness can change during Codex calls. Never load or unload Qwen.
        availability = client.call('cooperation_status')['qwen']
        if availability['available']:
            client, job, state = execute(client, read_dir,
                'Read input.txt and repeat its exact verification-marker, without explanation.',
                target='qwen', files=['input.txt'])
            if state['status'] != 'completed' or marker not in state.get('summary', ''):
                record('qwen_live_read', 'BLOCKED', dict(job=job['id'], error=state.get('error')))
            else:
                record('qwen_live_read', 'PASS', job['id'])
        else:
            record('qwen_live_read', 'SKIP', availability['reason'])
        return 0 if all(c['status'] in ('PASS', 'SKIP') for c in checks) else 2
    except Exception as exc:
        record('verification_error', 'FAIL', str(exc))
        return 1
    finally:
        if client is not None:
            client.close()
        report = '# Host verification\n\n' + '\n'.join(
            f"- {c['status']} — {c['check']}: {c['evidence']}" for c in checks)
        (directory / 'REPORT.md').write_text(report + '\n')
        print('Saved report: ' + str(directory / 'REPORT.md'), flush=True)


if __name__ == '__main__':
    sys.exit(main())
