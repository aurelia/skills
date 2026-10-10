# Aurelia Skills

Agent skills for building and maintaining Aurelia applications.

This repository currently ships one skill:

- [Aurelia 2](skills/aurelia2/SKILL.md) covers application development, scaffolding, routing, dependency injection, templates, testing, migration, and first-party plugins. Its short entry point directs agents to the references needed for each task.

The guidance uses official Aurelia documentation and source. The current compatibility baseline is Aurelia `2.0.0-rc.2`, checked on 10 October 2026. Agents should check installed versions before applying version-sensitive examples.

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

Run the portable repository check with Python 3; no installed agent tools or packages are required:

```bash
python3 scripts/validate.py
```

It checks local Markdown links, reference discoverability, code fences, the required skill fields, and plugin manifest consistency. GitHub Actions runs the same check on pushes and pull requests. It does not compile the embedded application examples or check external URLs.

If installed, also run the agent-specific validators:

```bash
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/aurelia2
claude plugin validate .
```

## Maintaining the guidance

Keep shared constraints in `SKILL.md` and task-specific detail in `references/`. Link new references from the entry point. Prefer official docs, release tags, and published package declarations when checking an API; the framework's master branch may contain unreleased features.

When refreshing compatibility guidance, check the generator, core package versions, and integration peer dependencies together. Update the verification date after checking them. Exercise changed runtime examples in a small application or fixture where static validation cannot establish correctness. Keep both plugin manifest versions aligned.

## License

MIT
