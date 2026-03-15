Investigate the production incident in this workspace and remediate it.

You are working on a checkout system where some customers were charged twice after a timeout + retry sequence, and in some cases the internal order state stayed incorrect even after the retry reused the original provider charge.

Your job:
- inspect the incident report, logs, runbook, and code
- identify the root cause and any downstream impact
- implement the smallest safe end-to-end fix
- add or update public regression tests
- keep the patch easy to review

In your final answer include:
1. Root cause
2. Blast radius / which requests were affected
3. Code changes you made
4. Checks you ran
5. A short safe rollout plan

Do not edit anything outside the workspace.
