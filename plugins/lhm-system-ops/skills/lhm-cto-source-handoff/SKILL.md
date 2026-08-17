---
name: lhm-cto-source-handoff
description: Recover typed source capability blockers through work-control.
---
# CTO source handoff
The host runtime invokes the existing CTO/work-control route. Repair the named capability without changing the parent outcome. After verified restoration, emit one exact `capability_restored` event carrying incident, parent, saved role and return point. Do not treat publication, installation or an unrelated read as restoration.
