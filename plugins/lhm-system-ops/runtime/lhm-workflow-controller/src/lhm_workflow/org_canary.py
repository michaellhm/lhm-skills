"""Restartable root orchestration for the isolated weekly SEO canary."""
from __future__ import annotations
import hashlib,hmac,json,os,re,subprocess,tempfile,time
from pathlib import Path
from .host_bridge import BridgeRoots,process_manifest
from .org_routing import ROLE_POLICY,Router,canonical,digest,receipt,seal
from .tracker_connector import TrackerConnector,sha,summary_from_parent

DEFAULT_ROOT=Path("/var/lib/lhm-workflow-canary")
KEY_NAMES=sorted({value[0] for value in ROLE_POLICY.values()})
SUPERVISOR=Path("/opt/lhm-workflow/current/integration/lhm_claude_trusted_supervisor.py")
HOOK=Path("/opt/lhm-workflow/current/integration/hermes_workflow_hook.py")
ROLE_ADAPTER=Path("/opt/lhm-workflow/current/integration/lhm-org-role-adapter")
TRACKER_ADAPTER=Path("/opt/lhm-workflow/current/integration/lhm-seo-tracker-adapter")

def atomic(path:Path,value):
    path.parent.mkdir(parents=True,exist_ok=True); fd,tmp=tempfile.mkstemp(dir=path.parent,prefix=f".{path.name}.")
    try:
        with os.fdopen(fd,"wb") as f: f.write(canonical(value)+b"\n"); f.flush(); os.fsync(f.fileno())
        os.chmod(tmp,0o600); os.replace(tmp,path)
    finally: Path(tmp).unlink(missing_ok=True)

def load_keys(root:Path,test=False):
    result={}
    for role in KEY_NAMES:
        path=root/"keys"/f"{role}.public.pem"; st=path.stat(follow_symlinks=False)
        expected=os.getuid() if test else 0
        if path.is_symlink() or st.st_uid!=expected or st.st_mode&0o077: raise ValueError(f"unsafe role key: {role}")
        if len(path.read_bytes())<32: raise ValueError(f"short role key: {role}")
        result[role]=path
    return result

