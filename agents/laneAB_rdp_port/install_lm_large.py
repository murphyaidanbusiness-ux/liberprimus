"""Lane AB: verify RDP's LM-large release archives and install them into the port, without RDP's own installer.

    python -I agents/laneAB_rdp_port/install_lm_large.py [--dry-run] > agents/laneAB_rdp_port/out_install_lm_large.txt

Inputs (already on disk; this script has no network code): the two archives in dl/rdp_downloads/, fetched by curl from
the release named in the port's assets/manifests/assets_manifest_v1.json (release_asset_sets.v1_lm_runtime_full).
1. Each archive's byte size and sha256 must equal the manifest's.
2. Every archive member must be a safe relative path (no absolute path, drive letter, '..' or empty part) that is a
   final_relpath of the manifest's installed_assets; anything else is reported and not extracted.
3. A member is streamed to a temporary file next to its target, checked against the manifest's size and sha256, then
   moved into place. A target that already exists is left alone if it already matches, and reported if it differs.
4. Finally every installed_assets row required for v1_lm_runtime_full is checked on disk by size and sha256.
"""
import argparse
import hashlib
import json
import os
import sys
import zipfile
from pathlib import Path, PurePosixPath

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
ASSETS = ROOT / 'dl' / 'rdp_port' / 'assets'
MANIFEST = ASSETS / 'manifests' / 'assets_manifest_v1.json'
DOWNLOADS = ROOT / 'dl' / 'rdp_downloads'
SET = 'v1_lm_runtime_full'


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for block in iter(lambda: fh.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def safe_rel(name):
    if not name or name.startswith(('/', '\\')) or ':' in name or '\\' in name:
        return None
    p = PurePosixPath(name)
    if any(part in ('', '.', '..') for part in p.parts):
        return None
    return p.as_posix()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true', help='verify archives and list members; extract nothing')
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding='utf-8')
    m = json.load(open(MANIFEST, encoding='utf-8'))
    rows = {r['final_relpath']: r for r in m['installed_assets']}
    need = [r for r in m['installed_assets'] if SET in r.get('required_for', [])]
    arch = m['release_asset_sets'][SET]
    print('manifest %s: %d installed_assets rows, %d required for %s; release %s %s' %
          (MANIFEST.relative_to(ROOT).as_posix(), len(rows), len(need), SET, arch['release_repository'],
           arch['release_tag']))
    ok = True
    for asset in arch['release_assets']:
        p = DOWNLOADS / asset['name']
        if not p.exists():
            print('MISSING archive %s' % p.name)
            ok = False
            continue
        size, sha = p.stat().st_size, sha256_of(p)
        good = size == asset['size_bytes'] and sha == asset['sha256']
        ok &= good
        print('archive %s: %d bytes (manifest %d), sha256 %s (manifest %s): %s' %
              (p.name, size, asset['size_bytes'], sha, asset['sha256'], 'OK' if good else 'MISMATCH'))
    if not ok:
        print('VERDICT: FAIL (archives do not match the manifest); nothing extracted')
        return 2
    extracted = kept = 0
    problems = []
    for asset in arch['release_assets']:
        with zipfile.ZipFile(DOWNLOADS / asset['name']) as z:
            infos = [i for i in z.infolist() if not i.is_dir()]
            print('%s: %d members, %d bytes uncompressed' % (asset['name'], len(infos),
                                                             sum(i.file_size for i in infos)))
            for info in infos:
                rel = safe_rel(info.filename)
                if rel is None:
                    problems.append('unsafe member name %r' % info.filename)
                    continue
                row = rows.get(rel)
                if row is None:
                    problems.append('member not in manifest: %s' % rel)
                    continue
                dest = ASSETS.joinpath(*PurePosixPath(rel).parts)
                if ASSETS.resolve() not in dest.resolve().parents:
                    problems.append('destination escapes the assets root: %s' % rel)
                    continue
                if dest.exists():
                    if dest.stat().st_size == row['size_bytes'] and sha256_of(dest) == row['sha256']:
                        kept += 1
                        if info.file_size != row['size_bytes']:
                            data = z.read(info)
                            same = hashlib.sha256(data.replace(b'\r\n', b'\n')).hexdigest() == row['sha256']
                            print('NOTE %s: archive copy is %d bytes (manifest %d)%s; the bundled file matches the '
                                  'manifest and is kept' % (rel, info.file_size, row['size_bytes'],
                                                            ', identical after CRLF -> LF' if same else ''))
                    else:
                        problems.append('existing file differs, left alone: %s' % rel)
                    continue
                if info.file_size != row['size_bytes']:
                    problems.append('member size %d != manifest %d: %s' % (info.file_size, row['size_bytes'], rel))
                    continue
                if a.dry_run:
                    continue
                dest.parent.mkdir(parents=True, exist_ok=True)
                tmp = dest.with_name(dest.name + '.part')
                h = hashlib.sha256()
                with z.open(info) as src, open(tmp, 'wb') as out:
                    for block in iter(lambda: src.read(1 << 20), b''):
                        h.update(block)
                        out.write(block)
                if h.hexdigest() != row['sha256']:
                    os.remove(tmp)
                    problems.append('sha256 mismatch after extraction, removed: %s' % rel)
                    continue
                os.replace(tmp, dest)
                extracted += 1
    print('extracted %d, already present and matching %d, problems %d' % (extracted, kept, len(problems)))
    for pr in problems:
        print('PROBLEM', pr)
    if a.dry_run:
        print('VERDICT: DRY RUN')
        return 0
    bad = []
    for r in need:
        p = ASSETS.joinpath(*PurePosixPath(r['final_relpath']).parts)
        if not p.exists() or p.stat().st_size != r['size_bytes'] or sha256_of(p) != r['sha256']:
            bad.append(r['final_relpath'])
    print('installed check: %d of %d %s files present with manifest size and sha256' % (len(need) - len(bad), len(need),
                                                                                      SET))
    for b in bad:
        print('BAD', b)
    print('VERDICT: %s' % ('PASS' if not bad and not problems else 'FAIL'))
    return 0 if not bad and not problems else 1


if __name__ == '__main__':
    sys.exit(main())
