#!/usr/bin/env python3
"""Deterministic completion worker: verify request, write/read back, reply/read back."""
import fcntl
import html
import json
from pathlib import Path
import lily_shared_mcp as shared
import website_loop as loop


def run():
    root=shared.PROFILE/'workspace/website-loop/completions';incoming=root/'incoming';incoming.mkdir(parents=True,exist_ok=True)
    with (root/'worker.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        for path in sorted(incoming.glob('*.json')):
            data=json.loads(path.read_text());mid=data['source_message_id'];receipt=root/'receipts'/(mid+'.json')
            marker='lily-completion:'+mid
            try:
                cfg=shared.config(data['task_id']);api=loop.BasicOps(cfg);api.identity()
                replies=api.call('list_replies_in_message',{'messageId':mid})
                rows=replies if isinstance(replies,list) else replies.get('data',[])
                if any(marker in r.get('message','') and r.get('userId')==82484 for r in rows):
                    loop.save(receipt,{'state':'verified_already_replied','message_id':mid});path.unlink();continue
                if receipt.exists() and json.loads(receipt.read_text()).get('state')=='posting_reply':
                    path.unlink();continue
                args={k:data[k] for k in ['task_id','item','evidence','source_message_id']}
                if data.get('next_action'):args['next_action']=data['next_action']
                result=shared.operation('record_website_completion',args)
                remaining=''.join('<li>'+html.escape(x)+'</li>' for x in result.get('remaining_checklist',[]))
                message='<p><strong>Website completion verified.</strong> '+html.escape(result['item'])+'</p><p>Shared Obsidian: <a href="'+result['note_url']+'">canonical project record</a>. Saved file read back successfully.</p><p>BasicOps task state unchanged; completing one checklist item does not close the overview.</p><p>Still open:</p><ul>'+remaining+'</ul><p>Next: '+html.escape(data.get('next_action') or 'see the canonical project dependencies; no new commitment selected.')+'</p><p>'+marker+'</p>'
                loop.save(receipt,{'state':'posting_reply','message_id':mid,'write':result})
                api.call('create_reply_in_message',{'messageId':mid,'message':message})
                observed=api.call('list_replies_in_message',{'messageId':mid});rows=observed if isinstance(observed,list) else observed.get('data',[])
                if not any(marker in r.get('message','') and r.get('userId')==82484 for r in rows):raise ValueError('Completion reply readback missing')
                loop.save(receipt,{'state':'verified','message_id':mid,'write':result,'reply_readback':True})
                path.unlink()
            except Exception as error:
                # Preserve partial success and uncertainty; never blindly resend.
                prior=json.loads(receipt.read_text()) if receipt.exists() else {}
                failure=type(error).__name__+': '+str(error)[:300]
                if prior.get('state')!='posting_reply' and 'api' in locals():
                    try:
                        api.call('create_reply_in_message',{'messageId':mid,'message':'<p>Website reconciliation blocked: '+html.escape(failure)+'. No completion claimed. Please resolve the missing mapping/evidence or retry after the failed write is checked.</p><p>lily-completion-blocked:'+mid+'</p>'})
                    except Exception:pass
                loop.save(receipt,dict(prior,state='blocked',message_id=mid,error=failure))
                path.unlink()


if __name__=='__main__':run()
