# Testing

Aurelia 2 components are tested with **Vitest** (jsdom) + `@aurelia/testing`'s `createFixture`.
This reference covers assertions, event helpers, mocks, async behavior, and router tests. Preserve the runner already used by the app; Vitest is the example here.

## Setup

**vitest.config.ts** — merge the app's Vite config so the Aurelia plugin and aliases apply:

```typescript
import { fileURLToPath } from "node:url";
import { mergeConfig, defineConfig, configDefaults } from "vitest/config";
import viteConfig from "./vite.config";

export default mergeConfig(
  viteConfig,
  defineConfig({
    test: {
      environment: "jsdom",
      watch: false,
      exclude: [...configDefaults.exclude, "e2e/*"],
      root: fileURLToPath(new URL("./", import.meta.url)),
      setupFiles: ["./test/setup.ts"],
    },
  }),
);
```

If tests declare decorated classes outside `src/` on Vite 8, extend the existing Aurelia plugin's `standardDecoratorInclude`, for example `aurelia({ standardDecoratorInclude: ['src/**/*.{ts,js}', 'test/**/*.{ts,js}'] })`. Otherwise Oxc can leave those standard decorators untransformed. Do not register a second plugin instance in the test config.

**test/setup.ts** — set the platform once and dispose fixtures after each test. Surface cleanup failures so broken teardown does not pass silently.

```typescript
import { BrowserPlatform } from '@aurelia/platform-browser';
import { setPlatform, onFixtureCreated, type IFixture } from '@aurelia/testing';
import { beforeAll, afterAll, afterEach } from 'vitest';

const fixtures: IFixture<object>[] = [];
let tracking: { dispose(): void } | undefined;

beforeAll(() => {
  const platform = new BrowserPlatform(window);
  setPlatform(platform);
  BrowserPlatform.set(globalThis, platform);
  tracking = onFixtureCreated(fixture => { fixtures.push(fixture); });
});

afterEach(async () => {
  const results = await Promise.allSettled(
    fixtures.splice(0).filter(fixture => !fixture.torn).map(async fixture => {
      await fixture.stop(true);
    }),
  );
  const errors = results.flatMap(result => result.status === 'rejected' ? [result.reason] : []);
  if (errors.length) throw new AggregateError(errors, 'Fixture cleanup failed');
});

afterAll(() => { tracking?.dispose(); });
```

Use jsdom's storage for tests that need it, with a configured document URL. Add a storage mock only when a specific runtime incompatibility requires it, and restore globals afterward.

## `createFixture` — two forms

**Positional:** `createFixture(template, viewModelOrClass?, registrations?, autoStart?)`.

```typescript
import { createFixture } from '@aurelia/testing';

const { appHost, component, container, assertText, started, stop } = createFixture(
  '<my-component name.bind="n"></my-component>',
  class { n = 'Alice'; },
  [MyComponent],
);
await started;            // resolves AFTER async lifecycle hooks complete
assertText('Alice', { compact: true });
await stop(true);         // stop + dispose + clean up the DOM
```

**Fluent builder** — `.html` / `.component` / `.deps` / `.config` in any order, ending in
`.build()` (at least `.html` is required):

```typescript
const { component, assertText, started, stop } = createFixture
  .component(class { greeting = 'Hello'; })
  .html`<div>${(vm: any) => vm.greeting} world</div>`
  .deps(SomeDep)
  .build();
await started;
```

The fixture object exposes: `appHost` (where the component renders — query this, not `testHost`),
`component` (root view-model), `container`, `platform`, `started`, `stop`, the assertion helpers
and event helpers below, and queries `getBy(selector)` (throws unless exactly one match),
`getAllBy(selector)`, `queryBy(selector)` (one or null).

## Assertions

The fixture returns ready-made assertions (no manual querying needed):

- `assertText(text)` / `assertText(selector, text)` — text content (`{ compact: true }` collapses whitespace)
- `assertTextContain(text)` / `assertTextContain(selector, text)`
- `assertHtml(html)` / `assertHtml(selector, html)`
- `assertValue(selector, value)` — input/form value
- `assertChecked(selector, boolean)` — checkbox/radio
- `assertClass(selector, ...classes)` / `assertClassStrict(...)`
- `assertAttr(selector, name, value)` / `assertStyles(selector, styles)`

