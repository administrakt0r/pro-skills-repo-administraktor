---
name: react-typescript-development
description: >-
  Develop, refactor, and architect production React applications using TypeScript and modern React 18 and 19 patterns.
  Covers functional components, strict typing, concurrent features (Suspense, transitions), hooks, state management,
  performance optimization, form actions, error boundaries, testing, and architecture conventions.
---

# React + TypeScript Development

Modern React development pairs TypeScript's static type safety with React's declarative, component-driven model. This skill establishes standards for building scalable, maintainable, and resilient React web applications across modern runtime versions (React 18 and React 19).

For deep-dive architectural blueprints (generics, compound components, polymorphic components, custom hooks, and event tables), see the companion guide in [references/component-patterns.md](references/component-patterns.md).

---

## When to Use

- Building or refactoring React applications and design systems with TypeScript.
- Structuring type-safe components, custom hooks, context providers, or external stores.
- Implementing concurrent features such as transitions (`useTransition`, `startTransition`), `useDeferredValue`, and `Suspense`.
- Modernizing legacy React code (class components, `React.FC`, legacy lifecycles) to functional components with strict TypeScript types.
- Adopting React 19 primitives (`useActionState`, `useOptimistic`, the `use` hook, direct `ref` props).
- Optimizing render cycles, profiling memory or layout thrashing, and eliminating unnecessary re-renders.
- Establishing test suites with Vitest and React Testing Library.

---

## Prerequisites

- **Runtime & Tools**: Node.js 18+ (or 20+ LTS), package manager (`npm`, `pnpm`, `yarn`, or `bun`).
- **TypeScript**: TypeScript 5.0+ with modern compiler options.
- **React**: React 18.2+ or React 19.x with matching `@types/react` and `@types/react-dom`.
- **Bundler/Framework**: Vite, Next.js, Remix, Astro, or TanStack Start.

---

## Steps

### 1. Project Architecture & TypeScript Configuration

Organize code by business feature rather than technical layer to keep components, hooks, tests, and types colocated.

#### Feature-Based Directory Layout

```text
src/
├── app/                  # Application root (providers, router, root layout)
├── assets/               # Static assets (images, fonts, global SVGs)
├── components/           # Shared, domain-agnostic UI primitives (Button, Modal, Input)
│   ├── Button/
│   │   ├── Button.tsx
│   │   ├── Button.test.tsx
│   │   ├── Button.types.ts
│   │   └── index.ts
├── features/             # Domain modules (self-contained feature slices)
│   ├── auth/
│   │   ├── components/   # Feature-specific UI components
│   │   ├── hooks/        # Feature-specific custom hooks
│   │   ├── services/     # API queries, mutations, DTO mappers
│   │   ├── types/        # Feature domain types and interfaces
│   │   └── index.ts      # Public API for the feature
├── hooks/                # Global reusable hooks (useMediaQuery, useDebounce)
├── lib/                  # Third-party wrappers (axios/fetch client, queryClient)
├── stores/               # Global state stores (Zustand, Jotai)
├── types/                # Global ambient and shared cross-cutting types
└── main.tsx              # Application entry point
```

#### TypeScript Compiler Settings (`tsconfig.json`)

Ensure strict type checking and modern JSX transform are enabled:

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["DOM", "DOM.Iterable", "ES2022"],
    "module": "ESNext",
    "moduleResolution": "bundler",
    "jsx": "react-jsx",
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true,
    "noImplicitOverride": true,
    "isolatedModules": true,
    "verbatimModuleSyntax": true,
    "skipLibCheck": true
  }
}
```

---

### 2. Typing Components, Props, and Children

#### Component Typing Best Practice

Avoid `React.FC` (or `React.FunctionComponent`). Instead, type props directly as standard TypeScript interfaces or types on function parameters.

```tsx
import React from 'react';

export interface CardProps {
  title: string;
  description?: string;
  children: React.ReactNode;
  footer?: React.ReactNode;
  variant?: 'elevated' | 'outlined' | 'flat';
  className?: string;
}

