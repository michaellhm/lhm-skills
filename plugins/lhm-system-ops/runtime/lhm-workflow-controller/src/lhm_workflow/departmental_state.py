"""Governed one-action departmental state with independent QA and durable CAS."""
from __future__ import annotations
import copy,fcntl,hashlib,hmac,json,os,re,tempfile
from contextlib import contextmanager
from pathlib import Path
SAFE=re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,119}$"); HEX=re.compile(r"^[0-9a-f]{64}$")
DONE={"accepted","cancelled","obsolete"}
def canonical(v): return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def digest(v): return hashlib.sha256(canonical(v)).hexdigest()
def seal(v,key):
 u=copy.deepcopy(v);u.pop("attestation",None);u["attestation"]=hmac.new(key,canonical(u),hashlib.sha256).hexdigest();return u
def authenticated(v,key,role):
 sig=v.get("attestation") if isinstance(v,dict) else None;u=copy.deepcopy(v) if isinstance(v,dict) else {};u.pop("attestation",None)
 return v.get("role") == role and isinstance(sig,str) and hmac.compare_digest(sig,hmac.new(key,canonical(u),hashlib.sha256).hexdigest())
def ident(v,n):
 if not isinstance(v,str) or not SAFE.fullmatch(v): raise ValueError(f"invalid {n}")
 return v
def text(v,n):
 if not isinstance(v,str) or not v.strip(): raise ValueError(f"invalid {n}")
 return v.strip()
def artifact(v,key):
 keys={"artifact_id","sha256","media_type","drive_file_id","drive_url","drive_parent_id","readback_sha256","role","attestation"}
 if not isinstance(v,dict) or set(v)!=keys: raise ValueError("invalid artifact receipt")
 ident(v["artifact_id"],"artifact_id")
 if not HEX.fullmatch(str(v["sha256"])) or v["readback_sha256"]!=v["sha256"]: raise ValueError("artifact readback mismatch")
 if not any(str(v["drive_url"]).startswith(p) for p in ("https://drive.google.com/","https://docs.google.com/document/","https://docs.google.com/spreadsheets/","https://docs.google.com/presentation/")) or any(not str(v[k]) for k in ("media_type","drive_file_id","drive_parent_id")): raise ValueError("invalid artifact destination")
 if not authenticated(v,key,"drive_connector"):raise ValueError("invalid connector attestation")
 return copy.deepcopy(v)
