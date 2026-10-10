# Routing

Use the `@route` decorator on the root component with **dynamic `import()`** for lazy loading:

```typescript
import { route } from '@aurelia/router';

@route({
  routes: [
    {
      path: ['', 'home'],
      component: import('./routes/home/home'),
      title: 'Home',
    },
    {
      path: 'about',
      component: import('./routes/about/about'),
      title: 'About',
    },
    {
      id: 'product',
      path: 'product/:id',
      component: import('./routes/product/product'),
      title: 'Product',
    },
    {
      path: 'files/*path',
      component: import('./routes/files/files'),
      title: 'Files',
    },
    { path: 'not-found', component: import('./routes/not-found/not-found'), title: 'Not Found' },
    { path: '*path', component: import('./routes/not-found/not-found'), title: 'Not Found' },
  ],
})
export class MyApp {}
```

### Route Parameter Types

- **Required:** `path: 'product/:id'`  -  must be provided
- **Optional:** `path: 'product/:id?'`  -  can be omitted
- **Wildcard:** `path: 'files/*path'`  -  captures everything after
- **Constrained:** `path: 'product/:id{{^\\d+$}}'`  -  must match regex
- **Multiple paths:** `path: ['', 'home']`  -  matches either

### Route Configuration Options

- `redirectTo`  -  redirect to another route path
- `fallback`  -  component/path for unmatched routes (choose fallback handling to match the app's route structure)
- `data`  -  arbitrary metadata (e.g. `{ requiresAuth: true }`)
- `caseSensitive`  -  whether path matching is case-sensitive
- `id`  -  unique route identifier for programmatic use

### Navigation in Templates

Use `load` for structured instructions and route IDs. Plain `href` is intercepted only when `useHref` is true (the default). Setting `useHref: false` disables that interception.

No active CSS class is added by default. Configure `activeClass` to style active `load` links, or bind their `active` flag. Plain `href` links do not receive this class.

For top-level app navigation when scoped/nested routing may be active, force root-context resolution with `context.bind: null`.

```html
<!-- load attribute (recommended, more features) -->
<a load="route: home; context.bind: null">Home</a>
<a load="route: product/42; context.bind: null">View Product</a>
<a load="route: product/${productId}; context.bind: null">Dynamic Product</a>
<a load="../details">Relative route (intentional scoped navigation)</a>

<!-- Plain href also works for simple navigation -->
<a href="home">Home</a>
<a href="about">About</a>

<!-- External links are auto-detected by the router. For edge cases, use the external attr -->
<a href="https://example.com">External (auto-detected)</a>
<a href="/api/download" external>API endpoint (forced external)</a>

<!-- Configure activeClass, or bind the active flag explicitly -->
<a load="route: about; active.bind: isAboutActive" active.class="isAboutActive">About</a>
<au-viewport></au-viewport>
```

### Programmatic Navigation

```typescript
import { resolve } from 'aurelia';
import { IRouter } from '@aurelia/router';

export class MyComponent {
  private router = resolve(IRouter);

  async goToProduct(id: number) {
    await this.router.load(`/product/${id}`);
  }

  async goWithOptions() {
    await this.router.load(
      { component: 'product', params: { id: '42' } },
      { queryParams: { tab: 'reviews' }, title: 'Product 42' },
    );
  }
}
```

### Route Lifecycle Hooks

Routed components can implement `IRouteViewModel` for route-specific lifecycle hooks. These are separate from component lifecycles:

```typescript
import { IRouteViewModel, Params, RouteNode, INavigationOptions } from '@aurelia/router';

export class ProductDetail implements IRouteViewModel {
  product: any;

  // Guard: can we load this route? Return false or a redirect path to prevent.
  async canLoad(params: Params, next: RouteNode, current: RouteNode | null) {
    this.product = await this.api.getProduct(params.id);
    if (!this.product) {
      return '/not-found'; // redirect
    }
    return true;
  }

  // Load data after canLoad passes. A returned Promise is awaited before rendering.
  async loading(params: Params, next: RouteNode, current: RouteNode | null) {
    this.relatedProducts = await this.api.getRelated(params.id);
  }

  // Runs after the component is fully loaded and activated. Good for analytics,
  // scroll restoration, or post-load side effects.
  loaded(params: Params, next: RouteNode, current: RouteNode | null) {
    analytics.track('page_view', { page: 'product', id: params.id });
    window.scrollTo(0, 0);
  }

  // Guard: can the user leave? Good for unsaved changes warnings.
  canUnload(next: RouteNode | null, current: RouteNode): boolean | Promise<boolean> {
    if (this.hasUnsavedChanges) {
      return confirm('You have unsaved changes. Leave?');
    }
    return true;
  }

  // Cleanup when navigating away.
  unloading(next: RouteNode | null, current: RouteNode): void {
    this.cleanup();
  }
}
```

**Full hook signatures:** every route hook receives a trailing `options: INavigationOptions` argument after the parameters shown above (`canLoad(params, next, current, options)`, `loading(params, next, current, options)`, `loaded(params, next, current, options)`, `canUnload(next, current, options)`, `unloading(next, current, options)`). Declare only the parameters you actually use — TypeScript allows implementing a hook with fewer parameters.

**Route lifecycle order:** `canLoad` -> `loading` -> `loaded` -> (user navigates away) -> `canUnload` -> `unloading`

**When to use each hook:**
- `canLoad` -- the page is useless without the data (blocks rendering). Can redirect or deny.
- `loading` -- initialize after navigation is approved. A returned Promise delays activation. To render a loading state immediately, start secondary work without returning its Promise, handle rejection, and prevent stale results after navigation.
- `loaded` -- component is fully active. Use for analytics, scroll position, post-load effects.
- `canUnload` -- prompt the user before leaving (unsaved changes, confirmations).
- `unloading` -- teardown and cleanup before navigating away.

### Accessing Current Route Info

```typescript
import { resolve } from '@aurelia/kernel';
import { ICurrentRoute } from '@aurelia/router';

export class MyComponent {
  private currentRoute = resolve(ICurrentRoute);

  logRoute() {
    console.log(this.currentRoute.path);
    console.log(this.currentRoute.parameterInformation);
  }
}
```

### Reading Query Parameters

Inside `canLoad` or `loading`, access query params from the `next` RouteNode:
```typescript
canLoad(params: Params, next: RouteNode) {
  const foo = next.queryParams.get('foo'); // /product/42?foo=bar
  return true;
}
```

## RC.1 and RC.2 routing

- `IContextRouter` wraps the router with the current component's route context. Prefer it for relative navigation inside routed components. Root-component injection needs `resolve(lazy(IContextRouter))`; see the official release guide.
- `/path` targets the app root; `path` and `./path` are relative; `../path` goes to a parent context. Check nested deep links and the deployment base path.
- Set `next.title` from loaded route data rather than writing `document.title` outside the router.
- `useEagerLoading: true` builds the routing table up front and can resolve ambiguous nested deep links. It is optional and changes startup costs; consult its empty-child-path restrictions before enabling it.
- Lazy route imports are a useful default for larger pages. Eager component imports remain valid when the app benefits from them.

Keep `@aurelia/router` and `@aurelia/router-direct` examples separate: their types and configuration are not interchangeable. Preserve an existing app's router choice unless migration is requested.

## Sources

- [Navigation](https://docs.aurelia.io/getting-to-know-aurelia/routing/aurelia-router/navigation/navigating)
- [Router options and navigation types](https://github.com/aurelia/aurelia/blob/v2.0.0-rc.2/packages/router/src/options.ts)
- [RC.1 and RC.2 changes](https://aurelia.io/blog/2026/10/5/aurelia-2-rc1-rc2-what-you-missed/)
