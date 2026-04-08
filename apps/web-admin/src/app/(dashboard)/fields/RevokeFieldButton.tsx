"use client";
import { useRouter } from "next/navigation";
import { useState } from "react";

export default function RevokeFieldButton({ fieldId, fieldName }: { fieldId: string; fieldName: string }) {
  const router = useRouter();
  const [loading, setLoading] = useState(false);

  async function revoke() {
    if (!confirm(`Revoke field "${fieldName}"? This cannot be undone.`)) return;
    setLoading(true);
    await fetch(`/api/admin/fields/${fieldId}`, { method: "DELETE" });
    setLoading(false);
    router.refresh();
  }

  return (
    <button onClick={revoke} disabled={loading}
      className="text-xs px-3 py-1 rounded-md border border-red-300 text-red-600 hover:bg-red-50 transition-colors disabled:opacity-50">
      {loading ? "…" : "Revoke"}
    </button>
  );
}