def validate_state(s):
 top={"schema_version","generation","parent_run_id","department","parent_goal","department_goal","state","action_register"}
 if not isinstance(s,dict) or set(s)!=top or s.get("schema_version")!=1 or not isinstance(s.get("generation"),int) or s["generation"]<0: raise ValueError("invalid departmental state")
 ident(s["parent_run_id"],"parent_run_id"); ident(s["department"],"department"); text(s["parent_goal"],"parent_goal"); text(s["department_goal"],"department_goal")
 if s["state"] not in {"ready","worker_running","qa_accepted","lead_accepted","department_accepted","failed"}: raise ValueError("invalid state")
 fields={"position","action_id","version","dependencies","objective","required_skills","accepted_inputs","required_output","dispatch_envelope","input_digest","stable_action_key","status","child_run_id","contract","candidate","qa_receipt","lead_acceptance","projection_receipt"}
 seen=set(); incomplete=[]
 if not isinstance(s["action_register"],list) or not s["action_register"]: raise ValueError("invalid register")
 for pos,a in enumerate(s["action_register"]):
  if not isinstance(a,dict) or set(a)!=fields or a["position"]!=pos: raise ValueError("invalid action")
  aid=ident(a["action_id"],"action_id")
  if aid in seen or any(d not in seen for d in a["dependencies"]): raise ValueError("invalid dependencies")
  seen.add(aid)
  if not isinstance(a["version"],int) or a["version"]<1 or not a["required_skills"]: raise ValueError("invalid action contract")
  if a["required_output"] not in {"durable","non_durable"}:raise ValueError("invalid required_output")
  envelope=a["dispatch_envelope"]; ekeys={"delivery_parent_id","permission_ceiling","completion_test","basicops_task_id","basicops_dedupe_key","discussion_payload","no_subtasks","constraints","return_role","return_point","approval"}
  if not isinstance(envelope,dict) or set(envelope)!=ekeys or envelope["permission_ceiling"] not in {"green","amber"} or not envelope["completion_test"] or envelope["no_subtasks"] is not True:raise ValueError("invalid dispatch envelope")
  blocks={"Goal","Outcome","Milestones","Actions","Artefacts","Dependencies","Completion","Next handoff"};discussion=envelope["discussion_payload"]
  if not isinstance(discussion,dict) or set(discussion)!=blocks or any(not discussion[k] for k in blocks):raise ValueError("invalid governed discussion payload")
  if not isinstance(envelope["approval"],dict) or set(envelope["approval"])!={"required","receipt","superseded_by_version"}:raise ValueError("invalid approval contract")
  if digest(a["accepted_inputs"])!=a["input_digest"]: raise ValueError("input digest mismatch")
  key=digest({"parent_run_id":s["parent_run_id"],"action_id":aid,"version":a["version"],"input_digest":a["input_digest"]})
  if key!=a["stable_action_key"]: raise ValueError("stable action key mismatch")
  if a["status"] not in {"waiting","ready","running","qa_accepted","lead_accepted","accepted","cancelled","obsolete"}: raise ValueError("invalid action status")
  if a["status"] not in DONE: incomplete.append(aid)
  if a["status"]=="accepted" and not all((a["candidate"],a["qa_receipt"],a["lead_acceptance"],a["projection_receipt"])): raise ValueError("accepted action lacks evidence")
  expected={"waiting":(0,0,0,0),"ready":(0,0,0,0),"qa_accepted":(1,1,0,0),"lead_accepted":(1,1,1,0),"accepted":(1,1,1,1)}.get(a["status"])
  if expected and tuple(int(x is not None) for x in (a["candidate"],a["qa_receipt"],a["lead_acceptance"],a["projection_receipt"]))!=expected:raise ValueError("status/evidence mismatch")
 ready=[a for a in s["action_register"] if a["status"]=="ready"]
 if len(ready)>1 or (ready and ready[0]["action_id"]!=incomplete[0]): raise ValueError("only first incomplete may be ready")
 active=next((a for a in s["action_register"] if a["status"] not in DONE),None)
 wanted="department_accepted" if active is None else {"ready":"ready","running":"worker_running","qa_accepted":"qa_accepted","lead_accepted":"lead_accepted","waiting":"failed"}[active["status"]]
 if s["state"]!=wanted:raise ValueError("top state mismatch")
 return s
def new_departmental_state(*,parent_run_id,department,parent_goal,department_goal,actions):
 ident(parent_run_id,"parent_run_id"); ident(department,"department"); reg=[]; seen=set()
 for pos,x in enumerate(actions):
  if set(x)!={"action_id","dependencies","objective","required_skills","accepted_inputs","required_output","dispatch_envelope"}: raise ValueError("invalid action fields")
  aid=ident(x["action_id"],"action_id")
  if aid in seen or any(d not in seen for d in x["dependencies"]): raise ValueError("invalid dependencies")
  seen.add(aid); inputs=copy.deepcopy(x["accepted_inputs"]); ih=digest(inputs); version=1
  reg.append({"position":pos,"action_id":aid,"version":version,"dependencies":list(x["dependencies"]),"objective":text(x["objective"],"objective"),"required_skills":list(x["required_skills"]),"accepted_inputs":inputs,"required_output":x["required_output"],"dispatch_envelope":copy.deepcopy(x["dispatch_envelope"]),"input_digest":ih,"stable_action_key":digest({"parent_run_id":parent_run_id,"action_id":aid,"version":version,"input_digest":ih}),"status":"ready" if pos==0 else "waiting","child_run_id":None,"contract":None,"candidate":None,"qa_receipt":None,"lead_acceptance":None,"projection_receipt":None})
 return validate_state({"schema_version":1,"generation":0,"parent_run_id":parent_run_id,"department":department,"parent_goal":text(parent_goal,"parent_goal"),"department_goal":text(department_goal,"department_goal"),"state":"ready","action_register":reg})
