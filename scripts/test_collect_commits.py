"""Disposable Git integration checks; no user repo changes."""
import os
import subprocess
import tempfile
import unittest
from datetime import date
from pathlib import Path
from collect_commits import TZ, collect, window


class CollectorTests(unittest.TestCase):
    def test_calendar(self):
        start, end = window(date(2026, 10, 23))
        self.assertEqual(start.isoformat(), '2026-10-16T00:00:00+08:00')
        self.assertEqual(end.isoformat(), '2026-10-23T00:00:00+08:00')
        self.assertEqual(window(date(2026, 10, 22))[1].date(), date(2026, 10, 16))
        self.assertEqual(window(date(2027, 1, 1))[0].date(), date(2026, 12, 25))

    def test_git_evidence(self):
        with tempfile.TemporaryDirectory() as folder:
            repo = Path(folder)
            def run(*args, env=None):
                return subprocess.run(['git', '-C', folder, *args], check=True,
                                      capture_output=True, text=True, env=env).stdout.strip()
            run('init', '-b', 'main')
            run('config', 'user.name', 'Test')
            run('config', 'user.email', 'owner@example.test')
            def commit(title, timestamp, email='owner@example.test'):
                (repo / 'file.txt').write_text(title)
                run('add', 'file.txt')
                env = dict(os.environ, GIT_AUTHOR_DATE=timestamp, GIT_COMMITTER_DATE=timestamp,
                           GIT_AUTHOR_EMAIL=email, GIT_COMMITTER_EMAIL=email)
                run('commit', '-m', title, env=env)
                return run('rev-parse', 'HEAD')
            commit('before', '2026-10-15T23:59:59+08:00')
            first = commit('boundary start', '2026-10-15T16:00:00+00:00')
            run('checkout', '-b', 'feature')
            branch = commit('unmerged work', '2026-10-18T12:00:00+08:00')
            run('checkout', 'main')
            run('merge', '--no-ff', 'feature', '-m', 'merge', env=dict(os.environ,
                GIT_AUTHOR_DATE='2026-10-19T12:00:00+08:00',
                GIT_COMMITTER_DATE='2026-10-19T12:00:00+08:00'))
            commit('someone else', '2026-10-20T12:00:00+08:00', 'other@example.test')
            last = commit('last second', '2026-10-22T23:59:59+08:00')
            commit('boundary end', '2026-10-23T00:00:00+08:00')
            run('checkout', '-b', 'unmerged')
            unmerged = commit('branch only', '2026-10-21T12:00:00+08:00')
            run('checkout', 'main')
            start, end = window(date(2026, 10, 23))
            evidence = collect(repo, {'owner@example.test'}, start, end)
            self.assertEqual({c['sha'] for c in evidence}, {first, branch, last, unmerged})
            self.assertEqual(len(evidence), 4)
            self.assertTrue(all(c['files'] == ['file.txt'] for c in evidence))
            self.assertEqual(collect(repo, {'missing@example.test'}, start, end), [])


if __name__ == '__main__':
    unittest.main()
