#!/usr/bin/env python3
"""Read local Git evidence for a Friday–Thursday report without modifying repos."""
import argparse
import json
import subprocess
from datetime import date, datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

TZ = ZoneInfo('Asia/Kuala_Lumpur')
CONFIG = Path(__file__).resolve().parents[1] / 'projects.json'


def window(day):
    end = datetime.combine(day - timedelta(days=(day.weekday() - 4) % 7), time.min, TZ)
    return end - timedelta(days=7), end


def git(repo, *args):
    return subprocess.run(['git', '-C', str(repo), *args], check=True,
                          capture_output=True, text=True).stdout


def collect(repo, emails, start, end):
    # Filter epochs ourselves because Git date pruning can miss out-of-order dates.
    raw = git(repo, 'log', '--all', 'HEAD', '--no-merges',
              '--format=%H%x00%ct%x00%ae%x00%aI%x00%s')
    commits = []
    for line in raw.splitlines():
        sha, stamp, email, authored, subject = line.split('\0', 4)
        if email.lower() not in emails or not start.timestamp() <= int(stamp) < end.timestamp():
            continue
        commits.append({'sha': sha, 'author_email': email, 'authored_at': authored,
                        'committed_at': datetime.fromtimestamp(int(stamp), TZ).isoformat(),
                        'subject': subject,
                        'files': git(repo, 'diff-tree', '--root', '--no-commit-id',
                                     '--name-only', '-r', sha).splitlines()})
    return sorted(commits, key=lambda c: (c['committed_at'], c['sha']))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report-date', type=date.fromisoformat,
                        default=datetime.now(TZ).date(), help='Use this Friday, YYYY-MM-DD, or latest Friday by default')
    parser.add_argument('--project', help='Exact configured project name')
    args = parser.parse_args()
    config = json.loads(CONFIG.read_text())
    projects = config['projects']
    if args.project:
        projects = [p for p in projects if p['name'].lower() == args.project.lower()]
        if not projects:
            parser.error('Unknown project')
    start, end = window(args.report_date)
    output = {'timezone': str(TZ), 'start_inclusive': start.isoformat(),
              'end_exclusive': end.isoformat(), 'week_start': start.date().isoformat(),
              'week_end': (end.date() - timedelta(days=1)).isoformat(),
              'date_basis': 'committer timestamp; author email ownership',
              'scope': 'all locally available refs plus HEAD; no fetch',
              'period_complete': datetime.now(TZ) >= end, 'projects': [], 'errors': []}
    emails = {e.lower() for e in config['author_emails']}
    for project in projects:
        result = {'name': project['name'], 'repos': []}
        for entry in project['repos']:
            repo = Path(entry['path']).expanduser()
            try:
                commits = collect(repo, emails, start, end)
                result['repos'].append({'role': entry['role'], 'path': str(repo), 'commits': commits})
            except (subprocess.CalledProcessError, OSError) as exc:
                output['errors'].append({'project': project['name'], 'repo': str(repo),
                                         'error': getattr(exc, 'stderr', '') or str(exc)})
        output['projects'].append(result)
    print(json.dumps(output, indent=2))
    return 1 if output['errors'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
