import { useEffect, useState } from "react";

import StatusBadge from "../components/StatusBadge";
import { useAuth } from "../hooks/useAuth";
import { extractErrorMessage, listPolicies } from "../services/api";
import type { PolicyStatus, PolicySummary } from "../types/policy";

const statusTone: Record<PolicyStatus, "success" | "warning" | "danger"> = {
  ACTIVE: "success",
  SUSPENDED: "warning",
  EXPIRED: "danger",
  CANCELLED: "danger",
};

// Display-only formatting. All money arithmetic happens on the backend with Decimal.
function formatMoney(value: string): string {
  return Number(value).toLocaleString("en-IN", { minimumFractionDigits: 2 });
}

export default function DashboardPage() {
  const { user } = useAuth();
  const [policies, setPolicies] = useState<PolicySummary[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    listPolicies(1, 50)
      .then((result) => {
        if (!cancelled) setPolicies(result.items);
      })
      .catch((err) => {
        if (!cancelled) setError(extractErrorMessage(err, "Could not load policies."));
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const heading = user?.role === "POLICYHOLDER" ? "Your policies" : "All policies";

  return (
    <section>
      <h1 className="text-2xl font-bold">Welcome, {user?.full_name}</h1>
      <p className="mt-1 text-sm text-slate-600">
        Claim submission and tracking arrive in the next stage.
      </p>

      <h2 className="mt-8 text-lg font-semibold">{heading}</h2>
      <div className="mt-3 overflow-x-auto rounded-lg border border-slate-200 bg-white shadow-sm">
        {error && <p className="p-4 text-sm text-danger">{error}</p>}
        {!error && policies === null && <p className="p-4 text-sm">Loading policies…</p>}
        {policies !== null && policies.length === 0 && (
          <p className="p-4 text-sm text-slate-600">No policies found.</p>
        )}
        {policies !== null && policies.length > 0 && (
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 text-slate-500">
              <tr>
                <th className="px-4 py-2 font-medium">Policy</th>
                <th className="px-4 py-2 font-medium">Type</th>
                <th className="px-4 py-2 font-medium">Status</th>
                <th className="px-4 py-2 font-medium">Period</th>
                <th className="px-4 py-2 font-medium text-right">Coverage limit</th>
              </tr>
            </thead>
            <tbody>
              {policies.map((p) => (
                <tr key={p.id} className="border-t border-slate-100">
                  <td className="px-4 py-2 font-medium">{p.policy_number}</td>
                  <td className="px-4 py-2">{p.insurance_type}</td>
                  <td className="px-4 py-2">
                    <StatusBadge label={p.status} tone={statusTone[p.status]} />
                  </td>
                  <td className="px-4 py-2">
                    {p.start_date} to {p.end_date}
                  </td>
                  <td className="px-4 py-2 text-right">{formatMoney(p.coverage_limit)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </section>
  );
}
