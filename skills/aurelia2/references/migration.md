# Migrating Aurelia 1 → Aurelia 2

Read this when porting an Aurelia 1 (v1) app to Aurelia 2, or when reviewing a codebase that is
part-way through that migration. Use the tables below as a quick reference, then follow the relevant steps within the agreed migration scope.

The migration story is **incremental**: stand up a v2 shell, register the `@aurelia/compat-v1`
shims so most v1 syntax keeps working, then modernize file-by-file and remove the shims at the end.

Use v2 syntax for new components. Keep compatibility shims while existing code still depends on them, then remove each shim after the corresponding migration is verified. A request to fix one component does not authorize migrating the whole application.

## `@aurelia/compat-v1` — the temporary escape hatch

`@aurelia/compat-v1` restores a set of v1 behaviors so a freshly-ported app runs before every
file is modernized. It is **temporary** — treat its presence as a migration TODO and aim to remove
it. Register the single `compatRegistration` export:

```typescript
import Aurelia from 'aurelia';
import { compatRegistration } from '@aurelia/compat-v1';
import { MyApp } from './my-app';

Aurelia
  .register(compatRegistration)
  .app(MyApp)
  .start();
```

What it restores (each is something v2 changed or removed):

- **`.delegate` event binding** — v2 removed event delegation; compat re-adds the `.delegate`
  command. Modern code uses `.trigger`.
- **Automatic `preventDefault()`** — v1 called `preventDefault()` on handled events; v2 does not.
  Compat restores the old default. Modern code opts in per-event with `.trigger:prevent`.
- **`.call` binding command** — for passing a callback expression. Modern code passes a function
  reference or an arrow, or uses `.trigger`.
- **`BindingEngine`** — v1's `propertyObserver`/`collectionObserver`/`expressionObserver` API.
  Modern code resolves `IObserverLocator`. Note the collection-observer callback differs (v1
  `splices` vs v2 `indexMap`), so collection observers may still need hand-porting.
- **`@computedFrom`** — explicit computed-dependency decorator. In v2, plain getters are tracked
  automatically; only keep `@computedFrom` (from compat) when you need to override that.
- **`@noView` / `@inlineView`** — replaced by the `template` option on `@customElement`.
- **`<au-compose>` v1 bindable names** — accepts `view-model`/`view` aliases in addition to the
  v2 `component`/`template`.

## Bootstrapping

v1 used a `configure(aurelia)` function and `PLATFORM.moduleName(...)`:

```typescript
// v1 main.ts
export function configure(aurelia) {
  aurelia.use.standardConfiguration();
  aurelia.start().then(() => aurelia.setRoot(PLATFORM.moduleName('app')));
}
```

v2 is direct and imperative — see [scaffolding.md](scaffolding.md):

```typescript
// v2 main.ts
import Aurelia from 'aurelia';
import { RouterConfiguration } from '@aurelia/router';
import { MyApp } from './my-app';

Aurelia
  .register(RouterConfiguration.customize({ useUrlFragmentHash: false }))
  .app(MyApp)
  .start();
```

- `aurelia-app="main"` on `<body>` → a root component element (`<my-app></my-app>`).
- `setRoot(PLATFORM.moduleName('app'))` → `.app(MyApp)` with the class.
- `standardConfiguration()` → register only what the app uses.
- `PLATFORM.moduleName('x')` everywhere → direct `import` / dynamic `import()`.
- Global resources: `globalResources([...])` → `Aurelia.register(...)` (import a barrel module of
  resources and register it).

## Templates

| v1 | v2 |
|----|----|
| `click.delegate="fn()"` | `click.trigger="fn()"` |
| (implicit preventDefault) | `click.trigger:prevent="fn()"` when needed |
| `<require from="x">` | `<import from="x">` |
| `<compose view-model.bind view.bind>` | `<au-compose component.bind template.bind>` |
| `<slot>` (light DOM), `<replaceable>`/`<replace>` | `<au-slot>` |
| `<router-view>` | `<au-viewport>` |
| `value.one-way="x"` | `value.to-view="x"` |
| `view-model.ref="vm"` | `component.ref="vm"` |
| `.call` bindings | function reference / arrow / `.trigger` |

