import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { AxiosError, type AxiosResponse } from "axios";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { AuthProvider } from "../context/AuthContext";
import * as api from "../services/api";
import LoginPage from "./LoginPage";

vi.mock("../services/api", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../services/api")>();
  return { ...actual, login: vi.fn(), getMe: vi.fn() };
});

const mockedLogin = vi.mocked(api.login);

function renderLogin() {
  return render(
    <MemoryRouter initialEntries={["/login"]}>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/dashboard" element={<div>Dashboard reached</div>} />
        </Routes>
      </AuthProvider>
    </MemoryRouter>,
  );
}

describe("LoginPage", () => {
  beforeEach(() => {
    localStorage.clear();
    mockedLogin.mockReset();
  });

  it("requires email and password before calling the API", async () => {
    renderLogin();
    await userEvent.click(screen.getByRole("button", { name: /sign in/i }));

    expect(await screen.findByRole("alert")).toHaveTextContent("Email and password are required.");
    expect(mockedLogin).not.toHaveBeenCalled();
  });

  it("signs in and navigates to the dashboard", async () => {
    mockedLogin.mockResolvedValue({
      access_token: "token-123",
      token_type: "bearer",
      user: {
        id: "u1",
        email: "alice@example.com",
        full_name: "Alice Demo",
        role: "POLICYHOLDER",
        is_active: true,
        created_at: new Date().toISOString(),
      },
    });
    renderLogin();

    await userEvent.type(screen.getByLabelText(/email/i), "alice@example.com");
    await userEvent.type(screen.getByLabelText(/password/i), "Demo@12345");
    await userEvent.click(screen.getByRole("button", { name: /sign in/i }));

    expect(await screen.findByText("Dashboard reached")).toBeInTheDocument();
    expect(mockedLogin).toHaveBeenCalledWith({ email: "alice@example.com", password: "Demo@12345" });
    expect(localStorage.getItem(api.TOKEN_KEY)).toBe("token-123");
  });

  it("shows the server's error message on failure", async () => {
    mockedLogin.mockRejectedValue(
      new AxiosError("Request failed", "ERR_BAD_REQUEST", undefined, undefined, {
        status: 401,
        statusText: "Unauthorized",
        headers: {},
        config: {},
        data: { error: { code: 401, message: "Invalid email or password" } },
      } as unknown as AxiosResponse),
    );
    renderLogin();

    await userEvent.type(screen.getByLabelText(/email/i), "alice@example.com");
    await userEvent.type(screen.getByLabelText(/password/i), "WrongPass1");
    await userEvent.click(screen.getByRole("button", { name: /sign in/i }));

    expect(await screen.findByRole("alert")).toHaveTextContent("Invalid email or password");
  });
});
