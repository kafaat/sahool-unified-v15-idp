"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import dynamic from "next/dynamic";
import type { BBoxArray } from "@/lib/bbox";

// Dynamically import the map to avoid SSR (Mapbox uses browser APIs)
const BBoxMapPicker = dynamic(() => import("@/components/BBoxMapPicker"), {
  ssr: false,
  loading: () => (
    <div className="h-[400px] rounded-xl bg-muted animate-pulse flex items-center justify-center text-muted-foreground text-sm">
      Loading map…
    </div>
  ),
});

export default function NewFieldPage() {
  const router = useRouter();
  const [bbox, setBBox] = useState<BBoxArray | null>(null);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!bbox) { setError("Please draw a field boundary on the map."); return; }
    setError("");
    setLoading(true);

    const res = await fetch("/api/fields", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, description, bbox }),
    });

    setLoading(false);

    if (res.ok) {
      const field = await res.json();
      router.push(`/fields/${field.id}`);
    } else {
      const data = await res.json();
      setError(data.error ?? "Failed to create field");
    }
  }

  return (
    <div className="max-w-2xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold">New field</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Draw a rectangle on the map to define your field boundary.
        </p>
      </div>

      {error && (
        <div className="bg-destructive/10 text-destructive text-sm px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      {/* Map step */}
      <BBoxMapPicker onBBoxChange={setBBox} />

      {bbox && (
        <div className="bg-muted/50 rounded-lg px-4 py-3 text-sm font-mono text-muted-foreground">
          BBox: [{bbox.map((v) => v.toFixed(5)).join(", ")}]
        </div>
      )}

      {/* Form */}
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="space-y-1">
          <label className="text-sm font-medium" htmlFor="name">Field name</label>
          <input
            id="name"
            required
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="e.g. North wheat field"
            className="w-full px-3 py-2 border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-ring"
          />
        </div>

        <div className="space-y-1">
          <label className="text-sm font-medium" htmlFor="description">
            Description <span className="text-muted-foreground font-normal">(optional)</span>
          </label>
          <textarea
            id="description"
            rows={2}
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Crop type, notes…"
            className="w-full px-3 py-2 border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-ring resize-none"
          />
        </div>

        <div className="flex gap-3">
          <button
            type="submit"
            disabled={loading || !bbox}
            className="bg-primary text-primary-foreground px-6 py-2 rounded-md text-sm font-medium hover:bg-primary/90 disabled:opacity-50 transition-colors"
          >
            {loading ? "Creating…" : "Create field"}
          </button>
          <button
            type="button"
            onClick={() => router.back()}
            className="px-6 py-2 rounded-md text-sm border hover:bg-muted transition-colors"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}
