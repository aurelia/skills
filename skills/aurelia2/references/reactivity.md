# Observation, Services, and Dependency Injection

### `@watch` Decorator

React to property changes with automatic dependency tracking:

```typescript
import { watch } from '@aurelia/runtime-html';

export class UserProfile {
  firstName = 'John';
  lastName = 'Doe';

  @watch('firstName')
  firstNameChanged(newValue: string, oldValue: string) {
    console.log(`First name: ${oldValue} -> ${newValue}`);
  }

  // Watch a computed expression with a function
  @watch(vm => `${vm.firstName} ${vm.lastName}`)
  fullNameChanged(newFullName: string) {
    console.log('Full name is now:', newFullName);
  }
}
```

Watchers activate after binding and deactivate before unbinding.

### `@observable` Decorator

Similar to `@bindable` change callbacks, but for internal (non-bound) properties:

```typescript
import { observable } from 'aurelia';

export class Car {
  @observable color = 'blue';

  // Convention: propertyName + "Changed"
  colorChanged(newValue: string, oldValue: string) {
    console.log(`Color changed: ${oldValue} -> ${newValue}`);
  }
}
```

The callback only fires when the value actually changes (no duplicate calls for same value).

## Event Aggregator

Lightweight pub/sub for cross-component communication:

```typescript
import { IEventAggregator, resolve } from 'aurelia';

export class Publisher {
  private ea = resolve(IEventAggregator);

  save() {
    this.ea.publish('item:saved', { id: 1 });
  }
}

export class Subscriber {
  private ea = resolve(IEventAggregator);
  private subscription?: { dispose(): void };

  bound() {
    this.subscription = this.ea.subscribe('item:saved', (payload: any) => {
      console.log('Item saved:', payload);
    });
  }

  unbinding() {
    this.subscription?.dispose(); // Always dispose to prevent memory leaks
  }
}
```

Type-safe events with classes:
```typescript
export class UserSaved {
  constructor(public readonly userId: string) {}
}

// Publishing
this.ea.publish(new UserSaved('abc'));

// Subscribing
this.ea.subscribe(UserSaved, ({ userId }) => {
  console.log('User saved:', userId);
});
```

## Dependency Injection (Advanced Patterns)

### Creating Interfaces

```typescript
import { DI } from '@aurelia/kernel';

export interface IApiService {
  get(url: string): Promise<unknown>;
}

export const IApiService = DI.createInterface<IApiService>('IApiService', x =>
  x.singleton(ApiService)
);

export class ApiService implements IApiService {
  async get(url: string): Promise<unknown> {
    const response = await fetch(url);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  }
}
```

### Registration Types

```typescript
import { Registration } from '@aurelia/kernel';

// Singleton  -  one instance shared across the container
Registration.singleton(IApiService, ApiService);

// Transient  -  new instance per injection
Registration.transient(IApiService, ApiService);

// Instance  -  use a pre-created instance
Registration.instance(IApiService, myApiInstance);

// Callback  -  factory function called each time
Registration.callback(IApiService, container => new ApiService(container.get(ILogger)));

// CachedCallback  -  factory called once, then cached
Registration.cachedCallback(IApiService, container => new ApiService());
```

### Resolve Modifiers

```typescript
import { resolve, all, lazy, newInstanceOf } from 'aurelia';

export class MyComponent {
  // Resolve all registered implementations of an interface
  private plugins: IPlugin[] = resolve(all(IPlugin));

  // Lazy resolution (factory function)
  private getService: () => IService = resolve(lazy(IService));

  // New isolated instance (not the shared singleton)
  private privateEa = resolve(newInstanceOf(IEventAggregator));
}
```

## Observation choices

Plain view-model properties used in bindings are observed automatically. `@observable` adds a change callback; it is not required on every bound property. Plain getters also track dependencies. Use `@computed` only when you need explicit control; method observation is experimental in RC.1/RC.2.

Use observable collection methods (`push`, `splice`, `pop`, and similar) or replace the array. Direct index assignment does not notify the repeater's collection observer; adding `@observable` to the array field does not fix that.

Dispose manual observers and subscriptions when their owner unbinds. Recreate them when it binds again. Clean up only resources the component owns.

## Sources

- [Dependency injection](https://docs.aurelia.io/getting-to-know-aurelia/dependency-injection)
- [Official runtime source](https://github.com/aurelia/aurelia/tree/master/packages/runtime/src)
- [Official kernel source](https://github.com/aurelia/aurelia/tree/master/packages/kernel/src)
