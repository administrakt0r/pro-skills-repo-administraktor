# React + TypeScript Component Patterns & Typing Reference

This reference provides production-grade architectural patterns, TypeScript type signatures, and reusable code blueprints for modern React applications.

---

## 1. TypeScript Generic Component Patterns

Generic components allow reusable UI elements to operate over arbitrary data models without sacrificing type safety or forcing consumers to perform unsafe type assertions.

### 1.1 Generic List Component

Use a function declaration or trailing comma syntax `<T,>` in TSX to distinguish generics from JSX tags.

```tsx
import React from 'react';

export interface Identifiable {
  id: string | number;
}

export interface ListProps<T extends Identifiable> {
  items: readonly T[];
  renderItem: (item: T, index: number) => React.ReactNode;
  keyExtractor?: (item: T) => string | number;
  emptyFallback?: React.ReactNode;
  className?: string;
}

export function List<T extends Identifiable>({
  items,
  renderItem,
  keyExtractor = (item) => item.id,
  emptyFallback = <p className="text-gray-500">No items available.</p>,
  className = '',
}: ListProps<T>): React.ReactElement {
  if (items.length === 0) {
    return <>{emptyFallback}</>;
  }

  return (
    <ul className={className} role="list">
      {items.map((item, index) => (
        <li key={keyExtractor(item)}>
          {renderItem(item, index)}
        </li>
      ))}
    </ul>
  );
}
```

### 1.2 Generic Select / Combobox Component

Ensures the selected value matches the item collection type exactly.

```tsx
import React from 'react';

export interface SelectOption<TValue extends string | number> {
  label: string;
  value: TValue;
  disabled?: boolean;
}

export interface SelectProps<TValue extends string | number> {
  options: readonly SelectOption<TValue>[];
  value: TValue;
  onChange: (value: TValue) => void;
  label: string;
  id: string;
  disabled?: boolean;
}

export function Select<TValue extends string | number>({
  options,
  value,
  onChange,
  label,
  id,
  disabled = false,
}: SelectProps<TValue>): React.ReactElement {
  const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    // Cast is safe because option values are constrained to TValue
    onChange(e.target.value as unknown as TValue);
  };

  return (
    <div className="flex flex-col gap-1">
      <label htmlFor={id} className="text-sm font-medium">
        {label}
      </label>
      <select
        id={id}
        value={value}
        onChange={handleChange}
        disabled={disabled}
        className="rounded border p-2"
      >
        {options.map((option) => (
          <option key={String(option.value)} value={option.value} disabled={option.disabled}>
            {option.label}
          </option>
        ))}
      </select>
    </div>
  );
}
```

### 1.3 Discriminated Union Props

Discriminated unions prevent invalid combinations of props at compile time.

```tsx
import React from 'react';

type BaseButtonProps = {
  children: React.ReactNode;
  className?: string;
};

// When 'as' is 'button', standard button HTML attributes are allowed
type ActionButtonProps = BaseButtonProps & {
  as?: 'button';
  onClick: (event: React.MouseEvent<HTMLButtonElement>) => void;
  disabled?: boolean;
  type?: 'button' | 'submit' | 'reset';
  href?: never;
  target?: never;
};

// When 'as' is 'link', standard anchor HTML attributes are required
type LinkButtonProps = BaseButtonProps & {
  as: 'link';
  href: string;
  target?: '_blank' | '_self';
  onClick?: (event: React.MouseEvent<HTMLAnchorElement>) => void;
  disabled?: never;
  type?: never;
};

export type ButtonProps = ActionButtonProps | LinkButtonProps;

export function Button(props: ButtonProps): React.ReactElement {
  if (props.as === 'link') {
    const { as: _, href, target, children, className, onClick } = props;
    return (
      <a href={href} target={target} className={className} onClick={onClick}>
        {children}
      </a>
    );
  }

  const { as: _, onClick, disabled, type = 'button', children, className } = props;
  return (
    <button type={type} onClick={onClick} disabled={disabled} className={className}>
      {children}
    </button>
  );
}
```

---

## 2. Compound Component Pattern