`one-time`, `two-way`, `from-view`, `${interpolation}`, `repeat.for`, `if`/`else`, `with`,
`as-element`, `containerless`, and `& bindingBehavior` syntax are unchanged. v2 adds niceties like
`active.class="isActive"` and lambda expressions in templates (`items.filter(x => x.ok)`).

## Components, lifecycle & DI

Lifecycle hook renames (see [components.md](components.md) for the full v2 order):

| v1 | v2 |
|----|----|
| `bind()` | `binding()` (may return a Promise to block children) |
| — | `bound()` (new — `ref`/`from-view`/`let` available) |
| `attached()` | `attaching()` (new, pre-attach, can animate) then `attached()` |
| `detached()` | `detaching()` |
| `unbind()` | `unbinding()` |
| — | `dispose()` (new — final teardown) |

Dependency injection:

```typescript
// v1
import { autoinject } from 'aurelia-framework';
@autoinject
export class UserList {
  constructor(private http: HttpClient) {}
}

// v2 — resolve() class field (see reactivity.md)
import { resolve } from 'aurelia';
import { IHttpClient } from '@aurelia/fetch-client';
export class UserList {
  private http = resolve(IHttpClient);
}
```

`@autoinject` is removed; `@inject` on constructor parameters does not work with TC39 decorators.
Use `resolve()` (preferred) or `static inject`. `@bindable`, `@customElement`, `@customAttribute`,
`@valueConverter`, `@bindingBehavior` decorators are unchanged.

`@computedFrom('a', 'b')` getters → plain getters (v2 tracks dependencies automatically).

## Router

v1 `configureRouter()` with `moduleId` strings → the declarative `@route` decorator with dynamic
`import()` (see [routing.md](routing.md)). Outlet `<router-view>` → `<au-viewport>`. Navigation
`router.navigateToRoute(name, params)` → `router.load(...)`.

Router lifecycle hook renames:

| v1 | v2 |
|----|----|
| `canActivate(params, config, nav)` | `canLoad(params, next, current, options)` |
| `activate(params, config, nav)` | `loading(params, next, current, options)` |
| `canDeactivate()` | `canUnload(next, current, options)` |
| `deactivate()` | `unloading(next, current, options)` |

Return a redirect (e.g. `'/login'` or a navigation instruction) from `canLoad` instead of v1's
redirect patterns. Implement `IRouteViewModel` for intellisense.

## Plugin authors

A v1 plugin exported `configure(config)` and called `config.globalResources([...])`. A v2 plugin
is a plain object (or class) with a `register(container)` method:

```typescript
import { IContainer } from 'aurelia';
import { MyComponent } from './components/my-comp';
import { MyValueConverter } from './resources/my-vc';

export const MyPlugin = {
  register(container: IContainer) {
    container.register(MyComponent, MyValueConverter);
  },
};

// consumer: Aurelia.register(MyPlugin).app(MyApp).start();
```

Add a `customize(options)` that returns a configured registry when the plugin needs options
(mirror the `RouterConfiguration.customize(...)` shape).

## Recommended strategy

1. **Scaffold a v2 shell** (`npx makes aurelia` — see [cli.md](cli.md)) and rewrite `main.ts`.
2. **Register `compatRegistration`** and copy the v1 `src/` over; most templates keep working.
3. **Routing first** — convert `configureRouter` → `@route`, rename router hooks, `<router-view>`
   → `<au-viewport>`. The app needs this to navigate.
4. **Templates & events** — `<require>`→`<import>`, `.delegate`→`.trigger` (+ `:prevent` where the
   v1 default mattered), `<compose>`→`<au-compose>`.
5. **Components & DI** — rename lifecycle hooks, `@autoinject`→`resolve()`, drop `@computedFrom`.
6. **Observation & cleanup** — port `BindingEngine` usage to `IObserverLocator`; remove
   `compat-v1` once nothing depends on it, then drop the dependency.

When reviewing a partial migration, report remaining v1 patterns and compatibility registrations. A scoped migration can intentionally retain shims; remove them only after the dependent code has been ported and verified.

## Sources

- [Official migration guide](https://docs.aurelia.io/migrating-to-aurelia-2/cheat-sheet)
- [Compatibility package](https://github.com/aurelia/aurelia/tree/v2.0.0-rc.2/packages/compat-v1)
