# Scaffolding and Tooling

Prefer the [official generator](https://github.com/aurelia/new). Read [cli.md](cli.md) for feature selection. Start with the features the user needs; a minimal app does not need Tailwind, Storybook, or a router.

```bash
npx makes aurelia my-app -s app,vite,typescript,no-unit-tests,app-blank
cd my-app
npm install
npm run build
```

Respect the project's package manager and lockfile when modifying an existing app.

## Compatibility baseline

Verified on 2026-10-10. Check package engines and peer dependencies again when selecting new versions.

| Package | Verified compatibility |
| --- | --- |
| `aurelia`, core `@aurelia/*` packages | `2.0.0-rc.2`; align direct core dependencies |
| `@aurelia/vite-plugin` RC.2 | Vite `^7.0.2` or `^8.0.0` |
| Convention tooling | TypeScript 5 and 6 |
| `@aurelia/storybook` 3.0.0 | Aurelia RC.2; Storybook and Vite builder `^10.5.6` |

Use a Node version supported by every selected tool, not just the generator. Vite 7/8 and the current Storybook integration require Node `^20.19.0` or `>=22.12.0`.

Avoid a copied kitchen-sink `package.json` with drifting `latest` tags. Resolve compatible versions when scaffolding and keep the resulting lockfile. The required runtime dependency is `aurelia`; add `@aurelia/router` separately for routed apps. Vite projects need `@aurelia/vite-plugin`, Vite, TypeScript, and `tslib` when `importHelpers` is enabled. Tests need their own runner and `@aurelia/testing` only when selected.

## Vite

```typescript
import { defineConfig } from 'vite';
import aurelia from '@aurelia/vite-plugin';

export default defineConfig({
  plugins: [aurelia()],
  build: { target: 'es2022' },
});
```

Omitting `useDev` lets the plugin select development bundles outside production mode. `useDev: true` forces them even for production builds. Inspect custom build modes deliberately.

On Vite 8, Aurelia's plugin handles standard decorators before Oxc runs. Leave `experimentalDecorators` and `emitDecoratorMetadata` disabled. Do not disable or override Oxc's decorator/TypeScript transform; use the plugin's `standardDecoratorInclude` for decorated source outside its normal selection. Existing Vite 7 projects do not need a bundler upgrade just to use this skill.

## TypeScript

Keep the generator's declarations for HTML/CSS resources. For a new modern Vite app, this is a useful baseline:

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true,
    "skipLibCheck": true,
    "esModuleInterop": true,
    "resolveJsonModule": true,
    "importHelpers": true,
    "sourceMap": true,
    "noEmit": true
  },
  "include": ["src"],
  "files": ["src/resource.d.ts"]
}
```

The generator's older TypeScript 5 baseline uses `moduleResolution: "node"`. TypeScript 6 deprecates that mode; use `bundler` for a Vite app when updating. Do not replace an existing configuration without checking its build and test requirements.

## Bootstrap

```typescript
import Aurelia from 'aurelia';
import { MyApp } from './my-app';

Aurelia.app(MyApp).start();
```

The HTML entry needs the matching host (`<my-app></my-app>`) and a module script pointing at `/src/main.ts`.

For a routed app, install `@aurelia/router` and register `RouterConfiguration` before `.app(MyApp)`. Configure only options the app needs; `useHref` defaults to true. Read [routing.md](routing.md) for navigation and active-link styling.

Register shared components, converters, or custom attributes with `Aurelia.register(...)` before startup. Prefer local imports for resources used by only a few components. Register `SVGAnalyzer` from `@aurelia/runtime-html` when using SVG attribute bindings.

## Optional Tailwind

When Tailwind v4 is selected, add `@tailwindcss/vite` to the Vite plugins and put `@import "tailwindcss";` in the CSS entry. Import that entry from the application. Preserve another existing CSS setup unless changing it is part of the task.

## Sources

- [Official generator](https://github.com/aurelia/new)
- [Vite plugin source](https://github.com/aurelia/aurelia/tree/v2.0.0-rc.2/packages-tooling/vite-plugin)
- [RC.1 and RC.2 tooling changes](https://aurelia.io/blog/2026/10/5/aurelia-2-rc1-rc2-what-you-missed/)
- [Application startup](https://docs.aurelia.io/getting-to-know-aurelia/startup-and-enhancement/app-configuration-and-startup)
