import { Routes, Route } from "react-router-dom";
import { lazy, Suspense } from "react";
import { AppLayout } from "@/shared/components/AppLayout";
import { ErrorBoundary } from "@/shared/components/ErrorBoundary";

// Lazy-loaded feature pages
const Dashboard = lazy(() => import("@/features/dashboard/components/Dashboard"));
const HandExplorer = lazy(() => import("@/features/hand-explorer/components/HandExplorer"));
const HandReplay = lazy(() => import("@/features/hand-explorer/components/HandReplay"));
const PlayerAnalysis = lazy(() => import("@/features/player-analysis/components/PlayerAnalysis"));
const AIAssistant = lazy(() => import("@/features/ai-assistant/components/AIAssistant"));
const Import = lazy(() => import("@/features/import/components/Import"));
const SessionTracker = lazy(() => import("@/features/session-tracker/components/SessionTracker"));

function PageLoader() {
  return (
    <div className="flex items-center justify-center h-96">
      <div className="animate-spin h-8 w-8 border-3 border-blue-500 border-t-transparent rounded-full" />
    </div>
  );
}

export default function App() {
  return (
    <ErrorBoundary>
      <AppLayout>
        <Suspense fallback={<PageLoader />}>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/hands" element={<HandExplorer />} />
            <Route path="/hands/:handId" element={<HandReplay />} />
            <Route path="/players" element={<PlayerAnalysis />} />
            <Route path="/players/:playerName" element={<PlayerAnalysis />} />
            <Route path="/ai" element={<AIAssistant />} />
            <Route path="/import" element={<Import />} />
            <Route path="/sessions" element={<SessionTracker />} />
          </Routes>
        </Suspense>
      </AppLayout>
    </ErrorBoundary>
  );
}
