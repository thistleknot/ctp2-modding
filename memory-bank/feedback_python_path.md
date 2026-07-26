---
name: feedback-python-path
description: Always invoke Python via C:\Users\user\py310\Scripts\python — the only correct interpreter for this project
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 77eb8577-a451-4ba1-84c7-af8b7cf3cf0e
---

The only correct Python for this project is `C:\Users\user\py310\Scripts\python`
(Python 3.10.0; in Git Bash: `/c/Users/user/py310/Scripts/python`).

**Why:** other interpreters may be on PATH depending on shell (PowerShell vs Git Bash)
or environment changes; project tooling (validate_all_surfaces.py, test_mom_slic.py,
ctpedit.py, patch_ctp2_images.py, mom_audit.py) is built against this 3.10 env and its
installed packages. Bare `python` happened to resolve correctly in Git Bash on
2026-07-09, but that is incidental, not guaranteed.

**How to apply:** use the explicit path in every shell invocation instead of bare
`python`/`py`. Git Bash: `/c/Users/user/py310/Scripts/python script.py`.
PowerShell: `& C:\Users\user\py310\Scripts\python script.py`.