def first_incomplete(s): validate_state(s); return next((copy.deepcopy(a) for a in s["action_register"] if a["status"] not in DONE),None)
def validate_approval(s,key):
 a=first_incomplete(s);approval=a["dispatch_envelope"]["approval"]
 if not approval["required"]:return True
 r=approval["receipt"];keys={"schema_version","role","parent_run_id","action_id","action_version","material_sha256","decision","attestation"}
 material=digest({"objective":a["objective"],"inputs":a["accepted_inputs"],"envelope":{k:v for k,v in a["dispatch_envelope"].items() if k!="approval"}})
 if not isinstance(r,dict) or set(r)!=keys or not authenticated(r,key,"approval_authority") or (r["parent_run_id"],r["action_id"],r["action_version"],r["material_sha256"],r["decision"])!=(s["parent_run_id"],a["action_id"],a["version"],material,"approved"):raise ValueError("valid machine approval required")
 return True
def revise_action_inputs(s,action_id,inputs):
 u=copy.deepcopy(validate_state(s)); a=next(x for x in u["action_register"] if x["action_id"]==action_id)
 if a["status"] not in {"ready","waiting","running","qa_accepted"}: raise ValueError("action inputs cannot be revised")
 first=first_incomplete(u)["action_id"]==action_id; old=a["version"];a["version"]+=1;a["dispatch_envelope"]["approval"].update(receipt=None,superseded_by_version=a["version"] if a["dispatch_envelope"]["approval"]["required"] else None); a["accepted_inputs"]=copy.deepcopy(inputs); a["input_digest"]=digest(inputs); a["stable_action_key"]=digest({"parent_run_id":u["parent_run_id"],"action_id":action_id,"version":a["version"],"input_digest":a["input_digest"]}); a.update(status="ready" if first else "waiting",child_run_id=None,contract=None,candidate=None,qa_receipt=None,lead_acceptance=None,projection_receipt=None); u["state"]="ready"; return validate_state(u)
def issue_next_action(s,child):
 u=copy.deepcopy(validate_state(s)); ident(child,"child_run_id"); a=next(x for x in u["action_register"] if x["status"] not in DONE)
 if a["status"]=="running" and a["child_run_id"]==child:return u,copy.deepcopy(a["contract"])
 if a["status"]!="ready":raise ValueError("first incomplete action is not dispatchable")
 c={"schema_version":1,"parent_run_id":u["parent_run_id"],"department":u["department"],"parent_goal":u["parent_goal"],"department_goal":u["department_goal"],"action_id":a["action_id"],"action_version":a["version"],"objective":a["objective"],"child_run_id":child,"required_skills":list(a["required_skills"]),"accepted_inputs":copy.deepcopy(a["accepted_inputs"]),"required_output":a["required_output"],"dispatch_envelope":copy.deepcopy(a["dispatch_envelope"]),"input_digest":a["input_digest"],"stable_action_key":a["stable_action_key"]}; a.update(status="running",child_run_id=child,contract=copy.deepcopy(c));u["state"]="worker_running";return validate_state(u),c
def record_candidate(s,c,v,connector_key):
 u=copy.deepcopy(validate_state(s));a=next(x for x in u["action_register"] if x["action_id"]==c.get("action_id"));keys={"candidate_id","contract_sha256","artifacts","completion_evidence","permission_evidence","output_disposition"}
 if a["candidate"] is not None:
  if a["candidate"]!=v:raise ValueError("conflicting candidate replay")
  return u
 if a["status"]!="running" or a["contract"]!=c or set(v)!=keys or v["contract_sha256"]!=digest(c):raise ValueError("invalid candidate")
 if v["completion_evidence"]!=c["dispatch_envelope"]["completion_test"] or v["permission_evidence"]!=[c["dispatch_envelope"]["permission_ceiling"]]:raise ValueError("candidate evidence does not satisfy dispatch")
 v=copy.deepcopy(v);v["artifacts"]=[artifact(x,connector_key) for x in v["artifacts"]]
 if any(x["drive_parent_id"]!=c["dispatch_envelope"]["delivery_parent_id"] for x in v["artifacts"]):raise ValueError("wrong Drive parent")
 if c["required_output"]=="durable" and (not v["artifacts"] or v["output_disposition"]!={"status":"delivered"}):raise ValueError("candidate requires durable artifact")
 disposition=v["output_disposition"]
 if c["required_output"]=="non_durable" and not v["artifacts"] and (not isinstance(disposition,dict) or set(disposition)!={"status","reason"} or disposition["status"]!="not_required" or not disposition["reason"]):raise ValueError("structured not_required evidence required")
 a["candidate"]=v;return validate_state(u)
