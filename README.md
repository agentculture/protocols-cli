# protocols-cli

Maintains **Culture Protocols** — a workflow system in which agents, bots and
humans describe how work is done, by whom, and under a verifiable contract.
The intended surface is authoring, versioning and validating protocol
definitions, then checking a completed run against the contract it promised.

> **Status: scaffold.** The protocol surface described above is not built yet.
> What ships today is the agent-first CLI skeleton, the mesh identity, and the
> vendored skill kit — see [What's here](#whats-here). Protocol verbs arrive as
> new noun groups under `protocols/cli/_commands/`.

## What's here

- **An agent-first CLI** cited from [teken](https://github.com/agentculture/teken)
  (`afi-cli`) — the runtime package has no third-party dependencies.
- **A mesh identity** — `culture.yaml` (`suffix: protocols-cli`,
  `backend: colleague`) and the matching resident prompt file
  `AGENTS.colleague.md`.
- **18 vendored skills** under `.claude/skills/`, cited-not-imported from
  guildmaster, devague, colleague and eidetic-cli. See
  [`docs/skill-sources.md`](docs/skill-sources.md) for provenance and re-sync
  commands.
- **A build + deploy baseline** — pytest, lint, the agent-first rubric gate, and
  PyPI Trusted Publishing wired into GitHub Actions.

## Quickstart

```bash
uv sync
uv run pytest -n auto                 # run the test suite
uv run protocols whoami               # identity from culture.yaml
uv run protocols learn                # self-teaching prompt (add --json)
uv run teken cli doctor . --strict    # the agent-first rubric gate CI runs
```

> **The installed command is `protocols`.** The distribution, the argparse
> `prog`, and the CLI's own help and `explain` text all say `protocols-cli`;
> only `[project.scripts]` binds the shorter `protocols`. Invoke `protocols`,
> read `protocols-cli` in the output.

## CLI

| Verb | What it does |
|------|--------------|
| `whoami` | Report this agent's nick, version, backend, and model from `culture.yaml`. |
| `learn` | Print a structured self-teaching prompt. |
| `explain <path>` | Markdown docs for any noun/verb path. |
| `overview` | Read-only descriptive snapshot of the agent. |
| `doctor` | Check the agent-identity invariants (prompt-file-present, backend-consistency). |
| `cli overview` | Describe the CLI surface itself. |

Every command supports `--json`. Results go to stdout, errors/diagnostics to
stderr (never mixed). Exit codes: `0` success, `1` user error, `2` environment
error, `3+` reserved.

## Development

Every PR bumps the version — the `version-check` CI job fails when
`pyproject.toml` matches `main`. Lint locally the way CI does:

```bash
uv run black --check protocols tests
uv run isort --check-only protocols tests
uv run flake8 protocols tests
uv run bandit -c pyproject.toml -r protocols

# markdownlint comes from npm, not the dev group — install once, pinned to the
# version CI uses:
npm install -g markdownlint-cli2@0.21.0
markdownlint-cli2 "**/*.md" "#node_modules" "#.local" "#.claude/skills" "#.teken"
```

See [`CLAUDE.md`](CLAUDE.md) for the full conventions — the rubric obligations
that shape the CLI, how to add a command, the PR lane, and the
cite-don't-import rule for `.claude/skills/`.

## License

Apache 2.0 — see [`LICENSE`](LICENSE).
