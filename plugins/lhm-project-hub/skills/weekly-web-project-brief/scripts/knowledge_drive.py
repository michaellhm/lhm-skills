#!/usr/bin/env python3
"""Read the verified shared LHM Knowledge vault through existing Hermes Google auth."""
import importlib.util,json,sys
from datetime import datetime,timezone
DRIVE='0AF6X3xDBIuVcUk9PVA'
ROOTS={'20 Clients','50 Meetings'}
def paths_from_files(files):
    by_id={f['id']:f for f in files};result={}
    for f in files:
        parts=[];node=f;seen=set()
        while node['id']!=DRIVE:
            if node['id'] in seen:raise ValueError('Drive ancestry cycle')
            seen.add(node['id']);name=node['name']
            if '/' in name or name in ('.','..'):break
            parts.append(name);parents=node.get('parents',[])
            if len(parents)!=1:break
            parent=parents[0]
            if parent==DRIVE:
                path='/'.join(reversed(parts))
                if parts[-1] in ROOTS:
                    if path in result:raise ValueError('Ambiguous knowledge path: '+path)
                    result[path]=f
                break
            if parent not in by_id:break
            node=by_id[parent]
    return result

def main():
    spec=importlib.util.spec_from_file_location('existing_google','/opt/data/skills/productivity/google-workspace/scripts/google_api.py');g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
    service=g.build_service('drive','v3')
    drive=service.drives().get(driveId=DRIVE,fields='id,name').execute()
    if drive!={'id':DRIVE,'name':'LHM Knowledge'}:raise ValueError('Wrong shared knowledge drive')
    action=sys.argv[1]
    if action=='index':
        files=[];token=None
        while True:
            data=service.files().list(q="trashed=false and (mimeType='application/vnd.google-apps.folder' or name contains '.md')",corpora='drive',driveId=DRIVE,supportsAllDrives=True,includeItemsFromAllDrives=True,pageSize=1000,pageToken=token,fields='nextPageToken,incompleteSearch,files(id,name,mimeType,parents,driveId,modifiedTime,size)').execute()
            if data.get('incompleteSearch'):raise ValueError('Incomplete knowledge index')
            files.extend(data.get('files',[]));token=data.get('nextPageToken')
            if not token:break
        value={'drive_id':DRIVE,'drive_name':drive['name'],'terminal':True,'files':paths_from_files(files)}
    elif action=='read':
        file_id=sys.argv[2];meta=service.files().get(fileId=file_id,supportsAllDrives=True,fields='id,name,mimeType,driveId,modifiedTime,size').execute()
        if meta.get('driveId')!=DRIVE or not meta['name'].endswith('.md') or meta.get('mimeType','').startswith('application/vnd.google-apps.') or int(meta.get('size','2000001'))>2000000:raise ValueError('Shared Markdown source required')
        body=service.files().get_media(fileId=file_id,supportsAllDrives=True).execute()
        if len(body)>2000000:raise ValueError('Oversized knowledge file')
        value={'metadata':meta,'text':body.decode('utf-8-sig')}
    else:raise ValueError('Read-only action required')
    value['read_at']=datetime.now(timezone.utc).isoformat();print(json.dumps(value))
if __name__=='__main__':main()
