"use client";

import { useEffect, useRef } from "react";
import mapboxgl from "mapbox-gl";
import MapboxDraw from "@mapbox/mapbox-gl-draw";
import * as turf from "@turf/turf";
import "mapbox-gl/dist/mapbox-gl.css";
import "@mapbox/mapbox-gl-draw/dist/mapbox-gl-draw.css";
import type { BBoxArray } from "@/lib/bbox";

interface Props {
  onBBoxChange: (bbox: BBoxArray | null) => void;
}

export default function BBoxMapPicker({ onBBoxChange }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<mapboxgl.Map | null>(null);
  const drawRef = useRef<MapboxDraw | null>(null);

  useEffect(() => {
    if (!containerRef.current || mapRef.current) return;

    mapboxgl.accessToken = process.env.NEXT_PUBLIC_MAPBOX_TOKEN!;

    const map = new mapboxgl.Map({
      container: containerRef.current,
      style: "mapbox://styles/mapbox/satellite-streets-v12",
      center: [45, 25], // Middle East default
      zoom: 4,
    });
    mapRef.current = map;

    const draw = new MapboxDraw({
      displayControlsDefault: false,
      controls: { trash: true },
      // Custom rectangle mode — draw a rectangle by clicking two corners
      defaultMode: "draw_rectangle" as MapboxDraw.DrawMode,
    });
    drawRef.current = draw;
    map.addControl(draw);
    map.addControl(new mapboxgl.NavigationControl(), "top-right");

    // Handle completed rectangle
    const onDrawCreate = () => {
      const data = draw.getAll();
      if (data.features.length > 0) {
        const bbox = turf.bbox(data.features[0]) as BBoxArray;
        onBBoxChange(bbox);
        // Allow only one rectangle at a time
        const ids = data.features.slice(1).map((f) => f.id as string);
        if (ids.length) draw.delete(ids);
      }
    };

    const onDrawDelete = () => {
      if (draw.getAll().features.length === 0) onBBoxChange(null);
    };

    map.on("draw.create", onDrawCreate);
    map.on("draw.update", onDrawCreate);
    map.on("draw.delete", onDrawDelete);

    return () => {
      map.remove();
      mapRef.current = null;
    };
  }, [onBBoxChange]);

  return (
    <div className="space-y-2">
      <p className="text-xs text-muted-foreground">
        Use the rectangle tool (top-left of map) to draw your field boundary.
      </p>
      <div ref={containerRef} className="h-[420px] rounded-xl overflow-hidden border" />
    </div>
  );
}
