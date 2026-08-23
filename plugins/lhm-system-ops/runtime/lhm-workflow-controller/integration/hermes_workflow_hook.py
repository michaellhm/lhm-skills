#!/usr/bin/env python3
"""Offline draft of the root hook called by Hermes host dispatchers.

Call `admit` after validating and launching the exact governed skill route,
`skill` at the host skill-dispatch boundary, `capability` after a host connector
readback, and `complete` only after the restricted worker exits successfully.
"""
from __future__ import annotations

import argparse, fcntl, hashlib, json, os, re, tempfile
from pathlib import Path
from lhm_workflow.secureio import read_trusted

if "LHM_WORKFLOW_ROOT" in os.environ and os.environ.get("LHM_WORKFLOW_TEST_MODE") != "1":
    candidate=Path(os.environ["LHM_WORKFLOW_ROOT"])
    if not (os.geteuid()==0 and os.environ.get("LHM_WORKFLOW_CANARY_MODE")=="1" and candidate.is_relative_to(Path("/var/lib/lhm-workflow-canary"))):
        raise SystemExit("LHM_WORKFLOW_ROOT override requires explicit test or root canary mode")
BASE = Path(os.environ.get("LHM_WORKFLOW_ROOT", "/var/lib/lhm-workflow"))
RUNTIME_UIDS = {"claude": 10002, "codex": 10001, "lhm_host_verifier": 10006}
NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,99}$")
CONTRACT_OUTBOX = BASE / "controller-outgoing"
WORKER_ROOTS = {
    "claude": Path("/home/hermes/.hermes/profiles/lhm_brain/dispatch/claude/runs"),
    "codex": Path("/home/hermes/.hermes/profiles/lhm_brain/dispatch/site-runs"),
    "lhm_host_verifier": BASE / "verifier-worker-results",
}

def canon(v): return json.dumps(v, sort_keys=True, separators=(",", ":")).encode()
def contract(child):
    if not NAME.fullmatch(child): raise SystemExit("invalid child id")
    path=BASE / "issued-contracts" / f"{child}.json"
    expected=os.getuid() if os.environ.get("LHM_WORKFLOW_TEST_MODE")=="1" else 0
    return json.loads(read_trusted(path, root=path.parent, uid=expected))
def atomic(path, raw, mode=0o600, uid=0, gid=0):
    if os.environ.get("LHM_WORKFLOW_TEST_MODE")=="1": uid,gid=os.getuid(),os.getgid()
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.")
    try:
        with os.fdopen(fd, "wb") as f: f.write(raw); f.flush(); os.fsync(f.fileno())
        os.chown(tmp, uid, gid); os.chmod(tmp, mode); os.replace(tmp, path)
    finally: Path(tmp).unlink(missing_ok=True)
def append(child, kind, **fields):
    c = contract(child); path = BASE / "host-events" / f"{child}.jsonl"; lock = path.with_suffix(".lock")
    path.parent.mkdir(parents=True,exist_ok=True)
    lock.touch(mode=0o600, exist_ok=True)
    with lock.open("r+") as held:
        fcntl.flock(held, fcntl.LOCK_EX)
        lines = path.read_bytes().splitlines() if path.exists() else []
        event = {"source":"host-dispatcher", "seq":len(lines)+1, "event":kind, "child_run_id":child,
                 "contract_sha256":hashlib.sha256(canon(c)).hexdigest(), **fields}
        atomic(path, b"\n".join(lines + [canon(event)]) + b"\n")
def main():
    test_mode=os.environ.get("LHM_WORKFLOW_TEST_MODE")=="1"
    if os.geteuid() != 0 and not test_mode: raise SystemExit("root host hook only")
    p=argparse.ArgumentParser(); sub=p.add_subparsers(dest="cmd", required=True)
    a=sub.add_parser("admit"); a.add_argument("source", type=Path); a.add_argument("child")
    for name in ("skill","capability"):
        q=sub.add_parser(name); q.add_argument("child"); q.add_argument("value")
    q=sub.add_parser("complete"); q.add_argument("child"); q.add_argument("result", type=Path)
    x=p.parse_args()
    if not NAME.fullmatch(x.child): raise SystemExit("invalid child id")
    if x.cmd=="admit":
        c=json.loads(read_trusted(x.source, root=CONTRACT_OUTBOX, uid=os.getuid() if test_mode else 0));
        if c.get("child_run_id") != x.child: raise SystemExit("contract child mismatch")
        target=BASE/"issued-contracts"/f"{x.child}.json"
        if target.exists():
            if read_trusted(target, root=target.parent, uid=os.getuid() if test_mode else 0) != canon(c)+b"\n": raise SystemExit("conflicting admitted contract")
            if (BASE/"host-events"/f"{x.child}.jsonl").exists(): return
        else: atomic(target, canon(c)+b"\n")
        append(x.child,"dispatch_admitted",worker=c["worker"])
    elif x.cmd in ("skill","capability"):
        append(x.child, "skill_invoked" if x.cmd=="skill" else "capability_observed", **({"skill":x.value} if x.cmd=="skill" else {"capability":x.value}))
    else:
        c=contract(x.child); runtime=c["worker"]["runtime"]; uid=os.getuid() if test_mode else RUNTIME_UIDS.get(runtime)
        if (BASE/"bridge-incoming"/f"{x.child}.json").exists(): return
        if uid is None: raise SystemExit("unknown runtime")
        worker_root=Path(os.environ["LHM_CLAUDE_RUNS"]) if test_mode and runtime=="claude" else WORKER_ROOTS[runtime]
        raw=read_trusted(x.result, root=worker_root, uid=uid); st=x.result.stat(); value=json.loads(raw)
        evidence=value.get("evidence")
        if not isinstance(evidence,list) or not evidence: raise SystemExit("candidate evidence required")
        evidence_root=BASE/"worker"/x.child
        evidence_root.mkdir(parents=True,exist_ok=True); os.chown(evidence_root,os.getuid() if test_mode else 0,os.getgid() if test_mode else 10004); os.chmod(evidence_root,0o750)
        for index,item in enumerate(evidence):
            if not isinstance(item,dict) or set(item)!={"kind","path","sha256"}: raise SystemExit("invalid candidate evidence")
            source=Path(item["path"]); body=read_trusted(source,root=worker_root,uid=uid)
            observed=hashlib.sha256(body).hexdigest()
            if item["kind"]!="artifact" or observed!=item["sha256"]: raise SystemExit("candidate evidence hash mismatch")
            target=evidence_root/f"{index}-{observed}.evidence"
            atomic(target,body,mode=0o640,uid=uid,gid=10004); item["path"]=str(target)
        raw=canon(value)+b"\n"
        atomic(BASE/"worker-results"/f"{x.child}.json", raw, uid=uid, gid=st.st_gid)
        append(x.child,"terminal",status="completed")
        manifest={"contract":f"{x.child}.json","host_events":f"{x.child}.jsonl","worker_result":f"{x.child}.json"}
        atomic(BASE/"bridge-incoming"/f"{x.child}.json", canon(manifest)+b"\n")
if __name__ == "__main__": main()
