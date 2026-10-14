import { useState, type FormEvent } from "react";
import { Link, Navigate } from "react-router-dom";

import FormField from "../components/FormField";
import { useAuth } from "../hooks/useAuth";
import { extractErrorMessage } from "../services/api";

export default function RegisterPage() {
  const { user, register } = useAuth();

  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  if (user) {
    return <Navigate to="/dashboard" replace />;
  }

  // Mirrors the backend rules; the backend remains authoritative.
  function validate(): string | null {
    if (fullName.trim().length < 2) return "Please enter your full name.";
    if (!email.trim()) return "Email is required.";
    if (password.length < 8) return "Password must be at least 8 characters.";
    if (!/[A-Za-z]/.test(password) || !/\d/.test(password)) {
      return "Password must contain at least one letter and one digit.";
    }
    if (password !== confirm) return "Passwords do not match.";
    return null;
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    const problem = validate();
    if (problem) {
      setError(problem);
      return;
    }
    setError(null);
    setSubmitting(true);
    try {
      await register(fullName.trim(), email.trim(), password);
    } catch (err) {
      setError(extractErrorMessage(err, "Registration failed. Please try again."));
      setSubmitting(false);
    }
  }

  return (
    <div className="mx-auto max-w-md rounded-lg border border-slate-200 bg-white p-8 shadow-sm">
      <h1 className="text-2xl font-bold">Create your account</h1>
      <form onSubmit={handleSubmit} noValidate className="mt-6 space-y-4">
        <FormField id="full_name" label="Full name" autoComplete="name" value={fullName} onChange={(e) => setFullName(e.target.value)} />
        <FormField id="email" label="Email" type="email" autoComplete="email" value={email} onChange={(e) => setEmail(e.target.value)} />
        <FormField id="password" label="Password" type="password" autoComplete="new-password" value={password} onChange={(e) => setPassword(e.target.value)} />
        <FormField id="confirm" label="Confirm password" type="password" autoComplete="new-password" value={confirm} onChange={(e) => setConfirm(e.target.value)} />
        {error && (
          <p role="alert" className="rounded-md bg-red-50 px-3 py-2 text-sm text-danger">
            {error}
          </p>
        )}
        <button
          type="submit"
          disabled={submitting}
          className="w-full rounded-md bg-primary px-4 py-2.5 font-medium text-white hover:bg-blue-700 disabled:opacity-60"
        >
          {submitting ? "Creating account…" : "Create account"}
        </button>
      </form>
      <p className="mt-4 text-sm text-slate-600">
        Already registered?{" "}
        <Link to="/login" className="text-primary hover:underline">
          Sign in
        </Link>
      </p>
    </div>
  );
}
