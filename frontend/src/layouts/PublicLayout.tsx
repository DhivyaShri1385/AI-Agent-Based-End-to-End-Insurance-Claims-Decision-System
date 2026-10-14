import { ShieldCheck } from "lucide-react";
import { Link, Outlet } from "react-router-dom";

import { useAuth } from "../hooks/useAuth";

export default function PublicLayout() {
  const { user } = useAuth();

  return (
    <div className="min-h-screen flex flex-col">
      <header className="bg-secondary text-white">
        <div className="mx-auto max-w-6xl px-4 py-4 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2 font-semibold text-lg">
            <ShieldCheck className="h-6 w-6 text-accent" aria-hidden />
            ClaimIQ
          </Link>
          <nav className="flex gap-4 text-sm">
            <Link to="/status" className="hover:text-accent">
              System status
            </Link>
            {user ? (
              <Link to="/dashboard" className="hover:text-accent">
                Dashboard
              </Link>
            ) : (
              <>
                <Link to="/login" className="hover:text-accent">
                  Sign in
                </Link>
                <Link to="/register" className="hover:text-accent">
                  Register
                </Link>
              </>
            )}
          </nav>
        </div>
      </header>
      <main className="flex-1 mx-auto w-full max-w-6xl px-4 py-10">
        <Outlet />
      </main>
      <footer className="text-center text-xs text-slate-500 py-4">
        ClaimIQ demo platform. Synthetic data only.
      </footer>
    </div>
  );
}