Compound components provide an expressive, declarative API where child components communicate implicitly via a shared Context.

### 2.1 Complete Type-Safe Tabs Implementation

```tsx
import React, { createContext, useContext, useState, useId } from 'react';

interface TabsContextValue {
  activeTab: string;
  setActiveTab: (tabId: string) => void;
  baseId: string;
}

const TabsContext = createContext<TabsContextValue | null>(null);

function useTabsContext(componentName: string): TabsContextValue {
  const context = useContext(TabsContext);
  if (!context) {
    throw new Error(`<${componentName}> must be rendered within a <Tabs> container.`);
  }
  return context;
}

// 1. Root Container
export interface TabsProps {
  defaultValue: string;
  value?: string;
  onValueChange?: (value: string) => void;
  children: React.ReactNode;
  className?: string;
}

export function Tabs({
  defaultValue,
  value,
  onValueChange,
  children,
  className = '',
}: TabsProps): React.ReactElement {
  const [internalTab, setInternalTab] = useState<string>(defaultValue);
  const baseId = useId();

  const activeTab = value !== undefined ? value : internalTab;

  const setActiveTab = (tabId: string) => {
    if (value === undefined) {
      setInternalTab(tabId);
    }
    onValueChange?.(tabId);
  };

  return (
    <TabsContext.Provider value={{ activeTab, setActiveTab, baseId }}>
      <div className={`tabs-root ${className}`}>{children}</div>
    </TabsContext.Provider>
  );
}

// 2. Tab List
export interface TabListProps {
  children: React.ReactNode;
  className?: string;
  ariaLabel?: string;
}

export function TabList({ children, className = '', ariaLabel = 'Navigation tabs' }: TabListProps): React.ReactElement {
  return (
    <div role="tablist" aria-label={ariaLabel} className={`flex border-b ${className}`}>
      {children}
    </div>
  );
}

// 3. Tab Trigger
export interface TabTriggerProps {
  value: string;
  children: React.ReactNode;
  disabled?: boolean;
  className?: string;
}

export function TabTrigger({ value, children, disabled = false, className = '' }: TabTriggerProps): React.ReactElement {
  const { activeTab, setActiveTab, baseId } = useTabsContext('Tabs.Trigger');
  const isSelected = activeTab === value;
  const triggerId = `${baseId}-tab-${value}`;
  const panelId = `${baseId}-panel-${value}`;

  return (
    <button
      id={triggerId}
      role="tab"
      type="button"
      aria-selected={isSelected}
      aria-controls={panelId}
      tabIndex={isSelected ? 0 : -1}
      disabled={disabled}
      onClick={() => setActiveTab(value)}
      className={`px-4 py-2 font-medium transition-colors ${
        isSelected ? 'border-b-2 border-blue-600 text-blue-600' : 'text-gray-600 hover:text-gray-900'
      } ${className}`}
    >
      {children}
    </button>
  );
}

// 4. Tab Panel
export interface TabPanelProps {
  value: string;
  children: React.ReactNode;
  className?: string;
}

export function TabPanel({ value, children, className = '' }: TabPanelProps): React.ReactElement | null {
  const { activeTab, baseId } = useTabsContext('Tabs.Panel');
  const isSelected = activeTab === value;
  const triggerId = `${baseId}-tab-${value}`;
  const panelId = `${baseId}-panel-${value}`;

  if (!isSelected) {
    return null;
  }

  return (
    <div
      id={panelId}
      role="tabpanel"
      aria-labelledby={triggerId}
      tabIndex={0}
      className={`p-4 focus:outline-none ${className}`}
    >
      {children}
    </div>
  );
}

// Attach subcomponents for dot notation
Tabs.List = TabList;
Tabs.Trigger = TabTrigger;
Tabs.Panel = TabPanel;
```

### 2.2 Consumer Usage Example

