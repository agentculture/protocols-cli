# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Agent identity

This repo hosts the **protocols-cli** agent — an AgentCulture mesh peer whose
domain is **Culture Protocols**: a workflow system in which agents, bots and
humans describe how work is done, by whom, and under a verifiable contract.
The intended surface is authoring, versioning and validating protocol
definitions, then checking a completed run against the contract it promised.

**None of that domain logic exists yet.** The repo was scaffolded from
`culture-agent-template` (commit `63fe68d`) and currently ships only the
template's agent-first CLI skeleton plus the vendored skill kit. When adding
protocol features, add them as new noun groups under `protocols/cli/_commands/`
(see "Adding a command" below) — do not assume any protocol code is present.

Identity lives in `culture.yaml`: `suffix: protocols-cli`, `backend: colleague`,
model `sakamakismile/Qwen3.6-27B-Text-NVFP4-MTP`. Because the backend is
`colleague`, the *resident* prompt file that `doctor` and `steward doctor`
require is **`AGENTS.colleague.md`**, not this file. This file is the Claude Code
guidance file; both must exist.

## Commands

```bash
uv sync                                  # install (dev group included)
uv run pytest -n auto                    # full suite (parallel)
uv run pytest tests/test_cli.py::test_whoami_json -v   # single test
uv run pytest --cov=protocols --cov-report=term        # coverage (fail_under=60)
uv run teken cli doctor . --strict       # agent-first rubric gate — CI blocks on this
```

Lint, exactly as CI runs it:

```bash
uv run black --check protocols tests
uv run isort --check-only protocols tests
uv run flake8 protocols tests
uv run bandit -c pyproject.toml -r protocols
markdownlint-cli2 "**/*.md" "#node_modules" "#.local" "#.claude/skills" "#.teken"
```

**The installed console script is `protocols`, not `protocols-cli`.** The dist
name, the argparse `prog`, and every string in the help/explain/learn text say
`protocols-cli`, but `[project.scripts]` binds `protocols`. So it's
`uv run protocols whoami`, and the README documents it that way. This split is
deliberate for now — don't "fix" it by rewriting the `protocols-cli` prose,
which the rubric and tests assert on. Closing it properly means changing the
`[project.scripts]` key, which renames the installed command for anyone who has
already installed the package.

## Architecture

A single Python package, `protocols/`, no `src/` wrapper, **zero runtime
dependencies** (everything is stdlib — including a hand-rolled `culture.yaml`
line parser in `whoami.py`, deliberately, to keep deps empty). Keep it that way.

The CLI is built to satisfy the **agent-first rubric** enforced by
`teken cli doctor --strict`. That gate is why the surface looks the way it does,
and it is the constraint most likely to bite you:

- `protocols/cli/__init__.py` — argparse wiring. `_CliArgumentParser` overrides
  `.error()` so even *parse-time* failures render as the structured
  `error:` / `hint:` pair instead of argparse's default. Since `args.json`
  doesn't exist yet at parse time, `main()` pre-scans raw argv for `--json` and
  stashes it on the class-level `_json_hint`. `_dispatch()` wraps any
  non-`CliError` exception so no traceback ever reaches stderr.
- `protocols/cli/_errors.py` — `CliError(code, message, remediation)` plus the
  exit-code policy: `0` success, `1` user error, `2` environment error, `3+`
  reserved. Every failure path raises `CliError`; nothing else.
- `protocols/cli/_output.py` — the hard split: **results to stdout, errors and
  diagnostics to stderr, never mixed**, in both text and JSON mode.
- `protocols/cli/_commands/*.py` — one module per verb/noun, each exposing
  `register(sub)`.
- `protocols/explain/catalog.py` — markdown docs keyed by command-path tuple.
  `explain` is *global* and path-addressable, distinct from `--help`.

Rubric obligations to preserve when you extend the CLI:

- every command accepts `--json`;
- `learn` stays ≥200 chars and keeps mentioning purpose, command map, exit
  codes, `--json`, and `explain`;
- descriptive verbs (`overview`) must **not** hard-fail on a bogus target — hence
  `overview`'s ignored optional `target` positional;
