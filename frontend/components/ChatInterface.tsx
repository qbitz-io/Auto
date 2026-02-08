"use client";

import React, { useState, useEffect, useRef } from "react";

interface Message {
  id: string;
  sender: "user" | "system";
  text: string;
}

export function ChatInterface() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Scroll chat to bottom on new message
  const chatEndRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;
    setError(null);

    // Add user message
    const userMessage: Message = {
      id: `user-${Date.now()}`,
      sender: "user",
      text: input.trim(),
    };
    setMessages((msgs) => [...msgs, userMessage]);

    setIsSending(true);
    setInput("");

    try {
      // Send POST request with JSON body {task: message, context: {}}
      const response = await fetch("http://localhost:8000/api/task", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ task: userMessage.text, context: {} }),
        mode: "cors",
      });

      if (!response.ok) {
        throw new Error(`Server error: ${response.statusText}`);
      }

      const data = await response.json();

      // Add system message with the output from the orchestrator
      const output = data?.result?.output || data?.result || JSON.stringify(data);
      const systemMessage: Message = {
        id: `system-${Date.now()}`,
        sender: "system",
        text: typeof output === "string" ? output : JSON.stringify(output, null, 2),
      };
      setMessages((msgs) => [...msgs, systemMessage]);
    } catch (err) {
      setError("Failed to send task request.");
    } finally {
      setIsSending(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (!isSending) {
        handleSend();
      }
    }
  };

  return (
    <div className="flex flex-col h-full max-w-3xl mx-auto bg-gray-900 rounded-lg shadow-lg p-4">
      <h2 className="text-2xl font-semibold mb-4 text-white">Describe Your Build Task</h2>

      <div className="flex-1 overflow-y-auto mb-4 p-2 bg-gray-800 rounded">
        {messages.length === 0 && (
          <p className="text-gray-400">Type what you want to build and press Enter.</p>
        )}
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`mb-2 max-w-[80%] whitespace-pre-wrap rounded px-3 py-2 ${
              msg.sender === "user"
                ? "bg-blue-600 text-white self-end"
                : "bg-gray-700 text-gray-200 self-start"
            }`}
            style={{ alignSelf: msg.sender === "user" ? "flex-end" : "flex-start" }}
          >
            {msg.text}
          </div>
        ))}
        <div ref={chatEndRef} />
      </div>

      {error && <div className="text-red-500 mb-2">Error: {error}</div>}

      <textarea
        className="w-full rounded p-2 resize-none bg-gray-700 text-white placeholder-gray-400"
        rows={3}
        placeholder="Describe what you want to build..."
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
        disabled={isSending}
        aria-label="Build task input"
      />

      <button
        onClick={handleSend}
        disabled={isSending || !input.trim()}
        className={`mt-2 px-4 py-2 rounded bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-semibold`}
        aria-label="Send build task"
      >
        {isSending ? "Building..." : "Send"}
      </button>
    </div>
  );
}
