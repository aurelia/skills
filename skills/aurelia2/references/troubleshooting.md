# Debugging & Troubleshooting

Read this when Aurelia 2 code "doesn't work" — especially silent failures (no error, wrong
behavior) and coded `AURxxxx` errors. The fastest path is usually the triage checklist at the end.

## Silent failures (no error thrown, wrong behavior)

These are the most common traps because nothing crashes — the binding just sits there.

| Symptom | Cause | Fix |
|---------|-------|-----|
| A custom element renders nothing / a custom attribute does nothing / a value converter prints the raw value | The resource isn't registered in scope | Add `<import from="./x">`, list it in the component's `dependencies`, or register it globally in `main.ts` |
| Array change doesn't update the view | Direct index assignment (`arr[0] = x`) or `arr.length = 0` isn't observable | Use `push`/`splice`/`pop`/`shift` or replace the reference (`this.items = [...]`) |
| A plain property change does not update the view | Wrong binding scope, one-time mode, or an untracked dependency | Bound properties are observed automatically; inspect the binding and object instance before adding decorators |
| A lifecycle or route hook never runs | A class property shadows the method name (e.g. `loading = true` overwrites the `loading()` route hook) | Rename the property (`isLoading`). Applies to `binding`/`bound`/`attached`/`loading`/`canLoad`/etc. |
| `ref` element is `undefined` | Accessed in `constructor`/`binding` | Read refs in `bound()` or later; do DOM work in `attached()` |
| SVG attribute bindings (`cx`, `r`, `d`, `viewBox`) silently do nothing | `SVGAnalyzer` not registered | Register `SVGAnalyzer` from `@aurelia/runtime-html` in `main.ts` |
| `click.delegate` (and other `.delegate`) does nothing | `.delegate` was removed in v2 | Use `.trigger` |
| Two-way binding to a custom element doesn't flow back | The target property isn't `@bindable`, or the mode is to-view | Mark it `@bindable` and use `.bind`/`.two-way` |
| A form reloads the page on submit | `submit.trigger` does **not** preventDefault by default | Use `submit.trigger:prevent="..."` (see [forms.md](forms.md)) |

## Reading `AURxxxx` errors

Aurelia throws coded errors. In a **dev build** (`aurelia({ useDev: true })` in `vite.config.ts`)
the message is expanded with a human-readable description and a docs link. In a **production
build** you get a terse `AURxxxx:param1:param2` — look the code up in the core docs under
`developer-guides/error-messages/` (grouped by code range), or search the framework's `errors.ts`
files. When you hit a code you don't recognize, switch to a dev build first to get the full text.

Rough map of where codes come from (range → package):

- `AUR00xx` — `@aurelia/kernel` (dependency injection): no registration found, cyclic dependency,
  `resolve()` called with no active container.
- `AUR01xx` — `@aurelia/runtime-html` (binding/resources): binding behavior / value converter not
  found (usually an unregistered/typo'd resource).
- `AUR07xx` — `@aurelia/template-compiler` (template compilation): unknown binding command,
  malformed template, binding to a non-bindable.
- `AUR3xxx` — `@aurelia/router`. `AUR5xxx` — `@aurelia/fetch-client`.

Don't trust a specific number from memory — confirm it against the dev-build message or the docs.

## Debugging techniques

**Lifecycle logging** — confirm a hook runs and see ordering:

```typescript
import { resolve } from 'aurelia';
import { ILogger } from '@aurelia/kernel';

export class MyComponent {
  private log = resolve(ILogger).scopeTo('MyComponent');
  binding() { this.log.debug('binding'); }
  attached() { this.log.debug('attached'); }
}
```

**Inspect a live component** using `CustomElement` imported from `aurelia` and its host element:

```javascript
// From application/debug code where the public API is imported:
const controller = CustomElement.for(element);
const vm = controller.viewModel;
```

**Router logging** — configure Aurelia logging with `LoggerConfiguration` and `LogLevel` from the public kernel API; check the installed router options before adding logging settings.

**Check DI resolution** — wrap a `resolve`/`container.get` in try/catch and log; "no registration"
means the service was never registered (or the key/interface doesn't match exactly), and a cyclic
dependency means two services inject each other (break the cycle or use `lazy`).

## What AI/agents struggle to debug (slow down and reason about the runtime)

Per the framework's own guidance, these need understanding of Aurelia internals rather than
pattern-matching: lifecycle **timing** problems, DI **container configuration** issues, **template
compilation** errors, and **cross-component communication**. When stuck on one of these, verify the
lifecycle order in [components.md](components.md), the registration, and the binding scope
before rewriting code.

## Quick triage checklist

1. **Nothing rendered?** Is the component imported/registered in scope? Check the console for an
   `AUR` error. Is the custom element name kebab-case and the file paired correctly?
2. **Binding not updating?** Is the binding reading the intended object and scope? Array mutated with
   `push`/`splice` (not index assignment)? Binding mode not `one-time`? Converter/behavior registered?
3. **Hook never fires?** Does a property share the hook's name (`loading`, `bound`, …)? Rename it.
4. **`ref`/DOM null?** Access in `bound()`/`attached()`, not `constructor`/`binding`.
5. **Event handler dead?** `.trigger`, not `.delegate`. Form reloading? Add `:prevent`.
6. **DI error?** Service registered? Key/interface matches exactly? No injection cycle?
7. **Still cryptic?** Switch to a dev build (`useDev: true`) to expand the `AUR` message + docs link.

Restore normal Vite configuration after forcing a diagnostic `useDev: true` build.

## Sources

- [Developing with AI](https://docs.aurelia.io/developer-guides/developing-with-ai)
- [Official error documentation](https://docs.aurelia.io/developer-guides/error-messages)
