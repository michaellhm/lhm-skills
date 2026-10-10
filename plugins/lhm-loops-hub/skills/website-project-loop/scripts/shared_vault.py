"""Verified shared Drive Markdown access, with explicit path and content checks."""
import hashlib
import importlib.util
import io
import re
from pathlib import PurePosixPath

DRIVE = '0AF6X3xDBIuVcUk9PVA'


class Vault:
    def __init__(self, config):
        spec = importlib.util.spec_from_file_location('google_api', config['google_api'])
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        self.service = module.build_service('drive', 'v3')
        drive = self.service.drives().get(driveId=DRIVE, fields='id,name').execute()
        if drive != {'id': DRIVE, 'name': 'LHM Knowledge'}:
            raise ValueError('Wrong shared knowledge drive')
        self.files = {}
        token = None; nodes = {}
        while True:
            data = self.service.files().list(q="trashed=false and (mimeType='application/vnd.google-apps.folder' or name contains '.md')", corpora='drive',driveId=DRIVE,supportsAllDrives=True,includeItemsFromAllDrives=True,pageSize=1000,pageToken=token,fields='nextPageToken,incompleteSearch,files(id,name,mimeType,parents,driveId,modifiedTime)').execute()
            if data.get('incompleteSearch'): raise ValueError('Incomplete vault index')
            nodes.update({f['id']:f for f in data.get('files',[])})
            token=data.get('nextPageToken')
            if not token: break
        for node in nodes.values():
            parts=[]; seen=set(); item=node
            while item['id'] != DRIVE:
                if item['id'] in seen: raise ValueError('Vault ancestry cycle')
                seen.add(item['id']); name=item['name']
                if '/' in name or name in ['.','..']: break
                parts.append(name); parents=item.get('parents',[])
                if len(parents)!=1: break
                if parents[0]==DRIVE:
                    path='/'.join(reversed(parts))
                    if path in self.files: raise ValueError('Ambiguous vault path: '+path)
                    self.files[path]=node; break
                if parents[0] not in nodes: break
                item=nodes[parents[0]]

    def read(self, path):
        if path not in self.files or not path.endswith('.md') or '..' in PurePosixPath(path).parts:
            raise ValueError('Missing or invalid canonical file: '+path)
        meta=self.files[path]
        body=self.service.files().get_media(fileId=meta['id'],supportsAllDrives=True).execute()
        if len(body)>2000000: raise ValueError('Oversized canonical note')
        return {'path':path,'id':meta['id'],'text':body.decode('utf-8-sig')}

    def write(self, path, before, after):
        if not (path.startswith('20 Clients/') or path.startswith('30 Projects/LHM Website Loop Sandbox/')):
            raise ValueError('Outside authorised project record area')
        if self.read(path)['text'] != before: raise ValueError('Canonical file changed; re-read before writing')
        from googleapiclient.http import MediaIoBaseUpload
        self.service.files().update(fileId=self.files[path]['id'],supportsAllDrives=True,media_body=MediaIoBaseUpload(io.BytesIO(after.encode()),mimetype='text/markdown',resumable=False)).execute()
        actual=self.read(path)['text']
        if actual!=after: raise ValueError('Shared Obsidian write readback mismatch')
        return hashlib.sha256(actual.encode()).hexdigest()


def complete(vault, path, item, day, evidence, source, actor):
    """Exact production checkbox only; approvals require their separate workflow."""
    from datetime import date
    date.fromisoformat(day)
    if not evidence.startswith('https://') or not source.startswith('https://') or not actor:
        raise ValueError('Completion requires evidence, source and attributed actor')
    before=vault.read(path)['text']; lines=before.splitlines()
    candidates=[]
    for index,line in enumerate(lines):
        if not re.match(r'^\s*- \[[ xX]\]',line): continue
        label=re.sub(r'^\s*- \[[ xX]\]\s*','',line)
        label=re.sub(r'^\(\d{4}-\d{2}-\d{2}\)\s*','',label)
        label=label.split(' — ',1)[0].split(';',1)[0]
        if label==item or re.match(r'^'+re.escape(item)+r'(?:\s|$)',label):candidates.append(index)
    if len(candidates)!=1: raise ValueError('Missing or ambiguous checklist match')
    i=candidates[0]
    if re.search(r'approval|approve|sign.off|launch|publish|deploy|merge',lines[i],re.I):
        raise ValueError('Approval or consequential gate requires its own authority workflow')
    key=hashlib.sha256((source+'\n'+item).encode()).hexdigest()[:20]
    marker='website-completion:'+key
    if marker in before: return {'state':'already_recorded','path':path,'item':lines[i]}
    if re.match(r'^\s*- \[[xX]\]',lines[i]): raise ValueError('Already complete; preserve existing evidence')
    lines[i]=lines[i].replace('[ ]','[x]',1)+f' — completed {day}; reported by {actor}; evidence: {evidence}'
    after='\n'.join(lines)+'\n\n'+f'## Completion reconciliation — {day}\n\n{marker}\nSource: {source}\nRecorded only: {item}. Approval and dependent work remain separate.\n'
    sha=vault.write(path,before,after)
    return {'state':'verified','path':path,'item':lines[i],'sha256':sha,'source':source}
