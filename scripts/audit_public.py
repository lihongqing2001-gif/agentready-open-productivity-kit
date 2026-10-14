"""Conservative public-tree/history scan; never prints matched values."""
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATTERNS = [
    rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY',
    rb'gh[pousr]_[A-Za-z0-9]{20,}',
    rb'sk-(?:proj-)?[A-Za-z0-9_-]{24,}',
    rb'AKIA[A-Z0-9]{16}',
    rb'(?:/' + rb'Users/|/' + rb'Volumes/)[^\s]+',
]
PRIVATE = {'.env', 'auth.json', 'CODEX_OVERNIGHT.md', 'HERMES_TRIAL_OVERNIGHT.md'}


def inspect(name, data):
    if Path(name).name in PRIVATE or any(part in {'.reports', '.user', 'private'} for part in Path(name).parts):
        raise ValueError('Private path in publication: ' + name)
    if any(re.search(pattern, data) for pattern in PATTERNS):
        raise ValueError('Sensitive pattern in publication: ' + name + ' (value suppressed)')


def main():
    names = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0')
    count = 0
    for name in filter(None, names):
        p = ROOT / name
        if p.is_symlink():
            raise ValueError('Symlink requires review: ' + name)
        inspect(name, p.read_bytes())
        count += 1
    blobs = subprocess.check_output(['git', 'rev-list', '--objects', '--all'], cwd=ROOT).decode().splitlines()
    for line in blobs:
        oid, _, name = line.partition(' ')
        if name and subprocess.check_output(['git', 'cat-file', '-t', oid], cwd=ROOT).strip() == b'blob':
            inspect(name, subprocess.check_output(['git', 'cat-file', '-p', oid], cwd=ROOT))
    print('Public tree/history audit passed:', count, 'tracked files; no matched patterns. Manual review still required.')


if __name__ == '__main__':
    main()
