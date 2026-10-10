#!/usr/bin/env python3
"""Add two bounded shared-record tools to Lily's existing BasicOps proxy."""
import importlib.util
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0,str(Path(__file__).parent))
import website_loop as loop
from shared_vault import Vault, complete

PROFILE=Path('/opt/data/profiles/lhm_project_manager')
spec=importlib.util.spec_from_file_location('existing_basicops_proxy',PROFILE/'basicops_mcp_proxy.py')
base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
PEOPLE={36398:'Michael',36401:'Kristalyn',36402:'Aiya',36403:'Jaimee',63471:'Josephine'}


def config(task):
    cfg=json.loads((PROFILE/'website-loop.json').read_text())
    if str(task) not in cfg['projects']:
        test=json.loads((PROFILE/'website-loop-test.json').read_text())
        if task in test.get('test_task_ids',[]):return test
        api=loop.BasicOps(cfg);api.identity();record=api.call('get_task',{'taskId':task})
        parent=record.get('parentTask',record.get('parent',record.get('parentTaskId')))
        if isinstance(parent,dict):parent=parent.get('id')
        if str(parent) in cfg['projects']:
            cfg['projects'][str(task)]=cfg['projects'][str(parent)];return cfg
        # A personal execution task can also be explicitly linked from the
        # canonical note. Never infer client identity from a title abbreviation.
        matches=[]
        for overview,mapping in list(cfg['projects'].items()):
            if mapping['project'].endswith('/Onboarding.md'):continue
            try: note=loop.context(cfg,overview)['project']['text']
            except ValueError:continue
            if record.get('url') and record['url'] in note:matches.append(mapping)
        unique={x['project']:x for x in matches}
        if len(unique)!=1:raise ValueError('Missing or ambiguous canonical task link; resolve the overview first')
        cfg['projects'][str(task)]=next(iter(unique.values()))
    return cfg


def operation(name,args):
    task=args['task_id'];cfg=config(task);api=loop.BasicOps(cfg);api.identity()
    context=loop.context(cfg,str(task));record=api.call('get_task',{'taskId':task});discussion=loop.discussions(api,task)
    if name=='read_website_project_context':
        return {'task':record,'context':context,'discussion':discussion,'note_url':'https://drive.google.com/file/d/'+context['project']['id']+'/view','authority':'Read only. Completion requires an explicit authenticated team request and its source message.'}
    mid=args['source_message_id'];sources=[x for x in discussion if x.get('id')==mid]
    if len(sources)!=1:raise ValueError('Source request must exist in this task Discussion')
    source=sources[0];actor=source.get('user',source.get('userId'))
    if isinstance(actor,dict):actor=actor.get('id')
    if actor not in PEOPLE:raise ValueError('Source actor is not a verified current LHM team member')
    text=re.sub('<[^>]+>',' ',source.get('message',''))
    if args['item'] not in text or args['evidence'] not in source.get('message','') or not re.search(r'\b(completed?|finished|done)\b',text,re.I) or re.search(r'\b(not|never|not yet)\s+(complete[ds]?|finished|done)\b',text,re.I):
        raise ValueError('Source request does not explicitly support this completion and evidence')
    day=datetime.now(ZoneInfo('Australia/Melbourne')).date().isoformat()
    source_url=record['url']+'#'+mid
    result=complete(loop._VAULT,context['project']['path'],args['item'],day,args['evidence'],source_url,PEOPLE[actor])
    result['note_url']='https://drive.google.com/file/d/'+context['project']['id']+'/view'
    result['remaining_checklist']=[line for line in loop._VAULT.read(context['project']['path'])['text'].splitlines() if re.match(r'^\s*- \[ \]',line)]
    result['basicops_state']='Unchanged; use the owning task manager for any explicitly authorised state change.'
    return result


async def list_tools(ctx,params):
    upstream=await base.list_tools(ctx,params)
    for name,description,properties,required in [
      ('read_website_project_context','Read the actual shared LHM Knowledge profile and canonical website checklist plus task Discussion. Accepts a mapped overview or an execution task explicitly parented/linked to its canonical record; never guesses from titles.',{'task_id':{'type':'integer'}},['task_id']),
      ('record_website_completion','Record one exact production checkbox completion in the actual shared Obsidian note and verify readback. Requires a current team member source request in this task Discussion explicitly naming the item and evidence. Refuses approvals/launch and leaves BasicOps state unchanged.',{'task_id':{'type':'integer'},'item':{'type':'string'},'evidence':{'type':'string'},'source_message_id':{'type':'string'}},['task_id','item','evidence','source_message_id'])]:
        upstream.tools.append(base.types.Tool.model_validate({'name':name,'description':description,'inputSchema':{'type':'object','properties':properties,'required':required,'additionalProperties':False}}))
    return upstream


async def call_tool(ctx,params):
    if params.name not in ['read_website_project_context','record_website_completion']:
        return await base.call_tool(ctx,params)
    try:
        result=await base.anyio.to_thread.run_sync(lambda:operation(params.name,params.arguments or {}))
        return base.types.CallToolResult(content=[base.types.TextContent(type='text',text=json.dumps(result))])
    except Exception as error:
        return base.types.CallToolResult(isError=True,content=[base.types.TextContent(type='text',text=type(error).__name__+': '+str(error)[:300])])


async def main():
    server=base.Server('lily-basicops-shared-projects',on_list_tools=list_tools,on_call_tool=call_tool)
    async with base.stdio_server() as (read,write):
        await server.run(read,write,server.create_initialization_options())


if __name__=='__main__':base.anyio.run(main)
