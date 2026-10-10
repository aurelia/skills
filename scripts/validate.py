#!/usr/bin/env python3
"""Validate local skill references and plugin packaging without installed agent tools."""

import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit


def validate(root):
    errors = []
    skill = root / 'skills/aurelia2/SKILL.md'
    markdown = [root / 'README.md', *sorted((root / 'skills').rglob('*.md'))]
    links = {}

    for path in markdown:
        text = path.read_text()
        label = path.relative_to(root)
        if sum(line.startswith('```') for line in text.splitlines()) % 2:
            errors.append(f'{label}: unclosed code fence')
        # Ignore examples when finding documentation links.
        prose = re.sub(r'^```[^\n]*\n.*?^```\s*$', '', text, flags=re.M | re.S)
        links[path.resolve()] = []
        for target in re.findall(r'\[[^\]]+\]\(([^\s)]+)\)', prose):
            url = urlsplit(target)
            if url.scheme or url.netloc or not url.path:
                continue
            resolved = (path.parent / unquote(url.path)).resolve()
            if not resolved.exists():
                errors.append(f'{label}: missing link target {target}')
            links[path.resolve()].append(resolved)

    text = skill.read_text()
    frontmatter = re.match(r'\A---\n(.*?)\n---\n', text, re.S)
    if not frontmatter:
        errors.append('SKILL.md: missing YAML frontmatter')
    else:
        # This repository uses plain single-line name and description fields.
        fields = dict(re.findall(r'^(name|description): (.+)$', frontmatter[1], re.M))
        if fields.get('name') != skill.parent.name:
            errors.append('SKILL.md: name must match the skill directory')
        if not fields.get('description', '').strip():
            errors.append('SKILL.md: missing description')

    reachable = set()
    pending = [skill.resolve()]
    while pending:
        path = pending.pop()
        if path in reachable:
            continue
        reachable.add(path)
        pending.extend(links.get(path, []))
    for reference in (skill.parent / 'references').glob('*.md'):
        if reference.resolve() not in reachable:
            errors.append(f'{reference.relative_to(root)}: not linked from the skill')

    manifests = {}
    for folder in ['.codex-plugin', '.claude-plugin', '.agents/plugins']:
        for path in (root / folder).glob('*.json'):
            try:
                manifests[str(path.relative_to(root))] = json.loads(path.read_text())
            except json.JSONDecodeError as error:
                errors.append(f'{path.relative_to(root)}: {error}')

    codex = manifests.get('.codex-plugin/plugin.json', {})
    claude = manifests.get('.claude-plugin/plugin.json', {})
    for field in ['name', 'version']:
        if not codex.get(field) or codex.get(field) != claude.get(field):
            errors.append(f'Plugin manifests must have matching {field} values')
    if not re.fullmatch(r'\d+\.\d+\.\d+', str(codex.get('version', ''))):
        errors.append('Plugin version must use major.minor.patch')
    if codex.get('skills') != './skills/':
        errors.append('Codex plugin must expose the canonical ./skills/ directory')
    for name in ['.claude-plugin/marketplace.json', '.agents/plugins/marketplace.json']:
        plugins = manifests.get(name, {}).get('plugins', [])
        if len(plugins) != 1 or plugins[0].get('name') != codex.get('name'):
            errors.append(f'{name}: expected the canonical plugin entry')

    return errors, len(markdown), len(manifests)


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[1]
    errors, documents, manifests = validate(root)
    if errors:
        print('\n'.join(errors), file=sys.stderr)
        sys.exit(1)
    print(f'Validated {documents} Markdown files and {manifests} plugin manifests; no errors.')
