import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import * as api from "../services/api";
import SystemStatusPage from "./SystemStatusPage";

vi.mock("../services/api", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../services/api")>();
  return { ...actual, getHealth: vi.fn() };
});

const mockedGetHealth = vi.mocked(api.getHealth);

describe("SystemStatusPage", () => {
  beforeEach(() => {
    mockedGetHealth.mockReset();
  });

  it("shows healthy state when backend responds ok", async () => {
    mockedGetHealth.mockResolvedValue({
      status: "ok",
      app: "ClaimIQ",
      version: "0.1.0",
      environment: "development",
      database: "connected",
      timestamp: new Date().toISOString(),
    });

    render(<SystemStatusPage />);

    expect(await screen.findByText("Healthy")).toBeInTheDocument();
    expect(screen.getByText("Connected")).toBeInTheDocument();
  });

  it("shows error state when backend is unreachable", async () => {
    mockedGetHealth.mockRejectedValue(new Error("network"));

    render(<SystemStatusPage />);

    expect(await screen.findByText("Unavailable")).toBeInTheDocument();
    expect(screen.getByText(/Backend unreachable/i)).toBeInTheDocument();
  });
});
