#!/usr/bin/env python3
"""
Validates that every plugin's version is consistent between its own
plugin.json and its entry in the top-level marketplace.json, matched by
plugin `name` (never by array position - plugin order in marketplace.json
has changed before and will change again).

Usage:
    scripts/validate-plugin-versions.py                # consistency check only
    scripts/validate-plugin-versions.py --bump-check    # also require a version
                                                         # bump for any plugin whose
                                                         # staged files changed
"""
import json
import re
import subprocess
import sys
from pathlib import Path

FLAGSHIP_PLUGIN = "lhm-marketing-hub"


def repo_root():
    out = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=True
    )
    return Path(out.stdout.strip())


def load_json(path):
    with open(path) as f:
        return json.load(f)


def git_show(rev_path, cwd):
    """Return parsed JSON for `git show <rev_path>`, or None if it doesn't exist."""
    result = subprocess.run(
        ["git", "show", rev_path], capture_output=True, text=True, cwd=cwd
    )
    if result.returncode != 0:
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return None


def main():
    bump_check = "--bump-check" in sys.argv
    root = repo_root()
    errors = []

    marketplace_path = root / ".claude-plugin" / "marketplace.json"
    marketplace = load_json(marketplace_path)
    marketplace_versions = {p["name"]: p["version"] for p in marketplace["plugins"]}
    marketplace_metadata_version = marketplace["metadata"]["version"]

    plugin_versions = {}
    plugin_paths = {}
    for plugin_json_path in sorted(root.glob("plugins/*/.claude-plugin/plugin.json")):
        data = load_json(plugin_json_path)
        name = data["name"]
        plugin_versions[name] = data["version"]
        plugin_paths[name] = plugin_json_path

    # 1. Every plugin.json must have a matching marketplace entry with the same version.
    for name, version in plugin_versions.items():
        if name not in marketplace_versions:
            errors.append(
                f"'{name}' has plugins/{name}/.claude-plugin/plugin.json (version {version}) "
                f"but no entry in .claude-plugin/marketplace.json."
            )
        elif marketplace_versions[name] != version:
            errors.append(
                f"Version mismatch for '{name}': plugin.json={version}, "
                f"marketplace.json entry={marketplace_versions[name]}. "
                f"Find the marketplace.json entry with \"name\": \"{name}\" (match by name, "
                f"not array position) and set its version to {version}."
            )

    # 2. Every marketplace entry must have a matching plugin.json.
    for name in marketplace_versions:
        if name not in plugin_versions:
            errors.append(
                f"marketplace.json references plugin '{name}' but "
                f"plugins/{name}/.claude-plugin/plugin.json was not found."
            )

    # 3. marketplace.json top-level metadata.version tracks the flagship plugin.
    if FLAGSHIP_PLUGIN in plugin_versions:
        flagship_version = plugin_versions[FLAGSHIP_PLUGIN]
        if marketplace_metadata_version != flagship_version:
            errors.append(
                f"marketplace.json metadata.version ({marketplace_metadata_version}) does not "
                f"match {FLAGSHIP_PLUGIN}'s plugin.json version ({flagship_version}). "
                f"metadata.version tracks {FLAGSHIP_PLUGIN} as the flagship plugin."
            )

    # 4. Optional: require a version bump for any plugin whose staged files changed.
    if bump_check:
        diff = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
            capture_output=True, text=True, cwd=root, check=True,
        )
        staged_files = [line for line in diff.stdout.splitlines() if line.strip()]

        changed_by_plugin = {}
        for f in staged_files:
            m = re.match(r"^plugins/([^/]+)/", f)
            if not m:
                continue
            name = m.group(1)
            if f.endswith("LEARNED.md"):
                continue
            changed_by_plugin.setdefault(name, []).append(f)

        for name, files in changed_by_plugin.items():
            plugin_json_rel = f"plugins/{name}/.claude-plugin/plugin.json"
            head_data = git_show(f"HEAD:{plugin_json_rel}", cwd=root)
            if head_data is None:
                # New plugin being introduced in this commit - nothing to compare against.
                continue
            staged_data = git_show(f":{plugin_json_rel}", cwd=root)
            staged_version = staged_data["version"] if staged_data else plugin_versions.get(name)
            if staged_version == head_data["version"]:
                other_files = [f for f in files if f != plugin_json_rel]
                if other_files:
                    errors.append(
                        f"'{name}' has staged changes ({', '.join(other_files[:5])}"
                        f"{', ...' if len(other_files) > 5 else ''}) but its version is still "
                        f"{head_data['version']}. Bump the patch version in {plugin_json_rel} "
                        f"and its matching marketplace.json entry."
                    )

    if errors:
        print("Plugin version validation failed:\n", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        print(
            "\nSee the Pre-Push Checklist in CLAUDE.md, or run "
            "`python3 scripts/validate-plugin-versions.py` after fixing.",
            file=sys.stderr,
        )
        return 1

    print("Plugin versions OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
