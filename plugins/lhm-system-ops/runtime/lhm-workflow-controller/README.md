# LHM Workflow Controller

Host-enforced orchestration for the fixed `seo-content-astro-v1` production workflow.

This service owns durable workflow state and accepts only host-derived evidence. Workers cannot
advance parent state or self-verify completion.

## Client preflight release

The `lhm-seo-org-canary-mvp` entry point requires a canonical Obsidian client record before
dispatching research. The required record is:

`_System/Hermes/clients/<client-id>/capabilities.json`

The Google Search Console capability must be `verified`, use the fixed `seo_gsc_readonly` route,
match the workflow property exactly, allow the four bounded read operations, and reference a
passing smoke-test result. Missing or incomplete records stop with `client_onboarding_required`.

This source tree is durable package source only. Copying or building it does not enable the cron,
start a watcher, install a service, or mutate the live vault.
