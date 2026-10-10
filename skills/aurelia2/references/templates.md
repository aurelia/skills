# Templates and Binding

### Event Binding  -  Always `.trigger`
```html
<button click.trigger="handleClick()">Click</button>
<input input.trigger="onInput($event)">
<form submit.trigger:prevent="onSubmit()">
  <button type="submit">Save</button>
</form>
```

### Property Binding & Binding Modes
```html
<!-- .bind  -  auto-detects mode (two-way on form elements, to-view otherwise) -->
<input value.bind="name">
<div class.bind="isActive ? 'active' : ''"></div>

<!-- Explicit binding modes -->
<input value.two-way="name">
<span textcontent.to-view="message"></span>
<span>${count}</span>
<input value.one-time="initialValue">
<custom-el value.from-view="outputValue"></custom-el>
```

### Conditional Rendering
```html
<!-- if.bind removes/adds DOM elements -->
<div if.bind="showContent">Conditional content</div>
<div else>Fallback content</div>

<!-- show.bind toggles visibility (keeps element in DOM) -->
<div show.bind="isVisible">Shown or hidden via CSS</div>

<!-- switch (template controller) -->
<template switch.bind="status">
  <span case="active">Active</span>
  <span case="inactive">Inactive</span>
  <span default-case>Unknown</span>
</template>
```

### List Rendering
```html
<div repeat.for="item of items">${item.name}</div>

<!-- With index -->
<div repeat.for="item of items">
  ${$index}: ${item.name}
</div>

<!-- Keyed rendering for performance -->
<div repeat.for="item of items; key: id">${item.name}</div>
```

### Lambda Expressions in Templates
```html
<!-- Filter and sort directly in templates -->
<ul>
  <li repeat.for="user of users.filter(u => u.isActive)">
    ${user.name}
  </li>
</ul>

<!-- Sort a copy so evaluating the binding does not mutate its source -->
<li repeat.for="item of items.slice().sort((a, b) => a.name.localeCompare(b.name))">
  ${item.name}
</li>
```

### Template References (`ref`)
```html
<input type="text" ref="nameInput" placeholder="Enter name">
<canvas ref="myCanvas"></canvas>
```

```typescript
export class MyComponent {
  nameInput!: HTMLInputElement;  // Type it explicitly
  myCanvas!: HTMLCanvasElement;

  // Refs are available from bound() onward (NOT in constructor or binding)
  bound() {
    console.log(this.nameInput); // HTMLInputElement
  }

  attached() {
    // Best place for DOM operations
    this.nameInput.focus();
  }
}
```

For custom element references:
```html
<!-- Get the view-model instance -->
<my-widget component.ref="widgetVm"></my-widget>

<!-- Get the Aurelia controller (advanced) -->
<my-widget controller.ref="widgetController"></my-widget>
```

### Template Variables (`<let>`)
```html
<!-- Declare variables directly in templates -->
<let full-name="${firstName} ${lastName}"></let>
<p>${fullName}</p>

<!-- Local template variable -->
<let total.bind="price * quantity"></let>
<p>Total: ${total}</p>
```

Use `to-binding-context` on `<let>` only when the value should be written to the view-model rather than the local template scope.

Note: Variable names use kebab-case in the `<let>` element but camelCase when referenced (`full-name` becomes `fullName`).

### CSS Class Binding
```html
<!-- Conditional class (individual) -->
<div active.class="isActive">Toggle active class</div>
<div loading.class="isLoading">Toggle loading class</div>

<!-- Expression-based -->
<div class="${isActive ? 'active' : 'inactive'}">Interpolated</div>
<div class.bind="computedClasses">Bound</div>
```

### Style Binding
```html
<div style="color: ${textColor}">Interpolated</div>
<div style.bind="styleObject">Bound</div>
```

### Content Projection with `<au-slot>`

Use `<au-slot>` for content projection (NOT native `<slot>` unless using Shadow DOM):

**card.html:**
```html
<div class="card">
  <div class="card-header">
    <au-slot name="header">
      <h3>Default Header</h3>
    </au-slot>
  </div>
  <div class="card-body">
    <au-slot>
      Default body content
    </au-slot>
  </div>
</div>
```

Usage:
```html
<card>
  <span au-slot="header">Custom Header</span>
  <p>Custom body content goes in the default slot</p>
</card>
```

### Attribute Binding (`& attr`)

Use `& attr` when you need to bind to the HTML attribute rather than the DOM property (useful for ARIA attributes, custom attributes, non-standard attributes):

```html
<div aria-busy.bind="isLoading & attr"></div>
<div data-id.bind="itemId & attr"></div>
```

## Value Converters

Value converters transform data in template bindings. They use the pipe `|` syntax.

```typescript
import { valueConverter } from 'aurelia';

@valueConverter('currency')
export class CurrencyValueConverter {
  toView(value: number, currencyCode = 'USD', locale = 'en-US'): string {
    return new Intl.NumberFormat(locale, {
      style: 'currency',
      currency: currencyCode,
    }).format(value);
  }
}
```

Usage in templates:
```html
<!-- Import locally -->
<import from="./converters/currency"></import>
<span>${price | currency}</span>
<span>${price | currency:'EUR':'de-DE'}</span>

<!-- Chaining converters -->
<span>${amount | currency | uppercase}</span>
<!-- uppercase is an app-defined converter; import/register it too. -->
```

Register globally only when the converter is shared across the app. Keep currency formatting to-view; localized currency input needs a parser that handles the chosen locale.

## Binding Behaviors

Binding behaviors modify how bindings work at runtime. Use the `&` syntax.

```html
<!-- Debounce input (default 200ms) -->
<input value.bind="search & debounce">
<input value.bind="search & debounce:500">

<!-- Throttle updates -->
<input value.bind="data & throttle:300">

<!-- Signal-based refresh -->
<span>${price | currency & signal:'refresh-prices'}</span>

<!-- Force binding mode -->
<input value.bind="name & oneTime">
<input value.bind="name & twoWay">
<input value.bind="name & toView">
<input value.bind="name & fromView">

<!-- Bind to attribute instead of property -->
<div data-value.bind="val & attr"></div>
```

## Dynamic composition

Use `<au-compose component.bind="currentComponent" model.bind="currentModel">` for dynamic components. In RC.1+, `flush-mode="async"` batches simultaneous component/model changes into one activation; the default is `sync`.

For RC.2, use nested `if`/`else` or `switch.bind` for multiple branches. Do not generate unreleased `else if` chains from examples on the framework's master branch.

## Sources

- [Template cheat sheet](https://docs.aurelia.io/templates/cheat_sheet)
- [List rendering](https://docs.aurelia.io/templates/repeats-and-list-rendering)
- [RC.1 and RC.2 changes](https://aurelia.io/blog/2026/10/5/aurelia-2-rc1-rc2-what-you-missed/)
