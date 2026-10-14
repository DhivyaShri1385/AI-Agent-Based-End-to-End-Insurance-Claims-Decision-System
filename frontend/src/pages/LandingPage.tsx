import { Link } from "react-router-dom";

export default function LandingPage() {
  return (
    <section className="py-8">
      <h1 className="text-4xl font-bold">Agentic insurance claims automation</h1>
      <p className="mt-4 max-w-2xl text-slate-600">
        ClaimIQ coordinates specialist agents for document understanding, policy
        validation, fraud risk, and payout calculation. Straightforward claims are
        settled automatically; everything uncertain goes to a human adjuster.
      </p>
      <div className="mt-6 flex gap-3">
        <Link
          to="/register"
          className="rounded-md bg-primary px-5 py-2.5 text-white font-medium hover:bg-blue-700"
        >
          Create account
        </Link>
        <Link
          to="/login"
          className="rounded-md border border-slate-300 bg-white px-5 py-2.5 font-medium hover:bg-slate-50"
        >
          Sign in
        </Link>
      </div>
      <p className="mt-6 text-sm text-slate-500">Claim submission is added in the next stage.</p>
    </section>
  );
}