def record_qa_acceptance(s,c,r,key):
 u=copy.deepcopy(validate_state(s));a=next(x for x in u["action_register"] if x["action_id"]==c.get("action_id"));keys={"schema_version","role","disposition","contract_sha256","candidate_sha256","artifact_receipt_sha256","readback_checks","permission_checks","completion_checks","attestation"}
 if a["qa_receipt"] is not None:
  if a["qa_receipt"]!=r:raise ValueError("conflicting QA replay")
  return u
 if set(r)!=keys or not authenticated(r,key,"qa_verifier") or r["disposition"]!="accepted" or a["status"]!="running" or not a["candidate"]:raise ValueError("independent QA acceptance required")
 if r["contract_sha256"]!=digest(c) or r["candidate_sha256"]!=digest(a["candidate"]) or r["artifact_receipt_sha256"]!=digest(a["candidate"]["artifacts"]):raise ValueError("QA evidence binding mismatch")
 if r["permission_checks"]!=[c["dispatch_envelope"]["permission_ceiling"]] or r["completion_checks"]!=c["dispatch_envelope"]["completion_test"] or not r["readback_checks"]:raise ValueError("QA evidence does not satisfy dispatch")
 a.update(status="qa_accepted",qa_receipt=copy.deepcopy(r));u["state"]="qa_accepted";return validate_state(u)
def record_lead_acceptance(s,c,r,key):
 u=copy.deepcopy(validate_state(s));a=next(x for x in u["action_register"] if x["action_id"]==c.get("action_id"));keys={"schema_version","role","decision","qa_receipt_sha256","goal_checks","attestation"}
 if a["lead_acceptance"] is not None:
  if a["lead_acceptance"]!=r:raise ValueError("conflicting Lead replay")
  return u
 if set(r)!=keys or not authenticated(r,key,"department_lead") or r["decision"]!="accepted" or a["status"]!="qa_accepted" or r["qa_receipt_sha256"]!=digest(a["qa_receipt"]) or not r["goal_checks"]:raise ValueError("Lead acceptance binding mismatch")
 a.update(status="lead_accepted",lead_acceptance=copy.deepcopy(r));u["state"]="lead_accepted";return validate_state(u)
def record_projection(s,c,r,key):
 u=copy.deepcopy(validate_state(s));a=next(x for x in u["action_register"] if x["action_id"]==c.get("action_id"));keys={"schema_version","role","parent_run_id","action_id","action_version","state_readback_sha256","tracker_path","tracker_sha256","tracker_readback_sha256","basicops_task_id","basicops_dedupe_key","basicops_comment_id","discussion_payload_sha256","no_subtasks","basicops_readback_sha256","attestation"}
 if a["projection_receipt"] is not None:
  if a["projection_receipt"]!=r:raise ValueError("conflicting projection replay")
  return u
 if set(r)!=keys or not authenticated(r,key,"projection_writer") or a["status"]!="lead_accepted" or r["state_readback_sha256"]!=digest(s):raise ValueError("projection incomplete")
 if (r["parent_run_id"],r["action_id"],r["action_version"])!=(s["parent_run_id"],a["action_id"],a["version"]):raise ValueError("projection binding mismatch")
 e=c["dispatch_envelope"]
 if r["basicops_task_id"]!=e["basicops_task_id"] or r["basicops_dedupe_key"]!=e["basicops_dedupe_key"] or r["discussion_payload_sha256"]!=digest(e["discussion_payload"]) or r["no_subtasks"] is not True:raise ValueError("projection BasicOps binding mismatch")
 if r["tracker_sha256"]!=r["tracker_readback_sha256"] or any(not r[k] for k in ("tracker_path","basicops_task_id","basicops_comment_id")) or not HEX.fullmatch(str(r["basicops_readback_sha256"])):raise ValueError("false projection readback")
 a.update(status="accepted",projection_receipt=copy.deepcopy(r));n=next((x for x in u["action_register"] if x["status"]=="waiting"),None)
 if n:
  if a["action_id"] not in n["dependencies"]:raise ValueError("next action lacks dependency")
  n["accepted_inputs"].extend(copy.deepcopy(a["candidate"]["artifacts"]));n["version"]+=1;n["input_digest"]=digest(n["accepted_inputs"]);n["stable_action_key"]=digest({"parent_run_id":u["parent_run_id"],"action_id":n["action_id"],"version":n["version"],"input_digest":n["input_digest"]});n["status"]="ready";u["state"]="ready"
 else:u["state"]="department_accepted"
 return validate_state(u)