export function Card({
  title,
  description,
  children,
  footer,
  variant = 'elevated',
  className = '',
}: CardProps): React.ReactElement {
  return (
    <article className={`card card--${variant} ${className}`}>
      <header>
        <h2 className="text-xl font-bold">{title}</h2>
        {description && <p className="text-sm text-gray-600">{description}</p>}
      </header>
      <div className="card-body">{children}</div>
      {footer && <footer className="card-footer">{footer}</footer>}
    </article>
  );
}
```

#### Typing Children

- `React.ReactNode`: Preferred for any renderable content (JSX elements, strings, numbers, fragments, portals, boolean/null).
- `React.ReactElement`: When children must strictly be a single valid React element (not plain text or numbers).
- `(data: T) => React.ReactNode`: For render props patterns.

#### Ref Forwarding: React 18 vs. React 19

In **React 18**, use `forwardRef`:

```tsx
import React, { forwardRef } from 'react';

export interface TextInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label: string;
}

export const TextInput = forwardRef<HTMLInputElement, TextInputProps>(
  function TextInput({ label, id, ...props }, ref) {
    return (
      <div className="input-group">
        <label htmlFor={id}>{label}</label>
        <input ref={ref} id={id} {...props} />
      </div>
    );
  }
);
TextInput.displayName = 'TextInput';
```

In **React 19**, `ref` is a standard prop and `forwardRef` is deprecated:

```tsx
export interface TextInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label: string;
  ref?: React.Ref<HTMLInputElement>;
}

export function TextInput({ label, id, ref, ...props }: TextInputProps) {
  return (
    <div className="input-group">
      <label htmlFor={id}>{label}</label>
      <input ref={ref} id={id} {...props} />
    </div>
  );
}
```

#### Render Props & Higher-Order Components (HOC)

```tsx
// Render Prop Pattern
export interface DataFetcherProps<T> {
  url: string;
  children: (state: { data: T | null; loading: boolean; error: Error | null }) => React.ReactNode;
}

export function DataFetcher<T>({ url, children }: DataFetcherProps<T>): React.ReactElement {
  // fetching logic...
  return <>{children({ data: null, loading: true, error: null })}</>;
}

// Higher-Order Component (HOC) Pattern with Generics
export interface WithAuthProps {
  isAuthenticated: boolean;
}

export function withAuth<P extends object>(
  WrappedComponent: React.ComponentType<P>
): React.FC<P & WithAuthProps> {
  const ComponentWithAuth = ({ isAuthenticated, ...props }: WithAuthProps & P) => {
    if (!isAuthenticated) {
      return <div>Please log in to continue.</div>;
    }
    return <WrappedComponent {...(props as P)} />;
  };

  ComponentWithAuth.displayName = `withAuth(${WrappedComponent.displayName || WrappedComponent.name || 'Component'})`;
  return ComponentWithAuth;
}
```

---

### 3. State Management Patterns

#### Local State: `useState` & `useReducer`

Always provide explicit generic types when state is nullable or complex:

```tsx
// Nullable object state
const [user, setUser] = useState<UserProfile | null>(null);

// Lazy initialization for expensive setup
const [settings, setSettings] = useState<AppSettings>(() => loadSettingsFromStorage());
```

For complex state machines, prefer `useReducer` with discriminated unions (see [references/component-patterns.md](references/component-patterns.md#5-context--reducer-architecture)).

#### External Stores: Zustand

Zustand provides lightweight, atomic, boilerplate-free state management outside the React tree with complete TypeScript support.

```typescript
import { create } from 'zustand';

export interface UserSession {
  userId: string;
  email: string;
}

export interface AuthStoreState {
  session: UserSession | null;
  isAuthenticated: boolean;
  setSession: (session: UserSession) => void;
  clearSession: () => void;
}

export const useAuthStore = create<AuthStoreState>()((set) => ({
  session: null,
  isAuthenticated: false,
  setSession: (session) => set({ session, isAuthenticated: true }),
  clearSession: () => set({ session: null, isAuthenticated: false }),
}));
```

#### Atomic State: Jotai

Jotai organizes state as small composable atoms:

```typescript
import { atom, useAtom, useAtomValue, useSetAtom } from 'jotai';

export const themeAtom = atom<'light' | 'dark'>('light');
export const isDarkModeAtom = atom((get) => get(themeAtom) === 'dark');

