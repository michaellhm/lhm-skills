#!/usr/bin/env python3
"""Prepare a fail-closed, idempotent patch for the deployed TED router.

Usage: patch_ted_scoped_approval.py INPUT_ROUTER OUTPUT_ROUTER
Copy assets/task-router/scoped_approval.py beside the deployed router as well.
This command never deploys or submits work.
"""
import ast
from pathlib import Path
import sys


def patch(source):
    if 'from scoped_approval import admission_text' in source:
        if 'admission = admission_text(instruction, explicit_provider(instruction))' not in source:
            raise ValueError('Unexpected partial repair; inspect instead of overwriting')
        return source
    start = source.index("        if feedback is None and (not msg or actor(msg) != self.config['reviewer_id']")
    end = source.index("        if task.get('status')", start)
    block = source[start:end]
    if (block.count('instruction, re.I') != 4
            or block.count('explicit_provider(instruction)') != 1
            or 'A direct personal work request is required' not in block):
        raise ValueError('Router admission changed; inspect instead of overwriting')
    projection = '        admission = admission_text(instruction, explicit_provider(instruction)) if feedback is None else instruction\n'
    revised = block.replace('instruction, re.I', 'admission, re.I').replace('explicit_provider(instruction)', 'explicit_provider(admission)')
    revised = revised.replace("re.search(r'AI authorship\\s*:', admission, re.I)", "re.search(r'AI authorship\\s*:', instruction, re.I)")
    result = source[:start] + projection + revised + source[end:]
    result = result.replace('import fcntl\n', 'import fcntl\nfrom scoped_approval import admission_text\n', 1)
    ast.parse(result)
    return result


if __name__ == '__main__':
    Path(sys.argv[2]).write_text(patch(Path(sys.argv[1]).read_text()))
