"use client";
import { useRouter } from "next/navigation";
import { useState } from "react";

export default function UserActions({ userId, status }: { userId: string; status: string }) {
  const router = useRouter();
  const [loading, setLoading] = useState(false);

  async function toggle() {
    setLoading(true);
    await fetch(`/api/admin/users/${userId}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status: status === "active" ? "suspended" : "active" }),
    });
    setLoading(false);
    router.refresh();
  }

  return (
    <button onClick={toggle} disabled={loading}
      className={`text-xs px-3 py-1 rounded-md border transition-colors disabled:opacity-50 ${
        status === "active"
          ? "border-red-300 text-red-600 hover:bg-red-50"
          : "border-green-300 text-green-600 hover:bg-green-50"
      }`}>
      {loading ? "…" : status === "active" ? "Suspend" : "Activate"}
    </button>
  );
}