## Triggering events & input

```typescript
const { trigger, type, component, assertText, started } = createFixture(
  '<button click.trigger="inc()">+</button><span>${count}</span>',
  class { count = 0; inc() { this.count++; } },
);
await started;
trigger.click('button');
await tasksSettled();
assertText('span', '1');
```

- `trigger.click(selector)`, `trigger.change`, `trigger.input`, `trigger.keydown`, etc., plus the
  generic `trigger(selector, eventName, init?)`.
- `type(selector, value)` sets an input's value and fires `input`.

## Awaiting updates

Always `await started` before asserting. After mutating state, flush the binding queue with
`tasksSettled` (from `@aurelia/runtime`) before asserting the DOM:

```typescript
import { tasksSettled } from '@aurelia/runtime';

component.name = 'Bob';
await tasksSettled();
assertText('Bob');
```

Await `started` for async lifecycle hooks. `tasksSettled()` waits for queued framework work, not arbitrary fetches. With fake timers and debounced bindings, advance the relevant timers before waiting for the queue to settle.

## Mocks & spies

Register mock services through the 3rd `createFixture` argument with `Registration.instance`
(or `.singleton`). The fourth argument is the `autoStart` boolean. Use your test runner's spies (`vi.fn()`):

```typescript
import { Registration } from 'aurelia';
import { IApiService } from '../src/services/api';

const api = { getUser: vi.fn().mockResolvedValue({ name: 'Test' }) };

const { assertText, started } = createFixture(
  '<user-card></user-card>',
  {},
  [UserCard, Registration.instance(IApiService, api)],
);
await started;
assertText('Test', { compact: true });
expect(api.getUser).toHaveBeenCalled();
```

`@aurelia/testing` also ships `createSpy(obj?, key?, callThrough?)` returning a spy with `.calls`,
`.reset()`, and `.restore()` if you want a dependency-free spy.

To call methods on the component under test, get its view-model with `CustomElement.for(el).viewModel`
(see [components.md](components.md)), or use the `component` returned by the fixture when the component is the root.

## Testing value converters, behaviors & attributes

- **Value converter / binding behavior:** unit-test the class directly (`new ToUpper().toView('x')`),
  and integration-test by registering it as a dep and asserting rendered output
  (`createFixture('<div>${v | toUpper}</div>', { v: 'hi' }, [ToUpper])`).
- **Custom attribute:** register it as a dep, apply it in the template, and assert the element's
  resulting DOM/state; trigger bindable changes via `component.x = ...` + `tasksSettled()`.

## Testing routing

Use `historyStrategy: 'none'` so tests don't mutate browser history, then drive navigation through
`IRouter`:

```typescript
import { route, IRouter, RouterConfiguration } from '@aurelia/router';

@route({ routes: [
  { path: ['', 'home'], component: () => import('./home') },
  { path: 'users/:id', component: () => import('./user') },
]})
class App {}

const { appHost, container, started, stop } = createFixture(
  '<au-viewport></au-viewport>',
  App,
  [RouterConfiguration.customize({ historyStrategy: 'none' })],
);
await started;

const router = container.get(IRouter);
await router.load('users/42');
expect(appHost.textContent).toContain('User 42');
await stop(true);
```

A `canLoad` returning a redirect path can be asserted the same way (load the guarded route, assert
the redirected component rendered). Router events are observable via `container.get(IRouterEvents)`.

## Pitfalls

- Forgetting `await started` → asserting before render/async hooks finish.
- Not calling `stop(true)` → leaked fixtures/DOM across tests. (The setup above tracks and stops fixtures; explicit `stop(true)` is also safe because cleanup checks `fixture.torn`.)
- Asserting without `await tasksSettled()` after a state change → stale DOM.
- Querying `testHost` (the wrapper) instead of `appHost` (the component host).
- Platform not set → bootstrap `setPlatform(...)` in `test/setup.ts` (see Setup above).

## Storybook

For current framework configuration and stories, read [storybook.md](storybook.md).

## Sources

- [Official testing source and fixture API](https://github.com/aurelia/aurelia/blob/v2.0.0-rc.2/packages/testing/src/startup.ts)
- [Testing guide](https://docs.aurelia.io/developer-guides/overview/testing)
