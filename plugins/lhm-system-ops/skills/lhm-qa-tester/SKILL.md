---
name: lhm-qa-tester
description: Test a proposed Hermes or LHM plugin capability independently from its implementation pass. Use after Platform Engineering and before security or release.
---

# LHM QA Tester

Test the proposed commit against the accepted capability brief. Do not repair failures during the QA pass; return them to Engineering.

## Minimum suite

- plugin and marketplace manifest validation;
- every changed skill's structural validation;
- existing-plugin compatibility;
- positive acceptance test;
- invalid input and permission negative tests;
- duplicate/idempotency behaviour;
- restart and interrupted-run recovery where stateful;
- the original incident regression;
- confirmation that protected `main`, live Hermes and production systems were not modified.

## Disposition

Return `pass`, `fail` or `blocked`, with commit tested, exact commands, outputs/evidence, failures, untested areas and required next owner. A partial or mocked test must be labelled as such.
