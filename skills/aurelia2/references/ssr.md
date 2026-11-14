# Server-Side Rendering (SSR) and Hydration

Server-Side Rendering (SSR) in Aurelia 2 pre-renders custom elements and templates on the server into full HTML before delivering them to the browser. This provides instantaneous First Contentful Paint (FCP), robust SEO for search indexers, and progressive client hydration.

## Architectural Model

Unlike virtual-DOM frameworks that serialize virtual node trees, Aurelia 2 operates directly against web standards and the DOM platform (`PLATFORM` in `@aurelia/platform-browser`).

```
                    ┌────────────────────────────┐
                    │ Incoming HTTP Request      │
                    │ (Hono / Node.js runtime)   │
                    └─────────────┬──────────────┘
                                  │
                                  ▼
                    ┌────────────────────────────┐
                    │ Request-Scoped DOM Scope   │
                    │ (Isolated Window & JSDOM)  │
                    └─────────────┬──────────────┘
                                  │
            ┌─────────────────────┴─────────────────────┐
            ▼                                           ▼
┌─────────────────────────┐               ┌──────────────────────────┐
│ Server Loader Execution │               │ Aurelia Component Render │
│ (DB / Cache / Auth)     │               │ (HTML & <au-slot> tags)  │
└───────────┬─────────────┘               └─────────────┬────────────┘
            │                                           │
            └─────────────────────┬─────────────────────┘
                                  ▼
                    ┌────────────────────────────┐
                    │ HTML Document Assembly     │
                    │ + Serialized State Payload │
                    └─────────────┬──────────────┘
                                  │
                                  ▼
                    ┌────────────────────────────┐
                    │ Client Hydration           │
                    │ (Aurelia.enhance / hydrate)│
                    └────────────────────────────┘
```

SSR in Aurelia 2 consists of three primary concerns:
1. **Request-Scoped Isolation**: Running renders inside per-request virtual DOM contexts to avoid concurrent request state leaks.
2. **State Serialization**: Embedding initial state into safe `<script id="__HYDRATION__" type="application/json">` blocks so client-side apps hydrate without redundant network calls.
3. **Client Hydration**: Binding the live Aurelia runtime to pre-rendered server DOM nodes without flickering or full rebuilds.

---

## 1. Request-Scoped Server DOM Isolation

Aurelia 2 uses platform globals (`window`, `document`, `HTMLElement`). When running in Node.js or edge runtimes, every request must execute in an isolated DOM scope to prevent cross-request contamination.

```typescript
import { JSDOM } from 'jsdom';
import Aurelia, { CustomElement } from 'aurelia';

export interface RenderResult {
  html: string;
  initialData?: unknown;
}

export async function renderToString(
  component: unknown,
  initialData?: unknown
): Promise<string> {
  const dom = new JSDOM('<!doctype html><html><head></head><body><div id="app"></div></body></html>');
  const { window } = dom;

  // Initialize or synchronize Aurelia's browser platform for this request
  const host = window.document.querySelector<HTMLElement>('#app')!;

  const au = new Aurelia();
  au.app({
    host,
    component: typeof component === 'function' ? component : CustomElement.define({ name: 'ssr-app', template: '' }, component as any),
  });

  await au.start();
  const renderedContent = host.innerHTML;
  await au.stop();

  return renderedContent;
}
```

---

## 2. Server Data Loaders & State Transfer

Avoid client-side loading spinners and duplicate API fetches by executing data loaders during SSR and serializing the initial payload into the response HTML:

```typescript
// pages/post-page.ts
export class PostPage {
  static async loader(params: { id: string }, db: DatabaseService) {
    const post = await db.findPost(params.id);
    return { post };
  }

  post?: { title: string; content: string };

  activate(data?: { post: { title: string; content: string } }) {
    if (data?.post) {
      this.post = data.post;
    }
  }
}
```

### Safe HTML Serialization

Always escape script tags and HTML entities to prevent Cross-Site Scripting (XSS) in hydration payloads:

```typescript
export function serializeState(data: unknown): string {
  const json = JSON.stringify(data) ?? '{}';
  // Escape '<' to prevent premature closing of the script tag or inline injection
  const safeJson = json.replace(/</g, '\\u003c');
  return `<script id="__HYDRATION__" type="application/json">${safeJson}</script>`;
}
```

---

## 3. Client Hydration

On the browser, read the server-injected state and bind Aurelia to the existing DOM host without duplicating API calls:

```typescript
// main.ts (client)
import Aurelia from 'aurelia';
import { App } from './app';

function getInitialState<T>(): T | undefined {
  const el = document.getElementById('__HYDRATION__');
  if (!el?.textContent) return undefined;
  try {
    return JSON.parse(el.textContent) as T;
  } catch {
    return undefined;
  }
}

async function bootstrap() {
  const initialState = getInitialState<{ post?: any }>();
  const host = document.querySelector<HTMLElement>('#app')!;

  const au = new Aurelia();
  const rootComponent = new App();

  if (initialState) {
    Object.assign(rootComponent, initialState);
  }

  au.app({ host, component: rootComponent });
  await au.start();
}

bootstrap().catch(console.error);
```

---

## 4. Fullstack Integration with Hono

Hono pairs cleanly with Aurelia SSR using middleware or custom renderers:

```typescript
import { Hono } from 'hono';
import { HomePage } from './pages/home';
import { renderToString, serializeState } from './ssr-engine';

const app = new Hono();

app.get('/', async (c) => {
  const data = await HomePage.loader();
  const bodyHtml = await renderToString(HomePage, data);
  const stateScript = serializeState(data);

  return c.html(`
    <!doctype html>
    <html>
      <head>
        <meta charset="utf-8" />
        <title>Aurelia 2 SSR on Hono</title>
      </head>
      <body>
        <div id="app">${bodyHtml}</div>
        ${stateScript}
        <script type="module" src="/src/main.ts"></script>
      </body>
    </html>
  `);
});

export default app;
```

---

## Comparison: Aurelia 2 SSR vs React Server Components (RSC)

| Architectural Dimension | Aurelia 2 SSR | React Server Components (RSC) |
| --- | --- | --- |
| **DOM Model** | Direct DOM / Light DOM (`<au-slot>`) | Virtual DOM fiber tree with custom binary wire format |
| **Data Binding** | Two-way and reactive observation | One-way immutable props and unidirectional flows |
| **Server Separation** | Standard classes with optional static `loader` | Strict `'use client'` and `'use server'` directive barriers |
| **Hydration Cost** | Surgical binding to pre-existing DOM | Reconciles virtual DOM tree against server-generated HTML |
| **Bundle Footprint** | Lean footprint, standard web components | Larger runtime for streaming fiber reconciliation |

---

## Sources

- [Aurelia 2 Enhancement and Startup](https://docs.aurelia.io/getting-to-know-aurelia/startup-and-enhancement/enhance)
- [Aurelia Component Templates](templates.md)
- [Aurelia Architecture and Reactivity](reactivity.md)
- [Hono Web Framework](https://hono.dev/)
