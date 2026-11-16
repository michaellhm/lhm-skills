#!/usr/bin/env python3
"""Run inside the existing Hermes container; calendar reads only, no model."""
import json
import os
import sys


FIELDS = ('id', 'summary', 'start', 'end', 'attendees', 'organizer', 'htmlLink',
          'status', 'visibility', 'eventType', 'recurringEventId', 'originalStartTime')


def execute(request):
    if request.get('action') not in {'identity', 'list', 'get'}:
        raise ValueError('Unsupported calendar operation')
    os.environ['HERMES_HOME'] = '/opt/data/.hermes'
    sys.path.insert(0, '/opt/data/skills/productivity/google-workspace/scripts')
    import google_api
    service = google_api.build_service('calendar', 'v3')
    calendar = request['calendar_id']
    if request['action'] == 'identity':
        return {'identity': service.calendars().get(calendarId=calendar).execute()['id']}
    if request['action'] == 'get':
        event = service.events().get(calendarId=calendar, eventId=request['event_id']).execute()
        return {k: event[k] for k in FIELDS if k in event}
    events, token = [], None
    for _ in range(40):
        result = service.events().list(calendarId=calendar, timeMin=request['start'],
            timeMax=request['end'], singleEvents=True, orderBy='startTime',
            maxResults=250, pageToken=token).execute()
        events.extend({k: e[k] for k in FIELDS if k in e} for e in result.get('items', []))
        token = result.get('nextPageToken')
        if not token:
            return {'events': events, 'pagination_complete': True}
    raise RuntimeError('Calendar pagination limit reached')


if __name__ == '__main__':
    try:
        print(json.dumps(execute(json.load(sys.stdin))))
    except Exception as exc:
        print(json.dumps({'error_type': type(exc).__name__}), file=sys.stderr)
        sys.exit(1)
