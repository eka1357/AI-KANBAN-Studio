import type { BoardData } from "./kanban";

export async function fetchBoard(): Promise<BoardData> {
  const res = await fetch("/api/board", { method: "GET" });
  if (!res.ok) {
    if (res.status === 401) {
      throw new Error("Unauthorized");
    }
    throw new Error("Failed to fetch board");
  }
  return res.json();
}

export async function saveBoard(board: BoardData): Promise<void> {
  const res = await fetch("/api/board", {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(board),
  });
  if (!res.ok) {
    if (res.status === 401) {
      throw new Error("Unauthorized");
    }
    throw new Error("Failed to save board");
  }
}

export async function chatWithAI(message: string, board: BoardData): Promise<{ reply: string, board?: BoardData }> {
  const res = await fetch("/api/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ message, board }),
  });
  if (!res.ok) {
    if (res.status === 401) {
      throw new Error("Unauthorized");
    }
    throw new Error("Failed to chat with AI");
  }
  return res.json();
}
