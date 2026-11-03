# AGENTS.md

## Environment
- Ask the user if you need to load a MOOSE conda environment, and if so, what the name of the conda environment is
- If `./tmap8-opt` or `run_tests` throws an error, stop and ask the user
- Pre-commit hooks handle all formatting and input file validation on every `git commit` — do not invoke `clang-format`, `black`, or `hit format` manually
- `moose/framework/contrib/hit/hit check <file>.i` is available to validate input files during development — use it before committing

## Before writing any code or input file
- Browse `doc/content/` to understand documentation standards and existing patterns before starting work
- Before writing a new C++ class, look through existing MOOSE classes in the codebase to confirm expected syntax and patterns
- Documentation in `doc/content/` may not accurately reflect current code behavior — once you identify a class to use in an input file, find its C++ implementation and read it to confirm the class does what you expect before writing the input file

## C++ code
- Every new class requires a MOOSE TestHarness test in `test/tests/` before committing
- Every new class requires a MooseDocs page following existing TMAP8 doc structure
- Never hardcode physical parameters — first check if it is already defined in `doc/content/source/utils/TMAP8PhysicalConstants`, and if not available, expose everything through `addParam`
- Code is unit-agnostic; units live in input files only

## Input files
- Before writing an input file, look through existing MOOSE and TMAP8 classes to confirm object names and parameter syntax
- Use `moose/framework/contrib/hit/hit check <file>.i` to validate before committing
- Use `./tmap8-opt -i <file>.i` to run input files
- Write parameter values in the units the reference source used; use the MOOSE units system for conversion — the units system is self-documenting and does not require inline comments
- State the unit system at the top of every input file in a comment block

## Testing
- Run tests only when `.C`, `.h`, or `test/tests/` files change
- Run only the affected module: `./run_tests -j<N> --re <module>`

## Session log
- Every session must be associated with a GitHub issue on `idaholab/TMAP8`; ask the user for the issue number at the start of the session if one is not provided, or create one if the user instructs you to
- **SQA requirement:** When creating a GitHub issue with `gh`, you must use the appropriate template from `.github/ISSUE_TEMPLATE/`; read the available templates first, select the one that fits (e.g. `bug-report.md` for bugs, `feature-request.md` for new features or tasks), and populate all sections in the template body — passing a bare description without following the template structure is not acceptable
- Before committing, copy the current session's `.jsonl` file into `doc/content/agent/<issue-number>/`. For Claude Code sessions the file is the most recently modified `.jsonl` under `~/.claude/projects/<repo-slug>/`; for Codex sessions check the equivalent Codex session directory. Do not remove old session files already in that directory — append the new one alongside them.

## Committing
- Commit at minimum after: every input file that successfully runs, every test that passes, and every new class added
- Keep every commit passing, so that `git bisect` can test each one. If a change makes a test fail, commit the change and its fix (for example, a regold) together. Include the full error message of the failure in that commit body.
- Every commit must reference the associated GitHub issue (e.g. `Refs #<issue-number>` or `Closes #<issue-number>` as appropriate) in the commit message
- **Every commit must include an updated copy of the session `.jsonl`** — before staging, copy the current session file from `~/.claude/projects/<repo-slug>/<session-id>.jsonl` to `doc/content/agent/<issue-number>/` and stage it; this is a critical SQA requirement. Do not remove session files already present in that directory — if multiple Claude/Codex sessions contribute to the same branch and issue, all session files must be kept.
- Every commit must include these trailers:
```
Refs #<issue-number>
AI-assisted: true
AI-model: <model name>
AI-version: <model version>
Co-Authored-By: <model name> <noreply@anthropic.com>
```

## Pull requests
- If the linked issue already contains a complete Reason/Design/Impact description, the PR body should contain only the closing reference (e.g. `Closes #<issue-number>`) — do not duplicate the issue content or leave template sections empty
- If the PR introduces physics/modeling decisions, non-obvious AI reasoning, or tests not described in the issue, add those as a short addendum below the issue reference
- Never merge autonomously

## Never do
- Modify existing passing tests without explicit user instruction
- Modify the build system without explicit user instruction
- Make physics modeling decisions without flagging them to the user
- Suppress or bypass test failures
