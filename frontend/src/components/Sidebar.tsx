"use client";

import { useState } from "react";
import { type BoardData } from "@/lib/kanban";
import { chatWithAI } from "@/lib/api";

type SidebarProps = {
  board: BoardData;
  onUpdateBoard: (board: BoardData) => void;
  onError: (msg: string) => void;
};

type ChatMessage = {
  id: string;
  role: "user" | "ai";
  content: string;
};

export function Sidebar({ board, onUpdateBoard, onError }: SidebarProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { id: `msg-${Date.now()}-u`, role: "user", content: userMessage }]);
    setIsLoading(true);

    try {
      const res = await chatWithAI(userMessage, board);
      setMessages((prev) => [...prev, { id: `msg-${Date.now()}-a`, role: "ai", content: res.reply }]);
      if (res.board) {
        onUpdateBoard(res.board);
      }
    } catch (err: any) {
      onError(err.message || "Failed to contact AI.");
      setMessages((prev) => [
        ...prev,
        { id: `msg-${Date.now()}-e`, role: "ai", content: "Sorry, I encountered an error while processing your request." },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      {/* Floating Action Button to open sidebar */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed bottom-6 right-6 z-40 rounded-full bg-[var(--primary-blue)] p-4 text-white shadow-lg transition hover:brightness-110"
        >
          <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
        </button>
      )}

      {/* Sidebar Panel */}
      <div
        className={`fixed right-0 top-0 z-50 h-full w-[380px] max-w-full transform flex-col border-l border-[var(--stroke)] bg-white/95 shadow-2xl backdrop-blur transition-transform duration-300 ${
          isOpen ? "translate-x-0" : "translate-x-full"
        } flex`}
      >
        <div className="flex items-center justify-between border-b border-[var(--stroke)] px-6 py-4">
          <h2 className="font-display font-semibold text-[var(--navy-dark)]">AI Assistant</h2>
          <button
            onClick={() => setIsOpen(false)}
            className="rounded-full p-2 text-[var(--gray-text)] transition hover:bg-[var(--surface)] hover:text-[var(--navy-dark)]"
          >
            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.length === 0 ? (
            <div className="text-center text-sm text-[var(--gray-text)]">
              How can I help you manage your board today?
            </div>
          ) : (
            messages.map((msg) => (
              <div
                key={msg.id}
                className={`max-w-[85%] rounded-2xl p-4 text-sm ${
                  msg.role === "user"
                    ? "ml-auto bg-[var(--primary-blue)] text-white"
                    : "bg-[var(--surface)] text-[var(--navy-dark)]"
                }`}
              >
                {msg.content}
              </div>
            ))
          )}
          {isLoading && (
            <div className="bg-[var(--surface)] text-[var(--navy-dark)] max-w-[85%] rounded-2xl p-4 text-sm animate-pulse">
              Thinking...
            </div>
          )}
        </div>

        <div className="border-t border-[var(--stroke)] p-6">
          <form onSubmit={handleSend} className="relative">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask me anything..."
              className="w-full rounded-full border border-[var(--stroke)] bg-[var(--surface)] py-3 pl-4 pr-12 text-sm text-[var(--navy-dark)] outline-none transition focus:border-[var(--primary-blue)]"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={!input.trim() || isLoading}
              className="absolute right-2 top-1/2 flex h-8 w-8 -translate-y-1/2 items-center justify-center rounded-full bg-[var(--primary-blue)] text-white transition disabled:opacity-50 hover:brightness-110"
            >
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            </button>
          </form>
        </div>
      </div>
    </>
  );
}