export function ThemeToggle() {
  const [theme, setTheme] = useAtom(themeAtom);
  const toggleTheme = () => setTheme((prev) => (prev === 'light' ? 'dark' : 'light'));

  return <button onClick={toggleTheme}>Current: {theme}</button>;
}
```

---

### 4. Concurrent Features & Modern React 18/19 APIs

#### Transitions (`useTransition` and `startTransition`)

Mark expensive, non-urgent updates as transitions so high-priority updates (typing, clicking) stay instant.

```tsx
import { useState, useTransition, ChangeEvent } from 'react';

export function SearchFilter({ items }: { items: string[] }) {
  const [query, setQuery] = useState('');
  const [filteredItems, setFilteredItems] = useState(items);
  const [isPending, startTransition] = useTransition();

  const handleSearch = (e: ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setQuery(value); // High priority: input updates immediately

    startTransition(() => {
      // Low priority: calculation can be deferred or interrupted
      const results = items.filter((item) =>
        item.toLowerCase().includes(value.toLowerCase())
      );
      setFilteredItems(results);
    });
  };

  return (
    <div>
      <input type="search" value={query} onChange={handleSearch} placeholder="Filter list..." />
      {isPending && <span className="spinner">Updating...</span>}
      <ul>
        {filteredItems.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </div>
  );
}
```

#### Deferred Values (`useDeferredValue`)

Defer updating a value until main renders complete:

```tsx
import { useDeferredValue, useState } from 'react';

export function HeavyListContainer({ data }: { data: ComplexData[] }) {
  const [filterText, setFilterText] = useState('');
  const deferredFilter = useDeferredValue(filterText);
  const isStale = filterText !== deferredFilter;

  return (
    <div style={{ opacity: isStale ? 0.7 : 1 }}>
      <input value={filterText} onChange={(e) => setFilterText(e.target.value)} />
      <HeavyDataList filter={deferredFilter} data={data} />
    </div>
  );
}
```

#### React 19 Action Primitives (`useActionState`, `useOptimistic`, `use`)

React 19 introduces native primitives for asynchronous mutations and optimistic updates:

```tsx
import { useActionState, useOptimistic, use } from 'react';

interface CartItem {
  id: string;
  name: string;
}

async function updateCartAction(
  previousState: CartItem[],
  formData: FormData
): Promise<CartItem[]> {
  const newItemName = formData.get('item') as string;
  const response = await fetch('/api/cart', {
    method: 'POST',
    body: JSON.stringify({ name: newItemName }),
  });
  if (!response.ok) throw new Error('Cart update failed');
  return response.json();
}

export function CartManager({ initialItems }: { initialItems: CartItem[] }) {
  const [cart, formAction, isPending] = useActionState(updateCartAction, initialItems);

  const [optimisticCart, addOptimisticItem] = useOptimistic(
    cart,
    (state, newItem: string) => [...state, { id: 'temp-id', name: newItem }]
  );

  const handleSubmit = async (formData: FormData) => {
    const item = formData.get('item') as string;
    addOptimisticItem(item);
    await formAction(formData);
  };

  return (
    <div>
      <form action={handleSubmit}>
        <input name="item" required disabled={isPending} />
        <button type="submit" disabled={isPending}>
          {isPending ? 'Adding...' : 'Add Item'}
        </button>
      </form>
      <ul>
        {optimisticCart.map((i) => (
          <li key={i.id}>{i.name}</li>
        ))}
      </ul>
    </div>
  );
}
```

Reading promises directly inside render using React 19 `use`:

```tsx
import { use, Suspense } from 'react';

function UserProfileCard({ userPromise }: { userPromise: Promise<{ name: string }> }) {
  const user = use(userPromise);
  return <h2>{user.name}</h2>;
}

export function ProfileWrapper({ promise }: { promise: Promise<{ name: string }> }) {
  return (
    <Suspense fallback={<div>Loading profile...</div>}>
      <UserProfileCard userPromise={promise} />
    </Suspense>
  );
}
```

---

### 5. Form Handling & Validation

#### Controlled Form with Type-Safe Validation (Zod)

```tsx
import React, { useState } from 'react';

export interface FormValues {
  email: string;
  age: number;
}

export interface FormErrors {
  email?: string;
  age?: string;
}

export function RegistrationForm() {
  const [values, setValues] = useState<FormValues>({ email: '', age: 18 });
  const [errors, setErrors] = useState<FormErrors>({});

  const validate = (): boolean => {
    const newErrors: FormErrors = {};
    if (!values.email.includes('@')) newErrors.email = 'Valid email is required';
    if (values.age < 18) newErrors.age = 'Must be at least 18';
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!validate()) return;
    // submit data...
  };

  return (
    <form onSubmit={handleSubmit} noValidate>
      <div>
        <label htmlFor="email">Email</label>
        <input
          id="email"
          type="email"
          value={values.email}
          onChange={(e) => setValues((v) => ({ ...v, email: e.target.value }))}
        />
        {errors.email && <span className="error">{errors.email}</span>}
      </div>
      <div>
        <label htmlFor="age">Age</label>
        <input
          id="age"
          type="number"
          value={values.age}
          onChange={(e) => setValues((v) => ({ ...v, age: Number(e.target.value) }))}
        />
        {errors.age && <span className="error">{errors.age}</span>}
      </div>
      <button type="submit">Submit</button>
    </form>
  );
}
```

---

### 6. Error Boundaries & Suspense Boundaries

Combine `Suspense` and `ErrorBoundary` to build robust async views with granular fault isolation.

```tsx
import React, { Component, ErrorInfo, ReactNode, Suspense, lazy } from 'react';

