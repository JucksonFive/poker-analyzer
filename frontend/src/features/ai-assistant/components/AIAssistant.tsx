import { useState, useRef, useEffect } from "react";
import { aiApi } from "@/api/client";
import { useAIStore } from "@/stores/useAIStore";
import { useAppStore } from "@/stores/useAppStore";
import { Bot, Send, User } from "lucide-react";

const EXAMPLE_QUESTIONS = [
  "What is my VPIP over the last month?",
  "Which position am I losing the most money from?",
  "Show me my biggest winning hands this week",
  "What is my 3Bet percentage from the button?",
];

export default function AIAssistant() {
  const [input, setInput] = useState("");
  const { messages, isLoading, addMessage, setIsLoading } = useAIStore();
  const { aiEnabled } = useAppStore();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSubmit = async (question?: string) => {
    const q = question ?? input;
    if (!q.trim() || isLoading) return;

    addMessage({ role: "user", content: q, timestamp: new Date() });
    setInput("");
    setIsLoading(true);

    try {
      const response = await aiApi.query(q);
      addMessage({
        role: "assistant",
        content: response.answer,
        sql: response.sql_used,
        timestamp: new Date(),
      });
    } catch {
      addMessage({
        role: "assistant",
        content:
          "Sorry, I encountered an error processing your question. Please try again.",
        timestamp: new Date(),
      });
    } finally {
      setIsLoading(false);
    }
  };

  if (!aiEnabled) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center max-w-md">
          <Bot size={48} className="mx-auto text-slate-600 mb-4" />
          <h2 className="text-lg font-semibold text-slate-200 mb-2">
            AI Assistant Disabled
          </h2>
          <p className="text-slate-400">
            The AI assistant is currently disabled. Enable it in settings to use
            natural language queries over your poker data.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)] max-w-3xl mx-auto">
      <h1 className="text-2xl font-semibold text-slate-200 mb-4">
        AI Assistant
      </h1>

      {/* Chat area */}
      <div className="flex-1 overflow-y-auto space-y-4 mb-4">
        {messages.length === 0 && (
          <div className="text-center py-12">
            <Bot size={48} className="mx-auto text-slate-600 mb-4" />
            <p className="text-slate-400 mb-6">
              Ask questions about your poker data in natural language.
            </p>
            <div className="grid grid-cols-2 gap-2 max-w-lg mx-auto">
              {EXAMPLE_QUESTIONS.map((q) => (
                <button
                  key={q}
                  onClick={() => handleSubmit(q)}
                  className="text-left text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 px-3 py-2 rounded transition-colors"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          <div
            key={i}
            className={`flex gap-3 ${
              msg.role === "user" ? "justify-end" : ""
            }`}
          >
            {msg.role === "assistant" && (
              <Bot size={18} className="shrink-0 mt-1 text-blue-400" />
            )}
            <div
              className={`max-w-[80%] rounded-lg px-4 py-3 ${
                msg.role === "user"
                  ? "bg-blue-600 text-white"
                  : "bg-slate-800 text-slate-200"
              }`}
            >
              <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
              {msg.sql && (
                <details className="mt-2">
                  <summary className="text-xs text-slate-400 cursor-pointer">
                    View SQL query
                  </summary>
                  <pre className="mt-1 text-xs bg-slate-900 p-2 rounded text-slate-300 overflow-x-auto">
                    {msg.sql}
                  </pre>
                </details>
              )}
            </div>
            {msg.role === "user" && (
              <User size={18} className="shrink-0 mt-1 text-slate-400" />
            )}
          </div>
        ))}

        {isLoading && (
          <div className="flex gap-3">
            <Bot size={18} className="shrink-0 mt-1 text-blue-400" />
            <div className="bg-slate-800 rounded-lg px-4 py-3">
              <div className="flex items-center gap-1">
                <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce [animation-delay:-0.3s]" />
                <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce [animation-delay:-0.15s]" />
                <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" />
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t border-slate-800 pt-4">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSubmit()}
            placeholder="Ask about your poker data..."
            className="flex-1 bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-600"
            disabled={isLoading}
          />
          <button
            onClick={() => handleSubmit()}
            disabled={isLoading || !input.trim()}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <Send size={16} />
          </button>
        </div>
        <p className="text-xs text-slate-500 mt-2">
          Data sent to Anthropic API for processing. No raw hand data is
          shared — only aggregated statistics.
        </p>
      </div>
    </div>
  );
}