```tsx
export function SettingsPage() {
  return (
    <Tabs defaultValue="account">
      <Tabs.List ariaLabel="Account settings tabs">
        <Tabs.Trigger value="account">Account</Tabs.Trigger>
        <Tabs.Trigger value="security">Security</Tabs.Trigger>
        <Tabs.Trigger value="billing">Billing</Tabs.Trigger>
      </Tabs.List>

      <Tabs.Panel value="account">
        <h3>Account Settings</h3>
      </Tabs.Panel>
      <Tabs.Panel value="security">
        <h3>Security Settings</h3>
      </Tabs.Panel>
      <Tabs.Panel value="billing">
        <h3>Billing Settings</h3>
      </Tabs.Panel>
    </Tabs>
  );
}
```

---

## 3. Polymorphic Component Pattern

A polymorphic component allows consumers to render the component as any semantic HTML element or React component via the `as` prop while maintaining complete TypeScript prop checking and ref forwarding.

### 3.1 Type Definitions for Polymorphism

```tsx
import React from 'react';

// Extract HTML element attributes omitting colliding props
export type AsProp<E extends React.ElementType> = {
  as?: E;
};

export type PropsToOmit<C extends React.ElementType, P> = keyof (AsProp<C> & P);

// Polymorphic props without ref
export type PolymorphicComponentProps<
  C extends React.ElementType,
  Props = {}
> = React.PropsWithChildren<Props & AsProp<C>> &
  Omit<React.ComponentPropsWithoutRef<C>, PropsToOmit<C, Props>>;

// Polymorphic ref type
export type PolymorphicRef<C extends React.ElementType> =
  React.ComponentPropsWithRef<C>['ref'];

// Complete polymorphic props with ref
export type PolymorphicComponentPropsWithRef<
  C extends React.ElementType,
  Props = {}
> = PolymorphicComponentProps<C, Props> & {
  ref?: PolymorphicRef<C>;
};
```

### 3.2 Implementation: Polymorphic `Text` Component

```tsx
import React, { forwardRef } from 'react';

interface TextOwnProps {
  color?: 'primary' | 'muted' | 'danger';
  size?: 'sm' | 'base' | 'lg' | 'xl';
  weight?: 'normal' | 'medium' | 'bold';
}

export type TextProps<C extends React.ElementType> = PolymorphicComponentPropsWithRef<
  C,
  TextOwnProps
>;

type TextComponent = <C extends React.ElementType = 'span'>(
  props: TextProps<C>
) => React.ReactElement | null;

export const Text: TextComponent = forwardRef(function Text<
  C extends React.ElementType = 'span'
>(
  {
    as,
    children,
    color = 'primary',
    size = 'base',
    weight = 'normal',
    className = '',
    ...restProps
  }: PolymorphicComponentProps<C, TextOwnProps>,
  ref?: PolymorphicRef<C>
) {
  const Component = as || 'span';

  const colorClass = {
    primary: 'text-gray-900',
    muted: 'text-gray-500',
    danger: 'text-red-600',
  }[color];

  const sizeClass = {
    sm: 'text-sm',
    base: 'text-base',
    lg: 'text-lg',
    xl: 'text-xl font-semibold',
  }[size];

  const weightClass = {
    normal: 'font-normal',
    medium: 'font-medium',
    bold: 'font-bold',
  }[weight];

  return (
    <Component
      ref={ref}
      className={`${colorClass} ${sizeClass} ${weightClass} ${className}`.trim()}
      {...restProps}
    >
      {children}
    </Component>
  );
}) as TextComponent;
```

### 3.3 Consumer Usage with Strict Type Validation

```tsx
export function Showcase() {
  return (
    <div>
      {/* Renders as <p> with paragraph props */}
      <Text as="p" size="lg" color="primary">
        Paragraph text
      </Text>

      {/* Renders as <a> with href prop strictly required/allowed */}
      <Text as="a" href="https://example.com" target="_blank" color="muted">
        External Link
      </Text>

      {/* Renders as <h1> */}
      <Text as="h1" size="xl" weight="bold">
        Page Header
      </Text>
    </div>
  );
}
```

---

## 4. Custom Hook Patterns with Proper Typing

### 4.1 Tuple vs. Object Return Types

When a custom hook returns a tuple, use `as const` to preserve exact types rather than widening to union arrays.

