#!/usr/bin/env python3
"""Read one Gmail message through the existing helper, including nested MIME parts."""
import argparse
import base64
import runpy
import types


def extract_message_body(message):
    found = []
    def walk(part):
        body = part.get('body', {}).get('data')
        mime = part.get('mimeType')
        # Attachments are not correspondence bodies.
        if not part.get('filename') and mime in ('text/plain', 'text/html') and body:
            decoded = base64.urlsafe_b64decode(body + '=' * (-len(body) % 4))
            found.append((mime, decoded.decode('utf-8', 'replace')))
        if not part.get('filename'):
            for child in part.get('parts', []):
                walk(child)
    walk(message.get('payload', {}))
    plain = [text for mime, text in found if mime == 'text/plain']
    return '\n'.join(plain or [text for _, text in found])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('message_id')
    parser.add_argument('--helper', default='/opt/data/skills/productivity/google-workspace/scripts/google_api.py')
    args = parser.parse_args()
    if not args.message_id or any(c not in '0123456789abcdef' for c in args.message_id):
        parser.error('Expected a Gmail message ID')
    helper = runpy.run_path(args.helper)
    # Reuse existing auth/read function in this process; do not modify its installation.
    helper['gmail_get'].__globals__['_extract_message_body'] = extract_message_body
    helper['gmail_get'](types.SimpleNamespace(message_id=args.message_id))


if __name__ == '__main__':
    main()
