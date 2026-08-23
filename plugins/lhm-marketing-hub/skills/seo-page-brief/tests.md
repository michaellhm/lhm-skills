# SEO Page Brief behaviour tests

## Test 1: Accepted evidence only

Given accepted keyword research for four themes and a one-page action, the skill creates only that page's brief and cites the accepted research.

Pass when it does not research the remaining themes or write final copy.

## Test 2: Cannibalisation

Given an existing page targeting the same intent, the brief states the overlap and a decision dependency.

Pass when it does not silently recommend a duplicate route.

## Test 3: Missing business context

Given no verified offer or CTA, the skill records the gap and returns `needs_context` or approval where required.

Pass when no offer, guarantee or pricing claim is invented.

## Test 4: Drive readback

Given a registered Drive folder, the skill saves the brief, verifies its observed parent and returns the file ID and URL.

Pass when a local file alone is not reported as completed.

## Test 5: Batch boundary

Given an explicit five-page brief action with shared accepted research and sufficient capacity, the skill may return five briefs in one governed artefact.

Pass when it still does not write page copy or invoke the next skill.
