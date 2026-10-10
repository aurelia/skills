---
name: aurelia2
description: Build, debug, test, review, and migrate Aurelia 2 applications. Use for Aurelia components, templates, routing, dependency injection, observation, and first-party plugins, or when scaffolding an Aurelia 2 app.
---

# Aurelia 2

Use the application's installed Aurelia version and conventions. This skill targets application development; framework contributions follow the Aurelia repository's own `AGENTS.md` files.

## Start with the project

Read the applicable project instructions, `package.json`, lockfile, TypeScript and bundler configuration, app entry point, and a representative component. Identify the router package before changing navigation.

For existing apps, preserve the bundler, CSS approach, test runner, and component conventions. Do not add routing, styling libraries, state management, or test tooling unless the task needs them. For reviews, report findings before changing code unless fixes were requested.

Check version-sensitive APIs against installed declarations and the corresponding official release. The verified baseline is Aurelia `2.0.0-rc.2` (2026-10-10); it is not an instruction to upgrade an existing app. Keep directly used Aurelia core packages on matching releases. Separately versioned integrations such as Storybook follow their own peer dependencies.

Official sources:

- [Aurelia documentation](https://docs.aurelia.io/)
- [Developing with AI](https://docs.aurelia.io/developer-guides/developing-with-ai)
- [Release history](https://github.com/aurelia/aurelia/releases)
- [Source and declarations](https://github.com/aurelia/aurelia)

Docs and `master` can describe unreleased behavior. If they disagree with the installed package, inspect the matching tag or package declarations before generating code. Do not copy framework-repository build commands into an application that has different scripts.

## Read the reference for the task

Load only the relevant files:

| Task | Reference |
| --- | --- |
| Create an app or configure Vite/TypeScript | [scaffolding.md](references/scaffolding.md) |
| Choose official generator options | [cli.md](references/cli.md) |
| Components, bindables, lifecycle, custom attributes | [components.md](references/components.md) |
| Bindings, lists, slots, composition, converters | [templates.md](references/templates.md) |
| Routes, parameters, navigation, route hooks | [routing.md](references/routing.md) |
| DI, observation, services, event subscriptions | [reactivity.md](references/reactivity.md) |
| Form controls and submission | [forms.md](references/forms.md) |
| Component tests, fixtures, async assertions | [testing.md](references/testing.md) |
| Storybook configuration and stories | [storybook.md](references/storybook.md) |
| Diagnose runtime or template failures | [troubleshooting.md](references/troubleshooting.md) |
| HTTP requests and interceptors | [fetch-client.md](references/fetch-client.md) |
| Form/model validation | [validation.md](references/validation.md) |
| Dialogs | [dialog.md](references/dialog.md) |
| Shared state | [state.md](references/state.md) |
| Translations and locale formatting | [i18n.md](references/i18n.md) |
| Port an Aurelia 1 application | [migration.md](references/migration.md) |
| Enhance existing/server-rendered HTML | [enhancement.md](references/enhancement.md) |

## Essential rules

- Use `.trigger` for events and `:prevent` when the browser's default action must be prevented, especially form submission. `.delegate` belongs only to the temporary v1 compatibility shim.
- Use `.bind`, `.to-view`, `.from-view`, `.two-way`, or `.one-time`; do not generate `.one-way`.
- For standard-decorator TypeScript projects, leave `experimentalDecorators` and `emitDecoratorMetadata` disabled. Prefer `resolve()` in class fields or constructors; `static inject` is valid. Parameter decorators and `@autoinject` are not the standard-decorator path.
- Register template resources with local `<import>`, component `dependencies`, or app registration. A matching filename does not make a resource globally available.
- The outer `<template>` wrapper is optional. Use `<au-slot>` for light-DOM projection and native `<slot>` with Shadow DOM.
- Use `binding`, `bound`, `attaching`, `attached`, `detaching`, and `unbinding`. Do not generate the removed `define` hook. Keep property names distinct from component and route hooks (`isLoading`, not a boolean `loading`).
- Read element refs from `bound()` onward; use `attached()` when the element must be in the document. Dispose owned subscriptions/listeners when their lifetime ends, and recreate them on rebind when appropriate.
- Plain bound properties and getters are observed automatically. Use `@observable` for change callbacks and `@watch` for specific observation work, not as a blanket fix for stale views.
- Key refreshed lists with `repeat.for="item of items; key: id"`. Keep binding expressions free of mutations; sort a copy or expose a derived property.
- Use default `aurelia()` Vite configuration for normal builds. Force `useDev: true` only for a deliberate diagnostic build, then restore the normal configuration.

## Verify the result

Use the app's own build, typecheck, and focused test commands. A successful TypeScript check alone does not prove that a template compiles or a route works. For interactive changes, exercise the affected behavior in a browser or component fixture, including the relevant failure path.

For routing changes, check direct navigation/refresh, relative links, back navigation, and the deployment base path. For forms, check submit prevention and validation. For lifecycle work, check removal and reattachment. Report what actually ran and any remaining limits.

For documentation-only work, validate the guidance and links without inventing an application build requirement.
