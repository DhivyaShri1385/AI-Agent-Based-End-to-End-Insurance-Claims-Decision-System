import { render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

import type { AuthContextValue } from "../context/AuthContext";
import { useAuth } from "../hooks/useAuth";
import type { User, UserRole } from "../types/auth";
import ProtectedRoute from "./ProtectedRoute";

vi.mock("../hooks/useAuth");
const mockedUseAuth = vi.mocked(useAuth);

function authValue(role: UserRole | null): AuthContextValue {
  const user: User | null = role
    ? {
        id: "u1",
        email: "x@example.com",
        full_name: "Test User",
        role,
        is_active: true,
        created_at: new Date().toISOString(),
      }
    : null;
  return { user, loading: false, login: vi.fn(), register: vi.fn(), logout: vi.fn() };
}

function renderAt(path: string) {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <Routes>
        <Route path="/login" element={<div>Login page</div>} />
        <Route path="/dashboard" element={<div>Dashboard page</div>} />
        <Route element={<ProtectedRoute roles={["ADMIN"]} />}>
          <Route path="/secret" element={<div>Admin secret</div>} />
        </Route>
      </Routes>
    </MemoryRouter>,
  );
}

describe("ProtectedRoute", () => {
  beforeEach(() => mockedUseAuth.mockReset());

  it("redirects anonymous visitors to the login page", () => {
    mockedUseAuth.mockReturnValue(authValue(null));
    renderAt("/secret");
    expect(screen.getByText("Login page")).toBeInTheDocument();
  });

  it("redirects users without the required role to the dashboard", () => {
    mockedUseAuth.mockReturnValue(authValue("POLICYHOLDER"));
    renderAt("/secret");
    expect(screen.getByText("Dashboard page")).toBeInTheDocument();
  });

  it("renders the page for an allowed role", () => {
    mockedUseAuth.mockReturnValue(authValue("ADMIN"));
    renderAt("/secret");
    expect(screen.getByText("Admin secret")).toBeInTheDocument();
  });
});
