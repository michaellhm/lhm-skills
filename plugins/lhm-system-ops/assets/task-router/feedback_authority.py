"""Optional registered prototype feedback authority; never impersonates a human.

The host operator owns this closed registry. Email text and BasicOps authors cannot
create grants. An admitted request keeps its scope when its cockpit leaves the
feedback stage; new admissions always require a fresh live stage read.
"""
import hashlib
import json
import os
import re
import stat
from pathlib import Path

AUTHORITY = 'MICHAEL-PROTOTYPE-FEEDBACK-20261107'
FIELDS = {'authority_id', 'task_id', 'instruction_message_id', 'instruction_sha256',
          'cockpit_id', 'stage_id', 'client_id', 'batch_id', 'author_id', 'reviewer_id',
          'repository', 'subtree', 'enabled'}
MAX_BYTES = 262144


def actor(value):
    user = value.get('user', value.get('userId', value.get('assignee')))
    return user.get('id') if isinstance(user, dict) else user


def fingerprint(grant):
    return hashlib.sha256(json.dumps(grant, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def read_registry(profile):
    path = Path(profile) / 'config/prototype-feedback-authority.json'
    try:
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    except FileNotFoundError:
        return None
    with os.fdopen(fd, 'rb') as stream:
        info = os.fstat(stream.fileno())
        if (info.st_uid != 0 or not stat.S_ISREG(info.st_mode)
                or info.st_mode & 0o022 or info.st_size > MAX_BYTES):
            raise ValueError('Feedback authority registry is not a protected root-owned file')
        value = json.loads(stream.read(MAX_BYTES + 1))
    if not isinstance(value, dict) or set(value) != {'schema_version', 'grants'} or value['schema_version'] != 1 or not isinstance(value['grants'], dict):
        raise ValueError('Malformed feedback authority registry')
    return value['grants']


def validate(grant, task_id):
    if not isinstance(grant, dict) or set(grant) != FIELDS:
        raise ValueError('Malformed feedback authority grant')
    for field in ('task_id', 'cockpit_id', 'stage_id', 'author_id', 'reviewer_id'):
        if type(grant[field]) is not int or grant[field] <= 0:
            raise ValueError('Invalid feedback authority identity')
    if (grant['task_id'] != task_id or grant['cockpit_id'] == task_id
            or grant['stage_id'] != 110340 or grant['author_id'] != 82491
            or grant['reviewer_id'] != 36398 or grant['authority_id'] != AUTHORITY
            or grant['repository'] != 'michaellhm/lhm-prototype'
            or type(grant['enabled']) is not bool or not grant['enabled']):
        raise ValueError('Feedback authority does not match approved scope')
    for field, pattern in (
        ('instruction_message_id', r'dm[1-9][0-9]*'),
        ('instruction_sha256', r'[a-f0-9]{64}'),
        ('client_id', r'[a-z0-9]+(?:-[a-z0-9]+)*'),
        ('batch_id', r'prototype-[a-f0-9]{32}'),
        ('subtree', r'luminary-counselling/')):
        if not isinstance(grant[field], str) or not re.fullmatch(pattern, grant[field]):
            raise ValueError('Invalid feedback authority ' + field)


def verify(profile, api, task, message, *, admitted_request=None):
    """Return a bound grant or None for the unchanged ordinary human route.

    admitted_request is the exact saved request whose host admission receipt has
    already been verified by the caller, never merely a queued state or email flag.
    The caller must also compare the resolved canonical client_id to this grant.
    """
    registry = read_registry(profile)
    if registry is None:
        return None
    task_id = task.get('id')
    grant = registry.get(str(task_id))
    if grant is None:
        return None
    validate(grant, task_id)
    if (not isinstance(message, dict) or message.get('id') != grant['instruction_message_id']
            or actor(message) != grant['author_id']
            or not isinstance(message.get('message'), str)
            or hashlib.sha256(message['message'].encode()).hexdigest() != grant['instruction_sha256']):
        raise ValueError('Feedback instruction differs from root-bound AI instruction')
    if api('get_current_user', {}).get('id') != grant['author_id']:
        raise ValueError('Feedback connector is not verified Ted')
    if not task.get('url', '').startswith('https://app.basicops.com/'):
        raise ValueError('Invalid feedback task URL')
    binding = {'authority_id': grant['authority_id'], 'grant_sha256': fingerprint(grant),
               'batch_id': grant['batch_id'], 'client_id': grant['client_id'],
               'repository': grant['repository'], 'subtree': grant['subtree']}
    if admitted_request is not None:
        if (not isinstance(admitted_request, dict)
                or admitted_request.get('task_id') != task_id
                or admitted_request.get('instruction_message_id') != grant['instruction_message_id']
                or admitted_request.get('instruction_sha256') != grant['instruction_sha256']
                or admitted_request.get('feedback_authority') != binding):
            raise ValueError('Admitted request does not match feedback authority')
        return binding
    if actor(task) != grant['author_id'] or task.get('status') != 'In Progress' or task.get('archived'):
        raise ValueError('Ted must own the active feedback execution task')
    cockpit = api('get_task', {'taskId': grant['cockpit_id']})
    if (cockpit.get('id') != grant['cockpit_id'] or cockpit.get('project', {}).get('id') != 68635
            or cockpit.get('section', {}).get('id') != grant['stage_id']
            or cockpit.get('archived') or cockpit.get('status') in ('Complete', 'Cancelled', 'Decline')):
        raise ValueError('Prototype cockpit is no longer eligible for new dispatch')
    return binding
