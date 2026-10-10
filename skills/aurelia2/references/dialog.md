# `@aurelia/dialog` — Modals & Dialogs

`@aurelia/dialog` provides a DI-driven dialog/modal service. Import from `@aurelia/dialog`.

## Registration

Pick one configuration:

- **`DialogConfigurationStandard`** (recommended) — renders into a native HTML5 `<dialog>`
  element with a real backdrop; modal by default. No CSS required.
- **`DialogConfigurationClassic`** — light-DOM overlay (`<au-dialog-container>` / overlay), matches
  the Aurelia 1 behavior; useful when migrating.
- **`DialogConfiguration`** — base, requires you to supply a custom `renderer`.

```typescript
import Aurelia from 'aurelia';
import { DialogConfigurationStandard } from '@aurelia/dialog';
import { MyApp } from './my-app';

Aurelia
  .register(DialogConfigurationStandard)
  .app(MyApp)
  .start();
```

Customize global defaults:

```typescript
DialogConfigurationStandard.customize(settings => {
  settings.options.modal = true;
  settings.rejectOnCancel = false;   // when true, cancel() rejects the promise instead of resolving
});
```

## Opening a dialog

Resolve `IDialogService` and call `open(...)`. To lazy-load the dialog component, pass a function
that returns the **class** (or a promise of it). The service does not unwrap module namespaces, so
map the `import()` result to the export — `() => import('./confirm-dialog')` alone renders nothing.

```typescript
import { resolve } from 'aurelia';
import { IDialogService } from '@aurelia/dialog';

export class Toolbar {
  private dialogs = resolve(IDialogService);

  async confirmDelete() {
    const { wasCancelled, dialog } = await this.dialogs.open({
      component: () => import('./confirm-dialog').then(m => m.ConfirmDialog),
      model: { message: 'Delete this item?' },
    });

    if (wasCancelled) return;

    const result = await dialog.closed;          // wait for the user to close it
    if (result.status === 'ok' && result.value) {
      // confirmed
    }
  }
}
```

`open()` returns a promise that resolves to `{ wasCancelled, dialog }` once the dialog has opened
(`wasCancelled` is true if `canActivate` blocked it). `dialog.closed` is a promise for the close
result. A shorthand `whenClosed()` skips the open result (since rc.2, calling it with no handler is
typed as `Promise<DialogCloseResult>`):

```typescript
this.dialogs.open({ component: () => import('./confirm-dialog').then(m => m.ConfirmDialog), model: { message: 'Sure?' } })
  .whenClosed(result => {
    if (result.status === 'ok') { /* ... */ }
  });
```

`open()` settings: `component`, `template`, `model` (passed to `activate`), `host`, `container`,
`renderer`, `rejectOnCancel`, and renderer-specific `options` (Standard: `modal`, `overlayStyle`,
`show`, `hide`, `closedby`; Classic: `lock`, `keyboard`, `overlayDismiss`, `startingZIndex`,
`mouseEvent`, `show`, `hide`).

## The dialog component

A dialog component is an ordinary custom element. It resolves `IDialogController` to close itself
and receives the opener's `model` via `activate`.

**confirm-dialog.ts**
```typescript
import { resolve } from 'aurelia';
import { IDialogController } from '@aurelia/dialog';

export class ConfirmDialog {
  private controller = resolve(IDialogController);
  message = '';

  activate(model: { message: string }) {
    this.message = model.message;
  }

  confirm() { this.controller.ok(true); }
  dismiss() { this.controller.cancel(false); }
}
```

**confirm-dialog.html**
```html
<div class="dialog">
  <p>${message}</p>
  <button click.trigger="confirm()">Yes</button>
  <button click.trigger="dismiss()">No</button>
</div>
```

Dialog lifecycle hooks (all optional): `canActivate(model?)` → return `false` to block opening;
`activate(model?)`; `canDeactivate(result)` → return `false` to block closing; `deactivate(result)`.

Closing methods on `IDialogController`:

- `controller.ok(value?)` → closes with `status: 'ok'`.
- `controller.cancel(value?)` → closes with `status: 'cancel'`.
- `controller.error(value)` → closes and **rejects** `dialog.closed` / `whenClosed()` with a
  `DialogCloseError` (`wasCancelled: false`, `value`); bypasses `canDeactivate`.

The close result is `{ status, value }` where `status` is `'ok' | 'cancel' | 'error' | 'abort'`.
`'abort'` is what `ok()`/`cancel()` return when `canDeactivate` returns `false`; the dialog stays open.

## Gotchas

- Resolve `IDialogController` in the dialog component to close it; the `$dialog` property is only
  available after the constructor.
- Classic renderer: `keyboard` is an array (`['Escape', 'Enter']`), not a boolean, and `lock: true`
  (the Classic default) disables Escape/Enter and overlay dismissal unless `keyboard` /
  `overlayDismiss` are set explicitly.
- `rejectOnCancel: true` makes `dialog.closed` / `whenClosed()` reject on cancel (and `open()` reject
  when `canActivate` returns `false`) — use try/catch.
- `error()` skips `canDeactivate`.

## Source

- [Official dialog package](https://github.com/aurelia/aurelia/tree/v2.0.0-rc.2/packages/dialog)