// Reusable TypeScript Class Error Boundary
export interface ErrorBoundaryProps {
  children: ReactNode;
  fallback: (error: Error, reset: () => void) => ReactNode;
  onCatch?: (error: Error, errorInfo: ErrorInfo) => void;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  public override state: ErrorBoundaryState = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  public override componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    this.props.onCatch?.(error, errorInfo);
  }

  private reset = (): void => {
    this.setState({ hasError: false, error: null });
  };

  public override render(): ReactNode {
    if (this.state.hasError && this.state.error) {
      return this.props.fallback(this.state.error, this.reset);
    }
    return this.props.children;
  }
}

// Lazy loading component
const AnalyticsWidget = lazy(() => import('./AnalyticsWidget'));

export function ResilientDashboard() {
  return (
    <ErrorBoundary
      fallback={(error, reset) => (
        <div className="alert alert-danger">
          <h3>Failed to load analytics: {error.message}</h3>
          <button onClick={reset}>Retry</button>
        </div>
      )}
    >
      <Suspense fallback={<div className="skeleton-loader">Loading analytics...</div>}>
        <AnalyticsWidget />
      </Suspense>
    </ErrorBoundary>
  );
}
```

---

### 7. Performance Optimization

1. **Avoid premature optimization**: Only introduce `React.memo`, `useMemo`, and `useCallback` when profiling reveals measurable re-render bottlenecks or when passing callbacks to memoized children.
2. **Push state down**: Colocate state in the lowest common ancestor rather than lifting it to top-level containers.
3. **Memoize context values**: Always wrap Context Provider `value` objects in `useMemo` to prevent all consumers from re-rendering on parent updates.

```tsx
import React, { useState, useMemo, useCallback } from 'react';

export const MemoizedRow = React.memo(function Row({
  id,
  title,
  onSelect,
}: {
  id: string;
  title: string;
  onSelect: (id: string) => void;
}) {
  return (
    <div onClick={() => onSelect(id)}>
      <h4>{title}</h4>
    </div>
  );
});

export function ItemTable({ items }: { items: Array<{ id: string; title: string }> }) {
  const [selectedId, setSelectedId] = useState<string | null>(null);

  // Stable callback reference
  const handleSelect = useCallback((id: string) => {
    setSelectedId(id);
  }, []);

  return (
    <div>
      <p>Selected: {selectedId}</p>
      {items.map((item) => (
        <MemoizedRow
          key={item.id}
          id={item.id}
          title={item.title}
          onSelect={handleSelect}
        />
      ))}
    </div>
  );
}
```

---

### 8. Testing with Vitest and React Testing Library

Write integration tests that interact with components the way end-users do (querying by accessible role and label, dispatching user events).

#### Example Test Suite (`src/components/Button/Button.test.tsx`)

```tsx
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import React from 'react';
import { Button } from './Button';

