#!/usr/bin/env python3
"""Native Hermes cheap pre-agent gate; install this wrapper in profile scripts."""
import os
os.execv('/opt/data/.venv/bin/python', ['/opt/data/.venv/bin/python', '/opt/data/profiles/lhm_brain/skills/weekly-web-project-brief/scripts/brief.py', 'gate'])
