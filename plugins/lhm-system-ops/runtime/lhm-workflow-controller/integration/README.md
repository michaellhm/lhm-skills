# Hermes dispatcher hook integration

`hermes_workflow_hook.py` is an offline deployment draft. `admit` accepts
contracts only from the fixed root-owned `controller-outgoing` spool; worker
results are restricted to the fixed runtime run roots. The root Claude and
Codex dispatchers call it only at host-controlled boundaries:

```text
admit <controller-issued-contract> <child>  # after fixed route validation
skill <child> <skill-id>                    # immediately before exact skill launch
capability <child> <capability-id>          # after host connector readback
complete <child> <worker-result>            # after successful bounded worker exit
```

Do not infer `skill` from the request or worker prose. For Claude, this hook
belongs beside the fixed `SPECIALIST_ROUTES`/`claude_agent` launch. For Codex,
it belongs beside the fixed skill-bearing worker command. Connector capability
events belong in the host connector adapter after successful readback.

The draft is not installed or enabled by `install.sh`; it must undergo the
same exact-byte deployment and real-user rehearsal as the controller before
use.

`lhm-scheduled-work-dispatch` is the container-visible queue writer and
`lhm-scheduled-work-ingress` is the common trusted host entry point. Department-specific wrappers
may select a registered identity and objective; they must not embed worker commands, polling,
retries, QA or delivery logic. The root-owned registry remains authoritative. The disabled SEO candidate is the
reference configuration and does not replace the live job until the full organisational canary,
failure receipt and rollback checks pass.