def accept_completion_dossier(s,r,key):
 """Head of Production accepts a closed SEO dossier and explicit Astro return evidence."""
 validate_state(s);keys={"schema_version","role","parent_run_id","department_state_sha256","seo_action_receipts","astro_return_evidence","completion_checks","decision","attestation"}
 if set(r)!=keys or not authenticated(r,key,"head_of_production") or s["state"]!="department_accepted" or r["decision"]!="accepted":raise ValueError("invalid completion dossier")
 if r["parent_run_id"]!=s["parent_run_id"] or r["department_state_sha256"]!=digest(s):raise ValueError("completion dossier binding mismatch")
 expected=[digest(a["projection_receipt"]) for a in s["action_register"] if a["status"]=="accepted"]
 astro=r["astro_return_evidence"];last=s["action_register"][-1]["dispatch_envelope"]
 if r["seo_action_receipts"]!=expected or not isinstance(astro,dict) or set(astro)!={"required","receipt_sha256","return_role","return_point","seo_state_sha256"} or not r["completion_checks"]:raise ValueError("incomplete SEO/Astro dossier")
 if astro["required"] is not True or not HEX.fullmatch(str(astro["receipt_sha256"])) or astro["return_role"]!=last["return_role"] or astro["return_point"]!=last["return_point"] or astro["seo_state_sha256"]!=digest(s):raise ValueError("Astro return evidence binding mismatch")
 return copy.deepcopy(r)
class DepartmentalStateStore:
 def __init__(self,root):self.root=Path(root);self.root.mkdir(parents=True,exist_ok=True)
 def path(self,p):return self.root/f"{ident(p,'parent_run_id')}.json"
 @contextmanager
 def lock(self,p):
  h=(self.root/f".{p}.lock").open("a+b");fcntl.flock(h,fcntl.LOCK_EX)
  try:yield
  finally:fcntl.flock(h,fcntl.LOCK_UN);h.close()
 def load(self,p):return validate_state(json.loads(self.path(p).read_text()))
 def checkpoint(self,s,*,expected_generation):
  v=copy.deepcopy(validate_state(s));p=self.path(v["parent_run_id"])
  with self.lock(v["parent_run_id"]):
   old=self.load(v["parent_run_id"]) if p.exists() else None;observed=None if old is None else old["generation"]
   if observed!=expected_generation:raise ValueError("stale departmental checkpoint")
   v["generation"]=1 if observed is None else observed+1;fd,tmp=tempfile.mkstemp(dir=self.root,prefix=f".{p.name}.")
   try:
    with os.fdopen(fd,"wb") as h:h.write(canonical(v)+b"\n");h.flush();os.fsync(h.fileno())
    os.chmod(tmp,0o600);os.replace(tmp,p);d=os.open(self.root,os.O_RDONLY);os.fsync(d);os.close(d)
   finally:Path(tmp).unlink(missing_ok=True)
   got=self.load(v["parent_run_id"])
   if digest(got)!=digest(v):raise IOError("departmental state readback mismatch")
   return got