```typescript
// Tuple return (like useState)
export function useToggle(initialValue = false): readonly [boolean, () => void, (value: boolean) => void] {
  const [state, setState] = React.useState(initialValue);
  const toggle = React.useCallback(() => setState((v) => !v), []);
  const setExplicit = React.useCallback((value: boolean) => setState(value), []);

  return [state, toggle, setExplicit] as const;
}

// Object return (preferred when returning > 2 items to prevent destructuring order bugs)
export interface UseCounterReturn {
  count: number;
  increment: () => void;
  decrement: () => void;
  reset: () => void;
}

export function useCounter(initialValue = 0): UseCounterReturn {
  const [count, setCount] = React.useState(initialValue);
  const increment = React.useCallback(() => setCount((c) => c + 1), []);
  const decrement = React.useCallback(() => setCount((c) => c - 1), []);
  const reset = React.useCallback(() => setCount(initialValue), [initialValue]);

  return { count, increment, decrement, reset };
}
```

### 4.2 Type-Safe Window / DOM Event Listener Hook

```typescript
import { useEffect, useRef } from 'react';

// Overload 1: Window events
export function useEventListener<K extends keyof WindowEventMap>(
  eventName: K,
  handler: (event: WindowEventMap[K]) => void,
  element?: undefined,
  options?: boolean | AddEventListenerOptions
): void;

// Overload 2: Document events
export function useEventListener<K extends keyof DocumentEventMap>(
  eventName: K,
  handler: (event: DocumentEventMap[K]) => void,
  element: React.RefObject<Document | null> | Document,
  options?: boolean | AddEventListenerOptions
): void;

// Overload 3: HTML element events
export function useEventListener<
  K extends keyof HTMLElementEventMap,
  T extends HTMLElement = HTMLElement
>(
  eventName: K,
  handler: (event: HTMLElementEventMap[K]) => void,
  element: React.RefObject<T | null> | T,
  options?: boolean | AddEventListenerOptions
): void;

// Implementation
export function useEventListener<
  KW extends keyof WindowEventMap,
  KH extends keyof HTMLElementEventMap,
  T extends HTMLElement = HTMLElement
>(
  eventName: KW | KH,
  handler: (event: WindowEventMap[KW] | HTMLElementEventMap[KH] | Event) => void,
  element?: React.RefObject<T | null> | T | Document,
  options?: boolean | AddEventListenerOptions
): void {
  const savedHandler = useRef(handler);

  useEffect(() => {
    savedHandler.current = handler;
  }, [handler]);

  useEffect(() => {
    const targetElement: EventTarget | null =
      element && 'current' in element ? element.current : (element as EventTarget) ?? window;

    if (!targetElement?.addEventListener) return;

    const eventListener = (event: Event) => savedHandler.current(event);
    targetElement.addEventListener(eventName, eventListener, options);

    return () => {
      targetElement.removeEventListener(eventName, eventListener, options);
    };
  }, [eventName, element, options]);
}
```

### 4.3 Generic Debounce Hook

```typescript
import { useState, useEffect } from 'react';

export function useDebounce<T>(value: T, delayMs: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedValue(value);
    }, delayMs);

    return () => {
      clearTimeout(timer);
    };
  }, [value, delayMs]);

  return debouncedValue;
}
```

### 4.4 Type-Safe Async Data Fetching Hook with Cancellation

