import argparse,json,os
from pathlib import Path
from .departmental_state import seal_ed25519
from .department_snapshot import verify_dispatch
from .department_final_producers import projection
from .secureio import read_trusted,trusted_key_copy
def main():
 p=argparse.ArgumentParser();p.add_argument("request",type=Path);p.add_argument("output",type=Path);p.add_argument("--observations",type=Path,default=Path("/var/lib/lhm-workflow/department-observations"));p.add_argument("--dispatch-public",type=Path,default=Path("/var/lib/lhm-workflow/public/controller-dispatch.public.pem"));p.add_argument("--adapter-public",type=Path,default=Path("/var/lib/lhm-workflow/public/adapter.public.pem"));p.add_argument("--private-key",type=Path,default=Path("/var/lib/lhm-workflow/secrets/projection.private.pem"));p.add_argument("--trusted-observation-uid",type=int,default=0);a=p.parse_args();r=json.loads(read_trusted(a.request,root=a.request.parent,uid=os.getuid()))
 with trusted_key_copy(a.dispatch_public,uid=0) as dispatch_public,trusted_key_copy(a.adapter_public,uid=0) as adapter_public,trusted_key_copy(a.private_key,uid=0) as private_key:
  snap=verify_dispatch(r,"projection",dispatch_public);state=snap["state_record"];action=next(x for x in state["action_register"] if x["status"]=="lead_accepted");stem=f'{state["parent_run_id"]}-{action["action_id"]}-v{action["version"]}';basic_path=a.observations/"basicops"/f"{stem}.json";tracker_path=a.observations/"tracker"/f"{stem}.json";basic=json.loads(read_trusted(basic_path,root=a.observations,uid=a.trusted_observation_uid));tracker=json.loads(read_trusted(tracker_path,root=a.observations,uid=a.trusted_observation_uid));receipt=projection(state,basic,tracker,adapter_public,private_key);result=seal_ed25519({"role":"projection_producer","snapshot_sha256":r["snapshot_sha256"],"receipt":receipt},private_key)
 a.output.parent.mkdir(parents=True,exist_ok=True);tmp=a.output.with_name(f".{a.output.name}.{os.getpid()}.tmp");tmp.write_text(json.dumps(result,sort_keys=True,separators=(",",":"))+"\n");os.chmod(tmp,0o640);os.replace(tmp,a.output);a.request.unlink()
if __name__=="__main__":main()
