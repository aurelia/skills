# Aurelia Skills

Agent skills for building and maintaining Aurelia applications.

This repository currently ships one skill:

- `skills/aurelia2` - Aurelia 2 application development, scaffolding, routing, dependency injection, templates, testing, SSR, prerendering, the first-party plugins (HTTP/fetch-client, validation, dialog, state, i18n), and review guidance.

The `skills/aurelia2` folder is the canonical skill. The root plugin manifests are packaging only, so Claude Code, Codex, and other compatible agents can discover the same skill without duplicate copies.

## Install in Codex

Install the skill directly from GitHub:

```bash
python3 ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo aurelia/skills \
  --path skills/aurelia2
```

Restart Codex after installing so the skill is loaded.

Codex can also add this repository as a plugin marketplace:

```bash
codex plugin marketplace add aurelia/skills
```

Then install or enable the `aurelia-skills` plugin from the Codex plugin UI.

## Install in Claude Code

For one session, load the repository checkout as a plugin:

```bash
claude --plugin-dir /path/to/skills
```

To use the repository as a Claude Code marketplace:

```bash
claude plugin marketplace add aurelia/skills
claude plugin install aurelia-skills@aurelia-skills
```

Restart Claude Code after installing or updating plugins.

## Manual Install

Copy the skill folder into your local skills directory:

```bash
mkdir -p ~/.codex/skills ~/.claude/skills
cp -R skills/aurelia2 ~/.codex/skills/aurelia2
cp -R skills/aurelia2 ~/.claude/skills/aurelia2
```

## Validate

The skill has been checked with the local Codex skill validator and Claude plugin validator. If you have those tools installed, you can run:

```bash
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/aurelia2
python3 ~/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py .
claude plugin validate .
```

## License

MIT
