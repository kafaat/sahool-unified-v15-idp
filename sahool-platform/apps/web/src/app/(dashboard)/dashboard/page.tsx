"use client";

import { useAuthStore } from "@/stores/auth.store";

export default function DashboardPage() {
  const { user } = useAuthStore();

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-800 mb-2">
        Welcome, {user?.name || "..."}
      </h1>
      <p className="text-gray-500 mb-8">You are signed in as <strong>{user?.email}</strong></p>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Card title="Role" value={user?.role || "-"} color="emerald" />
        <Card title="Account Status" value={user?.is_active ? "Active" : "Inactive"} color="blue" />
        <Card title="User ID" value={user?.id?.slice(0, 8) + "..." || "-"} color="purple" />
      </div>
    </div>
  );
}

function Card({ title, value, color }: { title: string; value: string; color: string }) {
  const colors: Record<string, string> = {
    emerald: "border-emerald-400 bg-emerald-50 text-emerald-800",
    blue: "border-blue-400 bg-blue-50 text-blue-800",
    purple: "border-purple-400 bg-purple-50 text-purple-800",
  };
  return (
    <div className={`rounded-xl border-l-4 p-4 ${colors[color] || colors.emerald}`}>
      <p className="text-xs uppercase tracking-wide opacity-70 mb-1">{title}</p>
      <p className="text-lg font-semibold capitalize">{value}</p>
    </div>
  );
}
