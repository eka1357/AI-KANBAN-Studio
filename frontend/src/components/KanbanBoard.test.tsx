import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";
import { KanbanBoard } from "@/components/KanbanBoard";

// vi.hoisted runs before vi.mock factories and before imports,
// giving us stable references safe to use inside vi.mock factories.
const { mockRouter } = vi.hoisted(() => ({
  mockRouter: { push: vi.fn() },
}));

// Mock next/navigation. IMPORTANT: return the same `mockRouter` object on
// every call — if useRouter() returns a new object each render, the [router]
// useEffect dependency changes, re-firing fetchBoard and resetting board state.
vi.mock("next/navigation", () => ({
  useRouter: () => mockRouter,
}));

// Mock @/lib/api — inline board data to avoid vi.mock hoisting issues.
// vi.mock factories are hoisted before imports, so imported values (like
// `initialData`) aren't safe to reference inside them.
vi.mock("@/lib/api", () => ({
  fetchBoard: vi.fn().mockResolvedValue({
    columns: [
      { id: "col-backlog", title: "Backlog", cardIds: ["card-1", "card-2"] },
      { id: "col-discovery", title: "Discovery", cardIds: ["card-3"] },
      { id: "col-progress", title: "In Progress", cardIds: ["card-4", "card-5"] },
      { id: "col-review", title: "Review", cardIds: ["card-6"] },
      { id: "col-done", title: "Done", cardIds: ["card-7", "card-8"] },
    ],
    cards: {
      "card-1": { id: "card-1", title: "Align roadmap themes", details: "Draft quarterly themes." },
      "card-2": { id: "card-2", title: "Gather customer signals", details: "Review support tags." },
      "card-3": { id: "card-3", title: "Prototype analytics view", details: "Sketch dashboard." },
      "card-4": { id: "card-4", title: "Refine status language", details: "Standardize labels." },
      "card-5": { id: "card-5", title: "Design card layout", details: "Add hierarchy." },
      "card-6": { id: "card-6", title: "QA micro-interactions", details: "Verify hover states." },
      "card-7": { id: "card-7", title: "Ship marketing page", details: "Final copy approved." },
      "card-8": { id: "card-8", title: "Close onboarding sprint", details: "Document release notes." },
    },
  }),
  saveBoard: vi.fn().mockResolvedValue(undefined),
  chatWithAI: vi.fn(),
}));

// Helper: always re-queries so we never hold a stale DOM reference after re-renders.
const firstColumn = () => screen.getByTestId("column-col-backlog");

describe("KanbanBoard", () => {
  it("renders five columns", async () => {
    render(<KanbanBoard />);
    const columns = await screen.findAllByTestId(/column-/i);
    expect(columns).toHaveLength(5);
  });

  it("renames a column", async () => {
    render(<KanbanBoard />);
    await screen.findAllByTestId(/column-/i);
    const input = within(firstColumn()).getByLabelText("Column title");
    await userEvent.clear(input);
    await userEvent.type(input, "New Name");
    expect(within(firstColumn()).getByLabelText("Column title")).toHaveValue("New Name");
  });

  it("adds and removes a card", async () => {
    render(<KanbanBoard />);
    await screen.findAllByTestId(/column-/i);

    await userEvent.click(within(firstColumn()).getByRole("button", { name: /add a card/i }));

    await userEvent.type(within(firstColumn()).getByPlaceholderText(/card title/i), "New card");
    await userEvent.type(within(firstColumn()).getByPlaceholderText(/details/i), "Notes");

    await userEvent.click(within(firstColumn()).getByRole("button", { name: /add card/i }));

    expect(await screen.findByText("New card")).toBeInTheDocument();

    await userEvent.click(
      within(firstColumn()).getByRole("button", { name: /delete new card/i })
    );

    expect(screen.queryByText("New card")).not.toBeInTheDocument();
  });
});
