"""Read and write the last-processed cursor in brain/Change Log.md.

The cursor is a single HTML comment, `<!-- last-processed: <sha|none> -->`.
`none`, or no marker at all, means the brain has not learned from any commit yet.
"""
import re
import sys
from pathlib import Path

MARKER = re.compile(r"<!--\s*last-processed:\s*(\S+?)\s*-->")


def last_processed(changelog_text):
    """Return the SHA in the final marker, or None for `none` or no marker."""
    found = MARKER.findall(changelog_text)
    if not found or found[-1].lower() == "none":
        return None
    return found[-1]


def set_marker(changelog_text, sha):
    """Return the text with exactly one marker, holding sha, at the end."""
    sha = sha.strip()
    if not sha or any(c.isspace() for c in sha) or "-->" in sha:
        raise ValueError("sha must be a single token")
    marker = f"<!-- last-processed: {sha} -->"
    if MARKER.search(changelog_text):
        parts = MARKER.split(changelog_text)
        # re.split with one group alternates text, captured sha, text ...; rebuild text only.
        text = "".join(parts[0::2])
        text = text.rstrip("\n")
        return text + "\n\n" + marker + "\n"
    return changelog_text.rstrip("\n") + "\n\n" + marker + "\n"


def main(argv):
    if len(argv) not in (2, 3):
        print("usage: brain_cursor.py 'Change Log.md' [new-sha]", file=sys.stderr)
        return 2
    path = Path(argv[1])
    text = path.read_text()
    if len(argv) == 2:
        print(last_processed(text) or "none")
        return 0
    path.write_text(set_marker(text, argv[2]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