```typescript
import { useState, useEffect, useCallback, useRef } from 'react';

export type AsyncStatus = 'idle' | 'pending' | 'success' | 'error';

export interface AsyncState<TData, TError = Error> {
  status: AsyncStatus;
  data: TData | null;
  error: TError | null;
  isLoading: boolean;
  isSuccess: boolean;
  isError: boolean;
}

export function useAsync<TData, TError = Error>(
  asyncFunction: (signal: AbortSignal) => Promise<TData>,
  immediate = true
): AsyncState<TData, TError> & { execute: () => Promise<TData | undefined> } {
  const [state, setState] = useState<AsyncState<TData, TError>>({
    status: immediate ? 'pending' : 'idle',
    data: null,
    error: null,
    isLoading: immediate,
    isSuccess: false,
    isError: false,
  });

  const abortControllerRef = useRef<AbortController | null>(null);

  const execute = useCallback(async (): Promise<TData | undefined> => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    const controller = new AbortController();
    abortControllerRef.current = controller;

    setState({
      status: 'pending',
      data: null,
      error: null,
      isLoading: true,
      isSuccess: false,
      isError: false,
    });

    try {
      const result = await asyncFunction(controller.signal);
      if (!controller.signal.aborted) {
        setState({
          status: 'success',
          data: result,
          error: null,
          isLoading: false,
          isSuccess: true,
          isError: false,
        });
        return result;
      }
    } catch (err: unknown) {
      if (!controller.signal.aborted) {
        setState({
          status: 'error',
          data: null,
          error: err as TError,
          isLoading: false,
          isSuccess: false,
          isError: true,
        });
      }
    }
  }, [asyncFunction]);

  useEffect(() => {
    if (immediate) {
      execute();
    }
    return () => {
      abortControllerRef.current?.abort();
    };
  }, [execute, immediate]);

  return { ...state, execute };
}
```

### 4.5 Type-Safe Outside Click Hook

```typescript
import { useEffect, useRef } from 'react';

export function useOnClickOutside<T extends HTMLElement = HTMLElement>(
  handler: (event: MouseEvent | TouchEvent) => void
): React.RefObject<T | null> {
  const ref = useRef<T | null>(null);
  const savedHandler = useRef(handler);

  useEffect(() => {
    savedHandler.current = handler;
  }, [handler]);

  useEffect(() => {
    const listener = (event: MouseEvent | TouchEvent) => {
      const target = event.target as Node | null;
      if (!ref.current || !target || ref.current.contains(target)) {
        return;
      }
      savedHandler.current(event);
    };

    document.addEventListener('mousedown', listener);
    document.addEventListener('touchstart', listener);

    return () => {
      document.removeEventListener('mousedown', listener);
      document.removeEventListener('touchstart', listener);
    };
  }, []);

  return ref;
}
```

---

## 5. Context + Reducer Architecture

Separating the State Context and Dispatch Context prevents components that only dispatch actions from re-rendering every time state changes.

### 5.1 Architecture Implementation

```tsx
import React, { createContext, useContext, useReducer, useMemo } from 'react';

// 1. State Definition
export interface TodoItem {
  id: string;
  title: string;
  completed: boolean;
}

export interface TodoState {
  items: readonly TodoItem[];
  filter: 'all' | 'active' | 'completed';
}

const initialTodoState: TodoState = {
  items: [],
  filter: 'all',
};

// 2. Action Discriminated Union
export type TodoAction =
  | { type: 'ADD_TODO'; payload: { id: string; title: string } }
  | { type: 'TOGGLE_TODO'; payload: { id: string } }
  | { type: 'REMOVE_TODO'; payload: { id: string } }
  | { type: 'SET_FILTER'; payload: { filter: TodoState['filter'] } }
  | { type: 'CLEAR_COMPLETED' };

// Exhaustive checking utility
function assertNever(x: never): never {
  throw new Error(`Unhandled action case: ${JSON.stringify(x)}`);
}

// 3. Pure Reducer
export function todoReducer(state: TodoState, action: TodoAction): TodoState {
  switch (action.type) {
    case 'ADD_TODO': {
      const newItem: TodoItem = {
        id: action.payload.id,
        title: action.payload.title,
        completed: false,
      };
      return { ...state, items: [...state.items, newItem] };
    }
    case 'TOGGLE_TODO': {
      return {
        ...state,
        items: state.items.map((item) =>
          item.id === action.payload.id ? { ...item, completed: !item.completed } : item
        ),
      };
    }
    case 'REMOVE_TODO': {
      return {
        ...state,
        items: state.items.filter((item) => item.id !== action.payload.id),
      };
    }
    case 'SET_FILTER': {
      return { ...state, filter: action.payload.filter };
    }
    case 'CLEAR_COMPLETED': {
      return {
        ...state,
        items: state.items.filter((item) => !item.completed),
      };
    }
    default:
      return assertNever(action);
  }
}

// 4. Split Contexts
const TodoStateContext = createContext<TodoState | null>(null);
const TodoDispatchContext = createContext<React.Dispatch<TodoAction> | null>(null);

// 5. Provider Component
export interface TodoProviderProps {
  children: React.ReactNode;
  initialState?: TodoState;
}

export function TodoProvider({ children, initialState = initialTodoState }: TodoProviderProps): React.ReactElement {
  const [state, dispatch] = useReducer(todoReducer, initialState);

  // Memoize state object if complex; dispatch identity is always stable
  const memoizedState = useMemo(() => state, [state]);

  return (
    <TodoStateContext.Provider value={memoizedState}>
      <TodoDispatchContext.Provider value={dispatch}>
        {children}
      </TodoDispatchContext.Provider>
    </TodoStateContext.Provider>
  );
}

// 6. Custom Consumer Hooks
export function useTodoState(): TodoState {
  const context = useContext(TodoStateContext);
  if (!context) {
    throw new Error('useTodoState must be used within a <TodoProvider>');
  }
  return context;
}

export function useTodoDispatch(): React.Dispatch<TodoAction> {
  const context = useContext(TodoDispatchContext);
  if (!context) {
    throw new Error('useTodoDispatch must be used within a <TodoProvider>');
  }
  return context;
}
```

