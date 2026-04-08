"use client";

import { useEffect, useRef } from "react";
import mapboxgl from "mapbox-gl";
import "mapbox-gl/dist/mapbox-gl.css";
import type { BBoxArray } from "@/lib/bbox";
import { bboxToLngLatBounds } from "@/lib/bbox";

interface Props {
  bbox: BBoxArray;
  sentinelImageUrl: string | null;
}

export default function FieldMap({ bbox, sentinelImageUrl }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<mapboxgl.Map | null>(null);

  // Init map once
  useEffect(() => {
    if (!containerRef.current || mapRef.current) return;
    mapboxgl.accessToken = process.env.NEXT_PUBLIC_MAPBOX_TOKEN!;

    const map = new mapboxgl.Map({
      container: containerRef.current,
      style: "mapbox://styles/mapbox/satellite-streets-v12",
      fitBoundsOptions: { padding: 60 },
    });
    mapRef.current = map;
    map.addControl(new mapboxgl.NavigationControl(), "top-right");

    map.on("load", () => {
      // BBox outline
      map.addSource("field-bbox", {
        type: "geojson",
        data: {
          type: "Feature",
          geometry: {
            type: "Polygon",
            coordinates: [[
              [bbox[0], bbox[1]],
              [bbox[2], bbox[1]],
              [bbox[2], bbox[3]],
              [bbox[0], bbox[3]],
              [bbox[0], bbox[1]],
            ]],
          },
          properties: {},
        },
      });

      map.addLayer({
        id: "field-outline",
        type: "line",
        source: "field-bbox",
        paint: { "line-color": "#22c55e", "line-width": 2 },
      });

      map.addLayer({
        id: "field-fill",
        type: "fill",
        source: "field-bbox",
        paint: { "fill-color": "#22c55e", "fill-opacity": 0.08 },
      });

      // Sentinel image layer (initially empty)
      map.addSource("sentinel-img", {
        type: "image",
        url: "data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7",
        coordinates: [
          [bbox[0], bbox[3]],
          [bbox[2], bbox[3]],
          [bbox[2], bbox[1]],
          [bbox[0], bbox[1]],
        ],
      });
      map.addLayer({ id: "sentinel-layer", type: "raster", source: "sentinel-img", paint: { "raster-opacity": 0.85 } });

      map.fitBounds(bboxToLngLatBounds(bbox), { padding: 60 });
    });

    return () => { map.remove(); mapRef.current = null; };
  }, [bbox]);

  // Update Sentinel overlay when URL changes
  useEffect(() => {
    const map = mapRef.current;
    if (!map || !map.isStyleLoaded()) return;
    const src = map.getSource("sentinel-img") as mapboxgl.ImageSource | undefined;
    if (!src) return;

    if (sentinelImageUrl) {
      src.updateImage({
        url: sentinelImageUrl,
        coordinates: [
          [bbox[0], bbox[3]],
          [bbox[2], bbox[3]],
          [bbox[2], bbox[1]],
          [bbox[0], bbox[1]],
        ],
      });
    }
  }, [sentinelImageUrl, bbox]);

  return <div ref={containerRef} className="w-full h-full" />;
}
