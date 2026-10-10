# Storybook

Use this only when the app needs Storybook. Verified baseline: `@aurelia/storybook` 3.0.0, Aurelia RC.2, Storybook `^10.5.6`, and matching builder packages. Check peers before upgrading an existing installation.

## Vite configuration

Install `@aurelia/storybook`, `storybook`, `@storybook/builder-vite`, and `@aurelia/vite-plugin` as development dependencies, selecting compatible versions.

**.storybook/main.ts**:

```typescript
import { defineMain } from '@aurelia/storybook/node';

export default defineMain({
  stories: ['../src/**/*.stories.@(ts|js)'],
  framework: { name: '@aurelia/storybook', options: {} },
  core: { builder: '@storybook/builder-vite' },
});
```

The preset configures Aurelia and avoids duplicate runtime instances. Do not add a second Aurelia plugin or copy old dependency-exclusion workarounds without an observed need.

**.storybook/preview.ts** holds project settings. It does not re-export `render` or `renderToCanvas`; the framework loads its renderer:

```typescript
import { definePreview } from '@aurelia/storybook';

export default definePreview({
  parameters: { controls: { expanded: true } },
});
```

## Component story

```typescript
import type { Meta, StoryObj } from '@aurelia/storybook';
import { UserCard } from './user-card';

const meta = {
  component: UserCard,
  args: { name: 'Alice' },
} satisfies Meta<typeof UserCard>;

export default meta;
type Story = StoryObj<typeof meta>;
export const Default = {} satisfies Story;
```

Use args matching the component's bindables. Add interaction tests where behavior matters and run `storybook build` before reporting the configuration complete. Preserve CSF 3 or typed factory conventions already used by the app.

For Webpack, Rsbuild/Rspack, resource registration, projected content, portable stories, and test addons, read the [official integration guide](https://github.com/aurelia/storybook).
