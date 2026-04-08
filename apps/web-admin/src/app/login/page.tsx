"use client";
import { useState } from "react";
import { signIn } from "next-auth/react";
import { useRouter } from "next/navigation";

export default function AdminLoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(""); setLoading(true);
    const res = await signIn("credentials", { email, password, redirect: false });
    setLoading(false);
    if (res?.error) setError("Invalid credentials or insufficient permissions.");
    else router.push("/");
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-muted/30">
      <div className="w-full max-w-sm bg-card border rounded-xl shadow-sm p-8 space-y-6">
        <div className="text-center space-y-1">
          <h1 className="text-2xl font-bold">Admin Panel</h1>
          <p className="text-sm text-muted-foreground">Administrator access only</p>
        </div>
        {error && <div className="bg-destructive/10 text-destructive text-sm px-4 py-3 rounded-lg">{error}</div>}
        <form onSubmit={handleSubmit} className="space-y-4">
          {["email", "password"].map((f) => (
            <div key={f} className="space-y-1">
              <label className="text-sm font-medium capitalize" htmlFor={f}>{f}</label>
              <input id={f} type={f} required
                value={f === "email" ? email : password}
                onChange={(e) => f === "email" ? setEmail(e.target.value) : setPassword(e.target.value)}
                className="w-full px-3 py-2 border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-ring"
              />
            </div>
          ))}
          <button type="submit" disabled={loading}
            className="w-full bg-primary text-primary-foreground py-2 rounded-md text-sm font-medium hover:bg-primary/90 disabled:opacity-50 transition-colors">
            {loading ? "Signing in…" : "Sign in"}
          </button>
        </form>
      </div>
    </div>
  );
}
