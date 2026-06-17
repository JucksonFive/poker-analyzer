import { Outlet } from "react-router-dom";
import { Sidebar } from "./Sidebar";
import { Header } from "./Header";

/**
 * Main application layout: sidebar + header + content.
 * Used by all routes.
 */
export function AppLayout({ children }: { children?: React.ReactNode }) {
  return (
    <div className="flex h-screen bg-slate-900">
      <Sidebar />
      <div className="flex flex-col flex-1 overflow-hidden">
        <Header />
        <main className="flex-1 overflow-y-auto p-6 bg-slate-900">
          {children ?? <Outlet />}
        </main>
      </div>
    </div>
  );
}
