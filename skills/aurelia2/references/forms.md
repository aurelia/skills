# Forms

Read this for input binding in Aurelia 2 — text, checkboxes, radios, selects, files, and form
submission. The recurring Aurelia-specific points are `model.bind` (for non-string values),
`matcher.bind` (for object equality), and that **form submit is not prevented by default**.

## Text-like inputs

`value.bind` is two-way by default on inputs and textareas.

```html
<input type="text" value.bind="userName">
<textarea value.bind="comment"></textarea>

<!-- Control when the model updates -->
<input value.bind="search & debounce:300">                 <!-- after typing pauses -->
<input value.bind="query & updateTrigger:'blur'">          <!-- only on blur -->
```

**Numbers:** `value.bind` on an `<input type="number">` still produces a **string**. Bind the
DOM's `valueAsNumber` instead (Aurelia observes it two-way on inputs), or coerce yourself:

```html
<input type="number" value.bind="age">             <!-- age is a string: '42' -->
<input type="number" value-as-number.bind="age">   <!-- age is a number (NaN when empty) -->
```

```typescript
// alternative: coerce where you read it, or expose a getter/setter pair
set ageInput(v: string) { this.age = v === '' ? null : Number(v); }
get ageInput() { return this.age == null ? '' : String(this.age); }
```

## Checkboxes

Single boolean:

```html
<input type="checkbox" checked.bind="agreeToTerms">
```

Bound to an **array** — use `model.bind` for the per-item value and `checked.bind` for the array.
Checking adds the value, unchecking removes it:

```html
<label repeat.for="p of products">
  <input type="checkbox" model.bind="p.id" checked.bind="selectedIds"> ${p.name}
</label>
```

Array of **objects** needs `matcher.bind` unless the bound items are the exact same references:

```html
<input type="checkbox" model.bind="p" matcher.bind="byId" checked.bind="selectedProducts">
```

```typescript
byId = (a: Product, b: Product) => a?.id === b?.id;
```

## Radio buttons

Group by `name`; use `model.bind` for the value and `checked.bind` for the selection. Use
`matcher.bind` for object values.

```html
<label repeat.for="p of products">
  <input type="radio" name="product" model.bind="p" matcher.bind="byId" checked.bind="selected">
  ${p.name}
</label>
```

## Select

Use `value.bind` on the `<select>` and `model.bind` on each `<option>` for non-string values
(`value` always coerces to a string). `<select multiple>` binds to an **array**.

```html
<!-- single, object values -->
<select value.bind="selectedProduct" matcher.bind="byId">
  <option model.bind="null">Choose…</option>
  <option repeat.for="p of products" model.bind="p">${p.name}</option>
</select>

<!-- multiple -> array -->
<select multiple value.bind="selectedIds">
  <option repeat.for="p of products" model.bind="p.id">${p.name}</option>
</select>
```

`matcher` signature: `(a, b) => boolean`.

## Files

File inputs are read-only — handle the `change` event (or use `files.from-view="files"`; the
`files` property is observed read-only on `<input>`):

```html
<input type="file" multiple accept="image/*" change.trigger="onFiles($event)">
```

```typescript
onFiles(e: Event) {
  const input = e.target as HTMLInputElement;
  this.files = input.files ? Array.from(input.files) : [];
}
```

## Form submission

**A `submit.trigger` handler does NOT call `preventDefault()` by default** — without it the browser
submits the form and reloads the page. Add the `:prevent` event modifier (the idiomatic way), or
prevent it manually:

```html
<!-- preferred: :prevent stops the default navigation -->
<form submit.trigger:prevent="save()">
  <input value.bind="name">
  <button type="submit" disabled.bind="isSubmitting">
    ${isSubmitting ? 'Saving…' : 'Save'}
  </button>
</form>
```

```typescript
async save() {
  this.isSubmitting = true;
  try { await this.api.save(this.form); }
  finally { this.isSubmitting = false; }
}
```

Equivalent manual form: `<form submit.trigger="save($event)">` with `$event.preventDefault()` in
the handler. (Mechanics: the `:prevent` modifier calls `preventDefault()` unconditionally before
the handler runs. The separate "handler returning `true` skips preventDefault" rule only applies
when the app-wide `IListenerBindingOptions.prevent` default is switched on; it is `false` by
default.)

## Validation

Form bindings integrate with `@aurelia/validation` via the `& validate` binding behavior:

```html
<input value.bind="email & validate">
```

See [validation.md](validation.md) for rules, the scoped controller, triggers, and error display.

## Gotchas

- Array/object checkboxes and object selects need **`model.bind`**, not `value` (which stringifies).
- Object equality in checkbox arrays / selects needs **`matcher.bind`**; otherwise only identical
  references match.
- `<input type="number">` with `value.bind` yields a **string** — use `value-as-number.bind` or coerce it.
- `submit.trigger` does **not** preventDefault — use `:prevent` (the page reloads otherwise).
- File inputs can't be written — read `files` via `files.from-view` or a `change.trigger` handler.

## Source

- [Official runtime-html package](https://github.com/aurelia/aurelia/tree/v2.0.0-rc.2/packages/runtime-html)
