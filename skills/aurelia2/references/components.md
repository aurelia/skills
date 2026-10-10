# Components and Lifecycle

### Convention-Based Components
Aurelia 2 uses convention: `my-component.ts` + `my-component.html` are automatically paired.

**my-component.ts**:
```typescript
import { bindable } from 'aurelia';

export class MyComponent {
  @bindable label = '';
  @bindable count = 0;
}
```

**my-component.html**:
```html
<div>
  <span>${label}: ${count}</span>
</div>
```

### Using Components in Templates

Components must be made available before use. Three ways to do this:

**1. `<import>` tag (local, per-template):**
```html
<import from="./components/my-component"></import>
<my-component label="Hello" count.bind="5"></my-component>
```

**2. `dependencies` array on `@customElement` (local, per-component):**
```typescript
import { customElement } from 'aurelia';
import { MyComponent } from './components/my-component';

@customElement({
  name: 'parent-widget',
  dependencies: [MyComponent],
})
export class ParentWidget {}
```

**3. Global registration in `main.ts`** (see [scaffolding.md](scaffolding.md)).

### HTML-Only Components

Create simple components with just an HTML file (no TypeScript needed):

**status-badge.html**:
```html
<bindable name="status"></bindable>
<bindable name="message"></bindable>
<span class="badge badge-${status}">${message}</span>
```

Usage:
```html
<import from="./status-badge.html"></import>
<status-badge status="success" message="Complete"></status-badge>
```

### Explicit Component Definition with `@customElement`

```typescript
import { customElement } from 'aurelia';

@customElement({
  name: 'user-card',
  template: `
    <div class="user-card">
      <h3>\${name}</h3>
      <p>\${email}</p>
    </div>
  `,
})
export class UserCard {
  name = 'John Doe';
  email = 'john@example.com';
}
```

### Dependency Injection
Prefer `resolve()` in class fields or the constructor. Existing `static inject` is also valid; do not call `resolve()` later in event handlers or lifecycle hooks:
```typescript
import { resolve } from 'aurelia';
import { MyService } from '../services/my-service';

export class MyComponent {
  private myService: MyService = resolve(MyService);
}
```

### Component Lifecycle Hooks

Lifecycle sequence (hooks are optional): `constructor` -> `hydrating` -> `hydrated` -> `created` -> `binding` -> `bound` -> `attaching` -> `attached` -> `detaching` -> `unbinding` -> `dispose`

The `define` hook is no longer called and was removed from the public API in RC.2.

All hooks are optional. Implement only what you need. Hooks like `binding`/`unbinding` and `attaching`/`detaching` are typically used in pairs for setup/cleanup.

```typescript
export class MyComponent {
  // constructor  -  inject services, basic setup
  constructor() {}

  // created  -  component fully constructed, children resolved. Runs once.
  created() {}

  // binding  -  bindable properties assigned, but view bindings not yet connected.
  //           Runs parent -> child. Return a Promise to block children.
  binding() {}

  // bound  -  view bindings active; ref, let, and from-view values available.
  //         Runs parent -> child.
  bound() {}

  // attaching  -  DOM insertion starting. Runs parent -> child.
  attaching() {}

  // attached  -  component and all children are in the DOM. Safe for DOM APIs.
  //            Runs child -> parent.
  attached() {}

  // detaching  -  before removal from DOM. Clean up DOM listeners, 3rd-party libs.
  //             Runs child -> parent.
  detaching() {}

  // unbinding  -  bindings disconnected. Clean up subscriptions.
  //             Runs child -> parent.
  unbinding() {}

  // dispose  -  permanent teardown. A cached/reused view may only unbind.
  //           Prevent memory leaks here.
  dispose() {}
}
```

**Key guidance:**
- Use `attached()` for DOM-dependent work (3rd-party library init, measuring elements).
- Use `detaching()` to tear down what you set up in `attached()`.
- Use `binding()` for async data loading that should block rendering (return a Promise).
- Use `bound()` when you need `ref` values or from-view bindings.
- Use `unbinding()` to dispose subscriptions set up in `binding()` or `bound()`.

### Bindable Properties

```typescript
import { bindable, BindingMode } from 'aurelia';

export class UserCard {
  @bindable user: any;
  @bindable isActive = false;

  // Explicit two-way binding mode
  @bindable({ mode: BindingMode.twoWay }) selectedId = '';

  // Change callback  -  convention: propertyName + "Changed"
  userChanged(newUser: any, oldUser: any) {
    console.log('User changed:', newUser);
  }

  isActiveChanged(newValue: boolean, oldValue: boolean) {
    console.log('Active changed:', newValue);
  }
}
```

Usage in templates:
```html
<user-card
  user.bind="currentUser"
  is-active.bind="userIsActive"
  selected-id.two-way="selectedUserId">
</user-card>
```

Note: bindable property names use camelCase in TypeScript but kebab-case in HTML attributes.

## Custom Attributes

Create reusable behavior that can be applied to any element:

```typescript
import { customAttribute, INode, bindable } from 'aurelia';
import { resolve } from '@aurelia/kernel';

@customAttribute({ name: 'tooltip', defaultProperty: 'text' })
export class TooltipCustomAttribute {
  @bindable text = '';

  private element: HTMLElement = resolve(INode) as HTMLElement;

  attached() {
    this.element.title = this.text;
  }

  textChanged(newValue: string) {
    this.element.title = newValue;
  }
}
```

Usage:
```html
<import from="./attributes/tooltip"></import>
<button tooltip="Click to save">Save</button>
<button tooltip.bind="dynamicTooltip">Dynamic</button>
```

`defaultProperty` selects the bindable used by single-value attribute syntax. The old `primary` and custom-attribute `defaultBindingMode` options are removed; set `mode` on individual bindables.

## Sources

- [Component lifecycles](https://docs.aurelia.io/components/component-lifecycles)
- [Custom attributes](https://docs.aurelia.io/templates/custom-attributes)
- [RC.2 release notes](https://github.com/aurelia/aurelia/releases/tag/v2.0.0-rc.2)
