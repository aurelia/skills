# Existing HTML and Server Rendering

Use official Aurelia documentation and the installed package's public APIs when working with existing HTML, server rendering, or hydration. Inspect the app's existing rendering integration before proposing changes. Do not assume that an API documented on `master` exists in the released package.

## Progressive enhancement

`Aurelia.enhance` attaches Aurelia behavior to existing DOM. This fits a server-rendered page, CMS widget, or a section of another application:

```typescript
import Aurelia from 'aurelia';

const host = document.querySelector<HTMLElement>('#counter');
if (!host) throw new Error('Counter host is missing');

const root = await Aurelia.enhance({
  host,
  component: { count: 0 },
});

// When the embedding application removes the widget:
await root.deactivate();
```

The host's existing markup can contain `${count}` and `click.trigger="count = count + 1"`. Keep the markup trusted: enhancement compiles Aurelia expressions; it is not an HTML sanitizer.

## SSR and hydration boundaries

Enhancement, fresh client rendering, and reuse of a server-rendered Aurelia view have different requirements. Existing HTML alone does not prove that a client can hydrate it. Check the exact public APIs, template definitions, state transfer, and markers required by the installed version. Avoid internal renderer APIs or fabricated manifest formats.

Keep browser-only work in the browser and preserve request isolation for server state. Verify meaningful initial HTML, one app host after startup, working events/navigation, and no avoidable data reset during client startup. If the installed release has no documented path for a requested integration, explain that gap before choosing an approach.

## Sources

- [Enhance](https://docs.aurelia.io/getting-to-know-aurelia/startup-and-enhancement/enhance)
- [Application startup](https://docs.aurelia.io/getting-to-know-aurelia/startup-and-enhancement/app-configuration-and-startup)
- [Public runtime exports for RC.2](https://github.com/aurelia/aurelia/blob/v2.0.0-rc.2/packages/runtime-html/src/index.ts)
