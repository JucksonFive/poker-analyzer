import { useEffect, useRef } from "react";

interface PokerTableProps {
  board: string[];
  heroCards: string[];
  potSize?: number;
  onCardClick?: (card: string) => void;
  className?: string;
}

/**
 * Visual poker table component for hand replay.
 *
 * Renders a felt-green poker table with board cards, hero cards,
 * and optionally villain cards. Supports card selection.
 */
export function PokerTable({
  board,
  heroCards,
  potSize,
  onCardClick,
  className,
}: PokerTableProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    // Draw felt background
    ctx.fillStyle = "#1a6b3c";
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Draw table ellipse
    ctx.beginPath();
    ctx.ellipse(400, 150, 350, 100, 0, 0, Math.PI * 2);
    ctx.strokeStyle = "#0f4f2a";
    ctx.lineWidth = 3;
    ctx.stroke();

    // TODO: Render cards with proper suit colors and symbols
  }, [board, heroCards]);

  return (
    <div className={className}>
      <canvas
        ref={canvasRef}
        width={800}
        height={300}
        className="w-full rounded-lg"
      />
      <div className="mt-2 flex justify-center gap-2">
        {board.map((card, i) => (
          <span
            key={i}
            className="inline-flex items-center justify-center w-10 h-14 bg-white text-slate-900 rounded font-mono text-sm font-bold cursor-pointer hover:ring-2 hover:ring-blue-400"
            onClick={() => onCardClick?.(card)}
          >
            {card}
          </span>
        ))}
      </div>
      {potSize !== undefined && (
        <div className="text-center text-slate-400 text-sm mt-2">
          Pot: ${potSize.toFixed(2)}
        </div>
      )}
    </div>
  );
}
