#!/usr/bin/env python3
"""Update an already-installed scoped Ads digest; preserve jobs and delivery state."""
import hashlib
import json
import os
import re
import shutil
import sys
from pathlib import Path


def install(release, commit, previous):
    assert all(re.fullmatch(r'[0-9a-f]{40}', value) for value in (commit, previous))
    release = Path(release).resolve()
    assert release == Path('/srv/lhm-ads-digest-releases') / commit
    source = release / 'plugins/lhm-marketing-hub/skills/google-ads-monthly-review'
    brain = Path('/home/hermes/.hermes/profiles/lhm_brain')
    registry = json.loads(Path('/home/claudeworker/.claude/plugins/installed_plugins.json').read_text())
    plugin = registry['plugins']['lhm-marketing-hub@lhm-marketing-skills'][0]
    skill_link = Path(plugin['installPath']) / 'skills/google-ads-monthly-review'
    digest_link = brain / 'scripts/ads-weekly-digest'
    assert skill_link.is_symlink() and digest_link.is_symlink()
    assert skill_link.resolve() == Path('/srv/lhm-ads-digest-releases') / previous / 'plugins/lhm-marketing-hub/skills/google-ads-monthly-review'
    assert digest_link.resolve() == brain / 'skill-releases/ads-weekly-digest' / previous
    backup = release / 'update-receipt.json'
    assert not backup.exists(), 'Inspect existing update before retrying'
    prior = {str(p): os.readlink(p) for p in (skill_link, digest_link)}
    dest = brain / 'skill-releases/ads-weekly-digest' / commit
    assert not dest.exists()
    shutil.copytree(source / 'scripts', dest, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    shutil.copy2(source / 'references/monday-digest.md', dest / 'monday-digest.md')
    record = {'commit': commit, 'previous_commit': previous, 'prior_links': prior,
              'state': 'prepared', 'jobs_and_receipts_unchanged': True}
    backup.write_text(json.dumps(record, indent=2) + '\n')
    try:
        for link, target in [(skill_link, str(source)),
                             (digest_link, '../skill-releases/ads-weekly-digest/' + commit)]:
            temp = link.with_name(link.name + '.update-' + commit[:12])
            temp.symlink_to(target, target_is_directory=True)
            os.replace(temp, link)
        hashes = {}
        for name in ['ads-weekly-digest.py', 'render_digest.py']:
            got = hashlib.sha256((digest_link / name).read_bytes()).hexdigest()
            assert got == hashlib.sha256((source / 'scripts' / name).read_bytes()).hexdigest()
            hashes[name] = got
        assert (skill_link / 'SKILL.md').read_bytes() == (source / 'SKILL.md').read_bytes()
        record.update(state='installed', hashes=hashes)
    except Exception:
        for name, target in prior.items():
            link = Path(name); temp = link.with_name(link.name + '.rollback-' + commit[:12])
            temp.symlink_to(target, target_is_directory=True); os.replace(temp, link)
        record['state'] = 'rolled_back'
        backup.write_text(json.dumps(record, indent=2) + '\n')
        raise
    backup.write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps(record))


if __name__ == '__main__':
    install(*sys.argv[1:])