class Canary:
    def __init__(self,root:Path,keys,research=None,content=None,role_adapter=ROLE_ADAPTER,tracker_adapter=TRACKER_ADAPTER,trusted_internal=False):
        self.root=root; self.keys=keys; self.router=Router(root/"router",keys); self.research=research or self._research_request
        self.content=content; self.artifacts=root/"artifacts"; self.tracker=TrackerConnector(root/"vault"); self.role_adapter=role_adapter; self.tracker_adapter=tracker_adapter; self.trusted_internal=trusted_internal
    def _research_request(self,parent,contract,config):
        request_id=digest(contract); request=self.root/"research-requests"/f"{request_id}.json"; result=self.root/"research-results"/f"{request_id}.json"
        atomic(request,{"parent":parent,"contract":contract,"config":config}); deadline=time.monotonic()+900
        while time.monotonic()<deadline:
            if result.exists():
                value=json.loads(result.read_text()); return value["artifact"],Path(value["path"])
            time.sleep(.25)
        raise TimeoutError("isolated Research service unavailable")
    def _signed(self,contract,outputs,checks,decision=None):
        if self.trusted_internal:
            key=self.keys.get(contract["owner"])
            if not isinstance(key,bytes) or len(key)<32: raise ValueError("trusted controller attestation key unavailable")
            return seal(receipt(contract,outputs=outputs,checks=checks,decision=decision),key)
        envelope={"contract":contract,"outputs":outputs,"checks":checks,"decision":decision}
        if os.environ.get("LHM_WORKFLOW_TEST_MODE")=="1":
            private=self.root/"keys"/f"{contract['owner']}.private.pem"; command=[str(self.role_adapter),contract["owner"],str(private)]
            if contract["runtime"]=="verifier": command += ["--verifier","--registry",str(self.root/"artifact-registry.json")]
            done=subprocess.run(command,input=json.dumps(envelope),text=True,capture_output=True,check=True,env={**os.environ,"LHM_WORKFLOW_CANARY_MODE":"1"}); return json.loads(done.stdout)
        request_id=digest({"contract":digest(contract),"envelope":envelope}); request=self.root/"sign-requests"/contract["owner"]/f"{request_id}.json"; result=self.root/"sign-results"/contract["owner"]/f"{request_id}.json"
        atomic(request,envelope); deadline=time.monotonic()+30
        while time.monotonic()<deadline:
            if result.exists(): return json.loads(result.read_text())
            time.sleep(.1)
        raise TimeoutError(f"isolated signer unavailable: {contract['owner']}")
    def _artifact(self,parent,stage,payload):
        raw=canonical(payload)+b"\n"; path=self.artifacts/parent/f"{stage}.json"; path.parent.mkdir(parents=True,exist_ok=True)
        if path.exists() and path.read_bytes()!=raw: raise ValueError("conflicting canary artifact")
        if not path.exists(): path.write_bytes(raw); path.chmod(0o600)
        artifact={"artifact_id":f"{parent}:{stage}","sha256":hashlib.sha256(raw).hexdigest(),"media_type":"application/json"}; self._register(artifact,path); return artifact
    def _register(self,artifact,path):
        registry_path=self.root/"artifact-registry.json"; registry=json.loads(registry_path.read_text()) if registry_path.exists() else {}
        record={"path":str(path),"sha256":artifact["sha256"]}; old=registry.get(artifact["artifact_id"])
        if old is not None and old!=record: raise ValueError("conflicting artifact registry")
        registry[artifact["artifact_id"]]=record; atomic(registry_path,registry)
    def _verify(self,inputs):
        registry=json.loads((self.root/"artifact-registry.json").read_text())
        for artifact in inputs:
            record=registry.get(artifact["artifact_id"])
            if not record or record["sha256"]!=artifact["sha256"]: raise ValueError("verifier registry mismatch")
            raw=Path(record["path"]).read_bytes()
            if hashlib.sha256(raw).hexdigest()!=artifact["sha256"]: raise ValueError("verifier artifact readback mismatch")
    def _claude(self,parent,contract,config):
        base=self.root/"workflow"; child=contract["child_run_id"]
        promoted_path=base/"adapter-source"/f"receipt_{child}.json"
        if promoted_path.exists():
            value=json.loads(promoted_path.read_text()); evidence=value["evidence"][0]
            artifact={"artifact_id":f"{parent}:{contract['stage_id']}","sha256":evidence["sha256"],"media_type":"text/markdown"}; self._register(artifact,Path(evidence["path"])); return artifact
        worker={"runtime":"claude","identity":"lhm-marketing-hub:seo" if contract["stage_id"]=="research" else "lhm-marketing-hub:content","run_id":child}
        bridge_contract={"parent_run_id":parent,"child_run_id":child,"workflow_id":"seo-content-astro-v1",
          "stage_id":"seo_evidence" if contract["stage_id"]=="research" else "content_production",
          "idempotency_key":contract["idempotency_key"],"worker":worker,"required_skills":contract["required_skills"],
          "required_capabilities":contract["required_capabilities"],"expected_mutation_state":"none"}
        source=base/"controller-outgoing"/f"{child}.json"; atomic(source,bridge_contract)
        atomic(self.root/"mappings"/f"{child}.json",{"org_contract_sha256":digest(contract),"bridge_contract_sha256":digest(bridge_contract),"org_stage":contract["stage_id"],"bridge_stage":bridge_contract["stage_id"],"child_run_id":child})
        hook=Path(os.environ.get("LHM_CANARY_HOOK",str(HOOK)))
        supervisor=Path(os.environ.get("LHM_CANARY_SUPERVISOR",str(SUPERVISOR)))
        env={**os.environ,"LHM_WORKFLOW_CANARY_MODE":"1","LHM_WORKFLOW_ROOT":str(base)}
        manifest=base/"bridge-incoming"/f"{child}.json"; roots=BridgeRoots(base/"issued-contracts",base/"host-events",base/"worker-results",base/"adapter-source",base/"processed"/"bridge",base/"quarantine"/"bridge")
        if not manifest.exists() and (base/"worker-results"/f"{child}.json").exists() and (base/"host-events"/f"{child}.jsonl").exists():
            events=(base/"host-events"/f"{child}.jsonl").read_text().splitlines()
            if events and json.loads(events[-1]).get("event")=="terminal": atomic(manifest,{"contract":f"{child}.json","host_events":f"{child}.jsonl","worker_result":f"{child}.json"})
        if manifest.exists():
            promoted=process_manifest(manifest,roots,adapter_gid=os.getgid())
            if promoted is not None:
                value=json.loads(promoted.read_text()); evidence=value["evidence"][0]; artifact={"artifact_id":f"{parent}:{contract['stage_id']}","sha256":evidence["sha256"],"media_type":"text/markdown"}; self._register(artifact,Path(evidence["path"])); return artifact
        subprocess.run([str(hook),"admit",str(source),child],check=True,env=env)
        request={"profile":"seo_gsc_readonly" if contract["stage_id"]=="research" else "specialist_readonly",
          "required_skills":contract["required_skills"],"required_capabilities":contract["required_capabilities"],
          "objective":config["objective"],"site_property":config["site_property"],"urls":config["urls"],"timeout_seconds":config.get("timeout_seconds",600)}
        run_dir=Path("/home/hermes/.hermes/profiles/lhm_brain/dispatch/claude/runs")/child
        subprocess.run([str(supervisor),child,str(self._request(child,request)),str(run_dir)],check=True,env=env)
        promoted=promoted_path if promoted_path.exists() else process_manifest(manifest,roots,adapter_gid=os.getgid())
        if promoted is None: raise ValueError("trusted Claude bridge promotion failed")
        value=json.loads(promoted.read_text()); evidence=value["evidence"][0]
        artifact={"artifact_id":f"{parent}:{contract['stage_id']}","sha256":evidence["sha256"],"media_type":"text/markdown"}; self._register(artifact,Path(evidence["path"])); return artifact
    def _request(self,child,value):
        path=self.root/"requests"/f"{child}.json"; atomic(path,value); return path
    def initialise(self,event,parent): return self.router.initialise(event,parent)
    def run(self,parent,config,step=False,pause_after=None):
        while True:
            state=self.router.load(parent)
            if state["state"]=="closed": self._bundle(parent); return state
            if state["state"] not in {"ready","running"}: self._bundle(parent); return state
            stage=state["stage_order"][state["cursor"]]; child=f"{parent}:{stage}"
            contract=self.router.issue(parent,child)
            operation=self.root/"operations"/f"{digest(contract)}.json"
            saved=json.loads(operation.read_text()) if operation.exists() else None
            if saved and saved.get("status")=="completed": outputs=saved["outputs"]
            elif stage=="research":
                observed=self.research(parent,contract,config)
                if isinstance(observed,tuple): observed,path=observed; self._register(observed,Path(path))
                outputs=[observed]
            elif stage=="content":
                if self.content is None: raise ValueError("content required but governed adapter unavailable")
                outputs=[self.content(parent,contract,config)]
            elif contract["runtime"]=="verifier":
                self._verify(contract["input_artifacts"])
                outputs=contract["input_artifacts"]
            elif stage=="operations_readback":
                expected=contract["input_artifacts"][0]
                if self.trusted_internal: observed,_=self.tracker.readback(expected["sha256"])
                else:
                    env={**os.environ,"LHM_WORKFLOW_CANARY_MODE":"1","LHM_WORKFLOW_CANARY_ROOT":str(self.root)}
                    done=subprocess.run([str(self.tracker_adapter),"readback",expected["sha256"]],text=True,capture_output=True,check=True,env=env); observed=json.loads(done.stdout)["artifact"]
                # The connector identifies the canonical tracker generically;
                # the workflow registry identifies this immutable version by run.
                observed={**observed,"artifact_id":expected["artifact_id"]}
                if observed!=expected: raise ValueError("tracker adapter readback identity mismatch")
                outputs=[observed]
            elif stage=="operations_write":
                current=self.router.load(parent); request={"parent_run_id":parent,"run_result":"succeeded","work_state":"complete","completed_at":config["completed_at"]}
                summary=summary_from_parent(current,request); previous_bytes=self.tracker._current(); previous=sha(previous_bytes)
                lines=self.tracker._render(summary); expected_bytes=previous_bytes+(b"\n" if previous_bytes and not previous_bytes.endswith(b"\n") else b"")+lines
                intent={"status":"started","kind":"tracker_write","previous_sha256":previous,"expected_sha256":sha(expected_bytes),"request":request};
                if not saved: atomic(operation,intent); saved=intent
                observed_sha=sha(self.tracker._current())
                if observed_sha==saved["expected_sha256"]: artifact={"artifact_id":f"{parent}:seo-rollout-tracker","sha256":observed_sha,"media_type":"text/markdown"}
                elif observed_sha==saved["previous_sha256"]:
                    if self.trusted_internal: artifact,_=self.tracker.append_structured(summary,saved["previous_sha256"])
                    else:
                        env={**os.environ,"LHM_WORKFLOW_CANARY_MODE":"1","LHM_WORKFLOW_CANARY_ROOT":str(self.root)}
                        done=subprocess.run([str(self.tracker_adapter),"write",saved["previous_sha256"]],input=json.dumps(request),text=True,capture_output=True,check=True,env=env); artifact=json.loads(done.stdout)["artifact"]
                    if os.environ.get("LHM_CANARY_FAULT")=="after_tracker_before_checkpoint": raise RuntimeError("fault after tracker write")
                else: raise ValueError("tracker reconciliation conflict")
                artifact={**artifact,"artifact_id":f"{parent}:seo-rollout-tracker"}
                self._register(artifact,self.tracker.path); outputs=[artifact]
            else: outputs=[self._artifact(parent,stage,{"stage_id":stage,"inputs":contract["input_artifacts"],"status":"accepted"})]
            if not (saved and saved.get("status")=="completed"):
                atomic(operation,{"status":"completed","stage_id":stage,"contract_sha256":digest(contract),"outputs":outputs})
                if os.environ.get("LHM_CANARY_FAULT")=="after_external_before_accept" and stage=="research": raise RuntimeError("fault after external Research checkpoint")
            checks=["structured_acceptance"]
            if stage=="chief_handback": checks.append("governed_delivery_suppressed_canary")
            decision=None
            if stage=="seo_accept": decision={"content_required":bool(config.get("content_required",False)),"website_required":False,"reason":"verified_research_canary"}
            value=self._signed(contract,outputs,checks,decision)
            atomic(self.root/"role-receipts"/f"{digest(contract)}.json",value)
            self.router.accept(parent,contract,value); self._bundle(parent)
            if step or pause_after==stage: return self.router.load(parent)
    def _bundle(self,parent):
        state=self.router.load(parent); bundle={"schema_version":1,"parent":state,"parent_sha256":digest(state),"artifact_hashes":{}}
        children={stage["child_run_id"] for stage in state.get("stages",[]) if stage.get("child_run_id")}
        contracts={stage["contract_sha256"] for stage in state.get("stages",[]) if stage.get("contract_sha256")}
        artifacts={item["artifact_id"] for stage in state.get("stages",[]) for item in stage.get("outputs",[]) if item.get("artifact_id")}
        root=self.artifacts/parent
        if root.exists(): bundle["artifact_hashes"]={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(root.rglob("*")) if p.is_file()}
        for name in ("mappings","operations","role-receipts"):
            directory=self.root/name
            wanted=children if name=="mappings" else contracts
            bundle[name]={p.name:{"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"value":json.loads(p.read_text())} for p in sorted(directory.glob("*.json")) if p.stem in wanted} if directory.exists() else {}
        workflow=self.root/"workflow"; bundle["bridge_evidence"]={}
        if workflow.exists():
            for sub in ("host-events","adapter-source","issued-contracts","worker","bridge-incoming","processed","controller-outgoing","worker-results"):
                for p in sorted((workflow/sub).rglob("*")):
                    exact_names={name for child in children for name in (child,f"{child}.json",f"{child}.jsonl",f"receipt_{child}.json")}
                    if p.is_file() and (p.name in exact_names or any(part in children for part in p.relative_to(workflow/sub).parts[:-1])):
                        bundle["bridge_evidence"][str(p.relative_to(workflow))]=hashlib.sha256(p.read_bytes()).hexdigest()
        registry_path=self.root/"artifact-registry.json"
        if registry_path.exists():
            registry=json.loads(registry_path.read_text()); scoped={key:value for key,value in registry.items() if key in artifacts}
            bundle["artifact_registry"]={"sha256":digest(scoped),"value":scoped}
        if self.tracker.path.exists():
            raw=self.tracker.path.read_bytes(); marker=f"## Governed run {parent}\n".encode(); start=raw.find(marker)
            if start>=0:
                end=raw.find(b"\n## Governed run ",start+len(marker)); scoped=raw[start:] if end<0 else raw[start:end+1]
                bundle["tracker"]={"sha256":hashlib.sha256(scoped).hexdigest(),"bytes_hex":scoped.hex()}
        requests=self.root/"requests"; bundle["requests"]={p.name:{"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"value":json.loads(p.read_text())} for p in sorted(requests.glob("*.json")) if p.stem in children} if requests.exists() else {}
        atomic(self.root/"evidence"/f"{parent}.json",bundle)