---

## 6. Event Handler Typing Cheatsheet

### 6.1 Event Type Reference Table

| Event | React Event Type | Common Target Elements | Key Properties |
| :--- | :--- | :--- | :--- |
| Click / Mouse | `React.MouseEvent<T>` | `HTMLButtonElement`, `HTMLAnchorElement`, `HTMLDivElement` | `clientX`, `clientY`, `button`, `shiftKey` |
| Input change | `React.ChangeEvent<T>` | `HTMLInputElement`, `HTMLSelectElement`, `HTMLTextAreaElement` | `target.value`, `target.checked`, `target.files` |
| Form submit | `React.FormEvent<T>` | `HTMLFormElement` | `preventDefault()`, `currentTarget` |
| Keyboard | `React.KeyboardEvent<T>` | `HTMLInputElement`, `HTMLDivElement` | `key`, `code`, `altKey`, `ctrlKey` |
| Focus / Blur | `React.FocusEvent<T>` | `HTMLInputElement`, `HTMLButtonElement` | `relatedTarget` |
| Drag & Drop | `React.DragEvent<T>` | `HTMLDivElement`, `HTMLTableRowElement` | `dataTransfer` |
| Pointer | `React.PointerEvent<T>` | `HTMLCanvasElement`, `HTMLDivElement` | `pointerId`, `pointerType` |
| Clipboard | `React.ClipboardEvent<T>` | `HTMLInputElement`, `HTMLTextAreaElement` | `clipboardData` |

### 6.2 Target vs. CurrentTarget in TypeScript

- `event.currentTarget`: The element to which the handler is attached (strongly typed as generic `T`).
- `event.target`: The element that initiated the event (may be a child inside `T`, typed as `EventTarget & HTMLElement`).

```tsx
const handleButtonClick = (event: React.MouseEvent<HTMLButtonElement>) => {
  // Always safe and matches the generic parameter
  console.log(event.currentTarget.id); // HTMLButtonElement

  // May be a <span> or <svg> inside the button
  if (event.target instanceof HTMLElement) {
    console.log(event.target.tagName);
  }
};
```

### 6.3 Props Typing: Handler Signatures vs. Event Handler Interfaces

```tsx
interface FormInputProps {
  // Option A: Explicit function signature (Recommended for clarity)
  onChange: (value: string, event: React.ChangeEvent<HTMLInputElement>) => void;
  onBlur?: (event: React.FocusEvent<HTMLInputElement>) => void;
  onKeyDown?: (event: React.KeyboardEvent<HTMLInputElement>) => void;

  // Option B: Standard React EventHandler type (Useful when passing directly to JSX element)
  onClick?: React.MouseEventHandler<HTMLInputElement>;
}
```
