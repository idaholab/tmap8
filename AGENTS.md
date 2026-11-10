# AGENTS.md

## Environment
- Ask the user if you need to load a MOOSE conda environment, and if so, what the name of the conda environment is
- If `./tmap8-opt` or `run_tests` throws an error, stop and ask the user
- Pre-commit hooks run formatting and input file validation on every `git commit`, but do not rely on them alone. Run formatters (`black` per `pyproject.toml`, `clang-format` per `.clang-format`, `hit format`) only immediately before committing, never after each edit during development, and fix any reformatting the hooks request before retrying the commit
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

## Verification and validation (V&V) and simulations
- Before adding or updating any V&V case, read `doc/content/verification_and_validation/verification_and_validation_standards.md` and follow it for input files, Python scripts, tests specifications, and documentation pages
- Apply the relevant parts of those standards (comprehensive comments, constants declared at the top, documented units, streamlined input files via CLI arguments, Python scripts that compute analytical solutions directly, quantified comparison metrics such as RMSPE, standardized physical constants) when developing or updating any other TMAP8 simulation
- Flag to the user any place where the standards cannot be followed, and why

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

## Committing
- Commit at minimum after: every input file that successfully runs, every test that passes, and every new class added
- Keep every commit passing, so that `git bisect` can test each one. If a change makes a test fail, commit the change and its fix (for example, a regold) together. Include the full error message of the failure in that commit body.
- Every commit must reference the associated GitHub issue (e.g. `Refs #<issue-number>` or `Closes #<issue-number>` as appropriate) in the commit message
- Before committing any physics or modeling change, review the proposed change with the user and wait for confirmation unless explicitly told otherwise, so the model implemented is the one the user expects
- Before committing any new or changed code, input file, test, or documentation, run an independent agent to adversarially review it and verify comments and claims by running the case or writing throwaway tests, rather than trusting the code or comments as written
- Never push to a remote unless the user asks for it or approves it
- Formatting happens only as a pre-commit step, not while editing: right before committing, format the changed files (Python with `black`, C++ with `clang-format`, input files with `hit format`), verify with `black --check`, `clang-format --dry-run --Werror` and `hit check`, then stage the formatted files
- Every commit must include these trailers:
```
Refs #<issue-number>
AI-assisted: true
AI-model: <model name>
AI-version: <model version>
Co-Authored-By: <model name> <email>
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
