import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  ScrollText,
  Users,
  Bot,
  Upload,
  Calendar,
} from "lucide-react";

const NAV_ITEMS = [
  { to: "/", icon: LayoutDashboard, label: "Dashboard" },
  { to: "/hands", icon: ScrollText, label: "Hands" },
  { to: "/players", icon: Users, label: "Players" },
  { to: "/ai", icon: Bot, label: "AI Assistant" },
  { to: "/import", icon: Upload, label: "Import" },
  { to: "/sessions", icon: Calendar, label: "Sessions" },
];

export function Sidebar() {
  return (
    <aside className="w-56 bg-sidebar-bg border-r border-slate-800 flex flex-col shrink-0">
      {/* Logo */}
      <div className="flex items-center gap-2 px-4 py-4 border-b border-slate-800">
        <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-sm font-bold">
          P
        </div>
        <span className="text-sm font-semibold text-slate-200">
          Poker Analytics
        </span>
      </div>

      {/* Navigation */}
      <nav className="flex-1 py-3 px-2 space-y-1">
        {NAV_ITEMS.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === "/"}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors ${
                isActive
                  ? "bg-sidebar-active text-white"
                  : "text-slate-400 hover:bg-sidebar-hover hover:text-slate-200"
              }`
            }
          >
            <Icon size={18} />
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div className="px-4 py-3 border-t border-slate-800 text-xs text-slate-500">
        v0.1.0 MVP
      </div>
    </aside>
  );
}
