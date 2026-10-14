import { LogOut, ShieldCheck } from "lucide-react";
import { Link, Outlet, useNavigate } from "react-router-dom";

import { useAuth } from "../hooks/useAuth";

export default function AppLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/", { replace: true });
  }

  return (
    <div className="min-h-screen flex flex-col">
      <header className="bg-secondary text-white">
        <div className="mx-auto max-w-6xl px-4 py-4 flex items-center justify-between">
          <Link to="/dashboard" className="flex items-center gap-2 font-semibold text-lg">
            <ShieldCheck className="h-6 w-6 text-accent" aria-hidden />
            ClaimIQ
          </Link>
          <div className="flex items-center gap-4 text-sm">
            <span>
              {user?.full_name}{" "}
              <span className="ml-1 rounded bg-slate-700 px-2 py-0.5 text-xs">{user?.role}</span>
            </span>
            <button
              type="button"
              onClick={handleLogout}
              className="flex items-center gap-1 hover:text-accent"
            >
              <LogOut className="h-4 w-4" aria-hidden />
              Sign out
            </button>
          </div>
        </div>
      </header>
      <main className="flex-1 mx-auto w-full max-w-6xl px-4 py-8">
        <Outlet />
      </main>
    </div>
  );
}
