import { useEffect, useState } from "react";

import StatusBadge from "../components/StatusBadge";
import { getHealth, type HealthResponse } from "../services/api";

type LoadState =
  | { kind: "loading" }
  | { kind: "loaded"; health: HealthResponse }
  | { kind: "error"; message: string };

export default function SystemStatusPage() {
  const [state, setState] = useState<LoadState>({ kind: "loading" });

  useEffect(() => {
    let cancelled = false;
    getHealth()
      .then((health) => !cancelled && setState({ kind: "loaded", health }))
      .catch(() => !cancelled && setState({ kind: "error", message: "Backend unreachable or unhealthy." }));
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <section>
      <h1 className="text-2xl font-bold">System status</h1>
      <div className="mt-6 rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
        {state.kind === "loading" && <p>Checking backend…</p>}

        {state.kind === "error" && (
          <div>
            <StatusBadge label="Unavailable" tone="danger" />
            <p className="mt-3 text-sm text-slate-600">{state.message}</p>
          </div>
        )}

        {state.kind === "loaded" && (
          <dl className="grid grid-cols-2 gap-y-3 text-sm">
            <dt className="text-slate-500">API</dt>
            <dd>
              <StatusBadge
                label={state.health.status === "ok" ? "Healthy" : "Degraded"}
                tone={state.health.status === "ok" ? "success" : "warning"}
              />
            </dd>
            <dt className="text-slate-500">Database</dt>
            <dd>
              <StatusBadge
                label={state.health.database === "connected" ? "Connected" : "Unavailable"}
                tone={state.health.database === "connected" ? "success" : "danger"}
              />
            </dd>
            <dt className="text-slate-500">Application</dt>
            <dd>
              {state.health.app} v{state.health.version}
            </dd>
            <dt className="text-slate-500">Environment</dt>
            <dd>{state.health.environment}</dd>
          </dl>
        )}
      </div>
    </section>
  );
}
