# Frontend: Kanban Studio

## Overview

The frontend is a Next.js 16 application (React 19, TypeScript, Tailwind CSS v4) that renders a fully interactive single-board Kanban workspace. It is a pure client-side demo with no backend connectivity yet.

## Tech stack

- **Framework**: Next.js 16, App Router, `"use client"` components
- **Language**: TypeScript (strict)
- **Styling**: Tailwind CSS v4 via PostCSS; all brand colours defined as CSS custom properties in `src/app/globals.css`
- **Drag and drop**: `@dnd-kit/core` and `@dnd-kit/sortable`
- **Unit tests**: Vitest + Testing Library (`npm run test:unit`)
- **E2e tests**: Playwright (`npm run test:e2e`)

## CSS design tokens (globals.css)

| Variable | Value | Usage |
|---|---|---|
| `--accent-yellow` | `#ecad0a` | Column header bar, card count accents |
| `--primary-blue` | `#209dd7` | Links, key UI sections |
| `--secondary-purple` | `#753991` | Submit buttons, important actions |
| `--navy-dark` | `#032147` | Main headings, body text |
| `--gray-text` | `#888888` | Supporting text, labels |
| `--surface` | `#f7f8fb` | Page background |
| `--surface-strong` | `#ffffff` | Column and card backgrounds |
| `--stroke` | `rgba(3,33,71,0.08)` | Borders |
| `--shadow` | `0 18px 40px rgba(3,33,71,0.12)` | Card and column shadows |

Fonts: `Space_Grotesk` (display headings, `--font-display`) and `Manrope` (body, `--font-body`) loaded from Google Fonts via `next/font`.

## Data model (src/lib/kanban.ts)

```ts
type Card   = { id: string; title: string; details: string }
type Column = { id: string; title: string; cardIds: string[] }
type BoardData = { columns: Column[]; cards: Record<string, Card> }
```

- Columns are ordered; each holds an ordered list of card IDs.
- Cards live in a flat map keyed by ID.
- `initialData` seeds 5 columns (Backlog, Discovery, In Progress, Review, Done) with 8 example cards.
- `moveCard(columns, activeId, overId)` — pure function that handles within-column and cross-column moves.
- `createId(prefix)` — generates a unique ID from a random base-36 string and a timestamp.

## Component tree

```
page.tsx
  KanbanBoard          (state owner, DnD context)
    KanbanColumn x 5   (droppable, SortableContext)
      KanbanCard x N   (sortable, drag handle)
      NewCardForm       (add card toggle form)
    DragOverlay
      KanbanCardPreview (ghost card during drag)
```

## Components

### KanbanBoard (src/components/KanbanBoard.tsx)

The root component and single source of truth for board state.

- Holds `board: BoardData` in `useState`, initialised from `initialData`.
- Holds `activeCardId` for the drag overlay.
- Configures `DndContext` with `PointerSensor` (6px activation distance) and `closestCorners` collision detection.
- Handlers:
  - `handleDragStart` — sets `activeCardId`
  - `handleDragEnd` — calls `moveCard` and updates `board.columns`
  - `handleRenameColumn(columnId, title)` — updates column title in state
  - `handleAddCard(columnId, title, details)` — creates a new card with `createId`, appends to column
  - `handleDeleteCard(columnId, cardId)` — removes card from `board.cards` and from the column's `cardIds`
- Renders the page header (with column pill badges) and a 5-column CSS grid.

### KanbanColumn (src/components/KanbanColumn.tsx)

- Uses `useDroppable` from dnd-kit (the column itself is a drop target).
- Wraps cards in `SortableContext` with `verticalListSortingStrategy`.
- Shows a yellow accent bar and card count above the column title.
- Column title is an `<input>` that fires `onRename` on change (inline rename, no confirm step).
- Renders an empty-state placeholder when `cards.length === 0`.
- Renders `NewCardForm` at the bottom.
- `data-testid={column-<id>}` on the section element.

### KanbanCard (src/components/KanbanCard.tsx)

- Uses `useSortable` from dnd-kit; applies `transform` and `transition` styles.
- Reduces opacity to 0.6 while dragging (`isDragging`).
- Shows card title (`h4`), details paragraph, and a "Remove" button.
- `data-testid={card-<id>}` on the article element.

### KanbanCardPreview (src/components/KanbanCardPreview.tsx)

- Stateless ghost card rendered inside `DragOverlay` during an active drag.
- Identical visual to `KanbanCard` but without drag listeners or the remove button.

### NewCardForm (src/components/NewCardForm.tsx)

- Toggle: starts as an "Add a card" dashed button; on click expands to a form.
- Form has a required title input and an optional details textarea.
- On submit: calls `onAdd(title, details)` then resets and collapses.
- Cancel button resets and collapses without submitting.

## Tests

- `src/components/KanbanBoard.test.tsx` — unit tests using Vitest + Testing Library (renders board, user interactions)
- `src/lib/kanban.test.ts` — unit tests for `moveCard` and `createId`
- `tests/` — Playwright e2e tests

## What is NOT yet implemented

- No backend connectivity; all state is in-memory and resets on page reload
- No user authentication or login page
- No AI sidebar
- The Next.js app is configured for `next dev` only; static export config (`output: "export"`) has not been added yet