- any noun group carrying action-verbs must also expose `<noun> overview`
  (that is the entire reason `cli.py` exists);
- an unknown `explain` path must exit 1 *with* a hint.

### Adding a command

1. New module in `protocols/cli/_commands/` with a `register(sub)` that adds a
   `--json` flag and `set_defaults(func=...)`.
2. Call it from `_build_parser()` (there's a marked spot for noun groups).
3. Add a catalog entry in `protocols/explain/catalog.py` — every registered
   noun/verb should be explainable.
4. Update the command maps in `learn.py` (both `_TEXT` and `_as_json_payload`)
   and the verb lists in `overview.py`, plus the README table.
5. For a noun group with action-verbs, add its `overview` sub-verb.
6. Propagate the subparser class: `p.add_subparsers(parser_class=type(p))`, so
   nested parse errors route through the structured contract (see `cli.py`).

## Version and PR workflow

**Every PR bumps the version — even docs, config, or CI-only changes.** The
`version-check` CI job compares `pyproject.toml` against `origin/main` and fails
(with a PR comment) when they match. Use the `version-bump` skill, which bumps
`pyproject.toml` and prepends a Keep-a-Changelog entry to `CHANGELOG.md`.
Publishing is PyPI Trusted Publishing: a PR touching `pyproject.toml` or
`protocols/**` publishes a `.devN` build to TestPyPI, and the merge to `main`
publishes for real — an unbumped version means a failed publish.

Use the `cicd` skill for the PR lane (open/read/reply/status/await; it wraps
`devex pr` and gates on the SonarCloud quality gate + unresolved threads). PR
replies are auto-signed `- protocols-cli (Claude)` by `pr-reply.sh` — don't sign
manually in the body. For anything the scripts don't author (a manual
`gh pr create --body`), sign explicitly as `- protocols-cli (Claude)`.

## Vendored skills — cite-don't-import

`.claude/skills/` is **vendored verbatim** from sibling repos (guildmaster,
devague, colleague, eidetic-cli); provenance and per-skill re-sync commands live
in `docs/skill-sources.md`, which is the authoritative ledger.

Do not patch a vendored skill locally to fix a review finding — fix it upstream
in its origin repo and re-vendor. A local patch is silently reverted by the next
re-sync, and it destroys `diff -r` against the origin as a check. The ledger
records the few deliberate exceptions (the `agex` → `devex` rename; skills
vendored directly from devague/colleague rather than guildmaster) — extend that
list rather than adding a silent one. These paths are excluded from
markdownlint and Sonar for the same reason.

`type: command` in each `SKILL.md` frontmatter is load-bearing: the culture
backend's `core.skill_loader` silently skips any skill lacking it, so re-add it
when an upstream copy omits it.

Optional tools some skills expect on PATH: `devex` (>=0.21), `agtag` (>=0.1),
`colleague`, `eidetic` (>=0.10.0).

## Conventions

- **Memory discipline** — `/recall` before non-trivial work rather than
  re-deriving prior decisions; `/remember` when a non-obvious decision,
  constraint, fix-and-why, or gotcha surfaces. The wrappers here default
  `--visibility public`, which routes records to the in-repo, committed
  `.eidetic/memory`; pass `--visibility private` to keep one in `$HOME`.
- **Reach for `ask-colleague` reflexively** — `review` and `explore` are
  read-only (throwaway worktree, no side effects), so running them before
  presenting a non-trivial diff is always safe. The side-effecting
  `write --apply` / `write --pr` needs the user's go-ahead first.
- **Worktrees** live in `../.worktrees.protocols-cli/<name>/` — one repo-named
  directory beside the checkout, never a shared `../worktrees/`. Scope branch
  prefixes to the work; bare `agent/*` collides with leftovers from earlier
  fan-outs and fails `git worktree add -b`. The vendored `assign-to-workforce`
  skill's example uses the old shared path and `agent/<task-id>` branches — it
  is cited verbatim and must not be edited, so override both when following it.
  `git worktree remove <path>` is what actually deletes a tree; `prune` only
  clears metadata.
- Line length 100 (black, isort `profile = "black"`, flake8 agree).
