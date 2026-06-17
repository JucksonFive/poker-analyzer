import { useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { importApi } from "@/api/client";
import { useImportStore } from "@/stores/useImportStore";
import { Upload, CheckCircle, AlertCircle } from "lucide-react";

export default function Import() {
  const navigate = useNavigate();
  const { isImporting, handsProcessed, handsTotal, errors, setImporting, setProgress, addError, reset } =
    useImportStore();
  const [dragOver, setDragOver] = useState(false);

  const handleFile = useCallback(
    async (file: File) => {
      const allowedExtensions = [".txt", ".hh", ".xml"];
      const suffix = "." + file.name.split(".").pop()?.toLowerCase();

      if (!allowedExtensions.includes(suffix)) {
        addError(`Unsupported file type: ${suffix}. Allowed: .txt, .hh, .xml`);
        return;
      }

      reset();
      setImporting(true, 0, 0);

      try {
        const response = await importApi.upload(file);
        const reader = response.body?.getReader();
        if (!reader) {
          addError("No response stream available");
          setImporting(false);
          return;
        }

        const decoder = new TextDecoder();
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const text = decoder.decode(value);
          const lines = text.split("\n");
          for (const line of lines) {
            if (!line.startsWith("data: ")) continue;
            try {
              const event = JSON.parse(line.slice(6));
              if (event.hands_processed !== undefined) {
                setProgress(event.hands_processed, event.hands_total ?? 0);
              }
              if (event.errors?.length > 0) {
                event.errors.forEach((e: string) => addError(e));
              }
              if (event.status === "completed") {
                setImporting(false);
              }
            } catch {
              // skip malformed SSE lines
            }
          }
        }
      } catch (err) {
        addError(String(err));
        setImporting(false);
      }
    },
    [setImporting, setProgress, addError, reset],
  );

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragOver(false);
      const files = e.dataTransfer.files;
      if (files.length > 0) handleFile(files[0]);
    },
    [handleFile],
  );

  return (
    <div className="space-y-6 max-w-xl mx-auto">
      <h1 className="text-2xl font-semibold text-slate-200">Import</h1>

      {/* Drop zone */}
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setDragOver(true);
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        className={`border-2 border-dashed rounded-xl p-12 text-center transition-colors ${
          dragOver
            ? "border-blue-400 bg-blue-900/20"
            : "border-slate-700 hover:border-slate-500"
        }`}
      >
        <Upload size={48} className="mx-auto text-slate-500 mb-4" />
        <p className="text-slate-300 font-medium mb-2">
          Drag & drop hand history files here
        </p>
        <p className="text-sm text-slate-500 mb-4">
          Supports PokerStars, GGPoker, and Ignition/Bovada formats
        </p>
        <label className="inline-block px-6 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 cursor-pointer transition-colors">
          Browse Files
          <input
            type="file"
            accept=".txt,.hh,.xml"
            className="hidden"
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file) handleFile(file);
            }}
          />
        </label>
      </div>

      {/* Progress */}
      {isImporting && (
        <div className="bg-slate-800 rounded-lg p-4 space-y-3">
          <div className="flex items-center justify-between text-sm">
            <span className="text-slate-300">Importing...</span>
            <span className="text-slate-400">
              {handsProcessed.toLocaleString()}
              {handsTotal > 0 && ` / ${handsTotal.toLocaleString()}`} hands
            </span>
          </div>
          <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
            <div
              className="h-full bg-blue-600 transition-all duration-300 rounded-full"
              style={{
                width: `${handsTotal > 0 ? (handsProcessed / handsTotal) * 100 : 10}%`,
              }}
            />
          </div>
        </div>
      )}

      {/* Errors */}
      {errors.length > 0 && (
        <div className="bg-red-900/20 border border-red-800 rounded-lg p-4">
          <h3 className="text-red-400 font-medium flex items-center gap-2 mb-2">
            <AlertCircle size={16} />
            Import Errors
          </h3>
          <ul className="space-y-1">
            {errors.map((err, i) => (
              <li key={i} className="text-sm text-red-300">
                {err}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Success — redirect CTA */}
      {!isImporting && handsProcessed > 0 && errors.length === 0 && (
        <div className="bg-green-900/20 border border-green-800 rounded-lg p-4 text-center">
          <CheckCircle size={24} className="mx-auto text-green-400 mb-2" />
          <p className="text-green-300 font-medium mb-3">
            {handsProcessed.toLocaleString()} hands imported successfully!
          </p>
          <button
            onClick={() => navigate("/")}
            className="px-4 py-2 bg-green-700 text-white text-sm rounded-lg hover:bg-green-600 transition-colors"
          >
            View Dashboard
          </button>
        </div>
      )}
    </div>
  );
}