describe('<Button />', () => {
  it('renders button with accessible role and text', () => {
    render(<Button onClick={() => {}}>Confirm Action</Button>);

    const buttonElement = screen.getByRole('button', { name: /confirm action/i });
    expect(buttonElement).toBeInTheDocument();
  });

  it('handles user click events', async () => {
    const user = userEvent.setup();
    const handleClick = vi.fn();

    render(<Button onClick={handleClick}>Submit</Button>);

    await user.click(screen.getByRole('button', { name: /submit/i }));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('disables user interaction when disabled prop is set', async () => {
    const user = userEvent.setup();
    const handleClick = vi.fn();

    render(<Button onClick={handleClick} disabled>Disabled</Button>);

    const button = screen.getByRole('button', { name: /disabled/i });
    expect(button).toBeDisabled();

    await user.click(button);
    expect(handleClick).not.toHaveBeenCalled();
  });
});
```

#### Testing Custom Hooks with `renderHook`

```tsx
import { describe, it, expect } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useCounter } from '../../hooks/useCounter';

describe('useCounter', () => {
  it('increments and decrements counter state', () => {
    const { result } = renderHook(() => useCounter(5));

    expect(result.current.count).toBe(5);

    act(() => {
      result.current.increment();
    });
    expect(result.current.count).toBe(6);

    act(() => {
      result.current.decrement();
    });
    expect(result.current.count).toBe(5);
  });
});
```

---

## Best Practices

- **Explicit Component Contracts**: Always define an explicit `Props` interface for components. Avoid broad types like `any` or untyped `Record<string, unknown>`.
- **Pure Renders**: Keep component render functions pure. Never mutate props, external variables, or state directly during render. All side effects belong in effects or event handlers.
- **Idempotent Effects**: In React 18+ StrictMode, effects mount, unmount, and remount in development. Always return a cleanup function from `useEffect` to abort fetch requests, unsubscribe from streams, or remove event listeners.
- **Derived State Over Synchronized State**: Compute values on the fly during render (or via `useMemo` if computationally expensive). Do not synchronize prop changes into state using `useEffect`.
- **Split Contexts**: Separate volatile state contexts from action dispatch contexts to prevent unnecessary re-rendering across deep component trees.
- **Keys in Lists**: Always use unique, stable IDs for `key` props (e.g. database UUIDs). Never use array indices when items can be filtered, reordered, or deleted.

---

## Common Pitfalls

- **`React.FC` Type Pollution**: Using `React.FC` which historically injected implicit `children` and complicates generic signatures.
- **Stale Closures**: Referencing mutable values inside `useEffect` or `useCallback` without declaring them in dependency arrays or without functional state updaters (`setState(prev => prev + 1)`).
- **Defining Components Inside Other Components**: Declaring a component function inside another component's body. This re-creates the component identity on every single render, destroying state and triggering remounts.
- **Recreating Context Values**: Supplying inline object literals directly to `Provider value={{ state, dispatch }}` without `useMemo`, causing all subscribers to re-render on any parent update.
- **Overusing `useEffect` for Data Fetching**: Building manual fetch-in-effect flows without race condition guards or cancellation. Use dedicated data-fetching libraries (e.g., TanStack Query) or modern Suspense / React 19 Actions.

---

## Verification

Before finalizing any React + TypeScript implementation, run the following verification checks:

1. **Type Checking**:
   ```bash
   npx tsc --noEmit
   ```
   Must pass with 0 errors.

2. **Linting & Formatting**:
   ```bash
   npx eslint . --ext .ts,.tsx
   ```
   Ensure no unescaped dependencies in `useEffect` or unsafe `any` usages.

3. **Automated Test Suite**:
   ```bash
   npx vitest run
   ```
   Verify all unit and component tests pass.

4. **Production Build**:
   ```bash
   npm run build
   ```
   Confirm bundle compilation, asset tree generation, and chunk size warnings pass within target thresholds.
