# Hermes publish recovery — recorded role passes

Parent: `ASP-SITEMAP-V2-PUBLISH-20260820`  
Incident: `hermes-publish-recovery-20260820`  
Original incident: `asp-proto-publish-route-20260820`

## 1. Capability Researcher — recommended

Native LHM already has a root-owned CTO dispatcher and bounded Git publisher. Reuse those patterns;
do not install a third party or grant Hermes general GitHub authority. Use deterministic iteration
branches (`base`, `base-i2`, `base-i3`) and exact-workspace retry reuse. Keep ASP protected-main
authority in a separate fixed publisher so the CTO branch publisher is not broadened.

## 2. Platform Engineer — implemented in workspace

Added deterministic worktree selection, safe exact retry reuse, the single-purpose ASP publisher,
static controls, tests and release documentation. No commit, push, deployment, credential access,
live Hermes, DNS, production-site, client-contact or BasicOps mutation occurred.

## 3. QA Tester — command evidence recorded at handoff

Coverage includes duplicate/retry and iteration behavior; repository, branch, path and schema
negatives; missing credentials; exact Actions/public-URL success gating; and plugin compatibility.
Mocked/static checks are labelled and do not claim a live publication or installation.

## 4. Security/Reliability Reviewer — approved for bounded review publication

The request has no command/refspec/authority escape, credentials remain root-only, paths reject
traversal/symlinks/sensitive material, moving main fails closed, and success follows remote SHA,
Actions and public URL verification. Residual risk: the installed root service and GitHub branch
protection/credential scope require operator verification. Rollback is executable/config-only.

## 5. Plugin Release Manager — unpublished handoff

The workspace may go only to the existing bounded `cto/*` branch publisher after validation. That
publication is not installation or restoration. Michael retains merge, release and deployment
authority. A live installed-commit regression and consumed restoration event remain post-deployment
evidence and are not claimed by this workspace pass.
