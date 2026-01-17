/**
 * Scouting Types Unit Tests
 * اختبارات وحدة أنواع الكشافة الحقلية
 *
 * Tests for field scouting type definitions and data validation
 */

import { describe, it, expect } from "vitest";
import type {
  ObservationCategory,
  Severity,
  SessionStatus,
  AnnotationType,
  PhotoAnnotation,
  AnnotatedPhoto,
  Observation,
} from "../types/scouting";

describe("Scouting Types", () => {
  describe("ObservationCategory", () => {
    it("should accept all valid observation categories", () => {
      const categories: ObservationCategory[] = [
        "pest",
        "disease",
        "weed",
        "nutrient",
        "water",
        "other",
      ];

      expect(categories).toHaveLength(6);
      expect(categories).toContain("pest");
      expect(categories).toContain("disease");
      expect(categories).toContain("weed");
    });
  });

  describe("Severity", () => {
    it("should accept severity values 1-5", () => {
      const validSeverities: Severity[] = [1, 2, 3, 4, 5];

      validSeverities.forEach((severity) => {
        expect(severity).toBeGreaterThanOrEqual(1);
        expect(severity).toBeLessThanOrEqual(5);
      });
    });

    it("should represent increasing severity", () => {
      const low: Severity = 1;
      const critical: Severity = 5;

      expect(critical).toBeGreaterThan(low);
    });
  });

  describe("SessionStatus", () => {
    it("should have all session status values", () => {
      const statuses: SessionStatus[] = ["active", "completed", "cancelled"];

      expect(statuses).toHaveLength(3);
      expect(statuses).toContain("active");
      expect(statuses).toContain("completed");
    });
  });

  describe("AnnotationType", () => {
    it("should support all annotation types", () => {
      const types: AnnotationType[] = ["circle", "arrow", "text", "rectangle"];

      expect(types).toHaveLength(4);
      expect(types).toContain("circle");
      expect(types).toContain("arrow");
    });
  });

  describe("PhotoAnnotation Interface", () => {
    it("should create valid circle annotation", () => {
      const circleAnnotation: PhotoAnnotation = {
        id: "ann-001",
        type: "circle",
        color: "#FF0000",
        x: 0.5,
        y: 0.5,
        width: 0.1,
        height: 0.1,
        createdAt: "2026-01-06T10:00:00Z",
      };

      expect(circleAnnotation.type).toBe("circle");
      expect(circleAnnotation.x).toBeGreaterThanOrEqual(0);
      expect(circleAnnotation.x).toBeLessThanOrEqual(1);
    });

    it("should create valid arrow annotation", () => {
      const arrowAnnotation: PhotoAnnotation = {
        id: "ann-002",
        type: "arrow",
        color: "#00FF00",
        x: 0,
        y: 0,
        startX: 0.2,
        startY: 0.2,
        endX: 0.8,
        endY: 0.8,
        createdAt: "2026-01-06T10:00:00Z",
      };

      expect(arrowAnnotation.type).toBe("arrow");
      expect(arrowAnnotation.startX).toBeDefined();
      expect(arrowAnnotation.endX).toBeDefined();
    });

    it("should create valid text annotation", () => {
      const textAnnotation: PhotoAnnotation = {
        id: "ann-003",
        type: "text",
        color: "#0000FF",
        x: 0.3,
        y: 0.3,
        text: "Pest detected here",
        fontSize: 14,
        createdAt: "2026-01-06T10:00:00Z",
      };

      expect(textAnnotation.type).toBe("text");
      expect(textAnnotation.text).toBeDefined();
    });
  });

  describe("AnnotatedPhoto Interface", () => {
    it("should create photo with annotations", () => {
      const photo: AnnotatedPhoto = {
        id: "photo-001",
        url: "https://storage.example.com/photos/field-1.jpg",
        thumbnailUrl: "https://storage.example.com/photos/field-1-thumb.jpg",
        annotations: [
          {
            id: "ann-001",
            type: "circle",
            color: "#FF0000",
            x: 0.5,
            y: 0.5,
            createdAt: "2026-01-06T10:00:00Z",
          },
        ],
        uploadedAt: "2026-01-06T09:00:00Z",
        fileSize: 1024000,
        mimeType: "image/jpeg",
      };

      expect(photo.annotations).toHaveLength(1);
      expect(photo.url).toContain("https://");
    });
  });

  describe("Observation Interface", () => {
    it("should create valid observation", () => {
      const observation: Observation = {
        id: "obs-001",
        sessionId: "session-001",
        fieldId: "field-001",
        location: {
          lat: 15.3694,
          lng: 44.191,
        },
        locationName: "North corner",
        locationNameAr: "الزاوية الشمالية",
        category: "pest",
        subcategory: "aphid",
        subcategoryAr: "من",
        severity: 3,
        notes: "Found aphid infestation on lower leaves",
        notesAr: "وجدت إصابة بالمن على الأوراق السفلية",
        photos: [],
      };

      expect(observation.category).toBe("pest");
      expect(observation.severity).toBe(3);
      expect(observation.location.lat).toBeGreaterThan(0);
    });

    it("should support high severity observations", () => {
      const criticalObservation: Observation = {
        id: "obs-002",
        sessionId: "session-001",
        fieldId: "field-001",
        location: { lat: 15.37, lng: 44.19 },
        category: "disease",
        severity: 5,
        notes: "Severe fungal infection spreading",
        photos: [],
      };

      expect(criticalObservation.severity).toBe(5);
      expect(criticalObservation.category).toBe("disease");
    });
  });
});

describe("Scouting Data Validation", () => {
  it("should validate location coordinates", () => {
    const validLat = 15.3694;
    const validLng = 44.191;

    expect(validLat).toBeGreaterThanOrEqual(-90);
    expect(validLat).toBeLessThanOrEqual(90);
    expect(validLng).toBeGreaterThanOrEqual(-180);
    expect(validLng).toBeLessThanOrEqual(180);
  });

  it("should validate annotation positions are relative (0-1)", () => {
    const annotation: PhotoAnnotation = {
      id: "test",
      type: "circle",
      color: "#FF0000",
      x: 0.5,
      y: 0.75,
      createdAt: new Date().toISOString(),
    };

    expect(annotation.x).toBeGreaterThanOrEqual(0);
    expect(annotation.x).toBeLessThanOrEqual(1);
    expect(annotation.y).toBeGreaterThanOrEqual(0);
    expect(annotation.y).toBeLessThanOrEqual(1);
  });

  it("should map category to Arabic names", () => {
    const categoryLabels: Record<
      ObservationCategory,
      { en: string; ar: string }
    > = {
      pest: { en: "Pest", ar: "حشرات" },
      disease: { en: "Disease", ar: "أمراض" },
      weed: { en: "Weed", ar: "أعشاب ضارة" },
      nutrient: { en: "Nutrient Deficiency", ar: "نقص غذائي" },
      water: { en: "Water Stress", ar: "إجهاد مائي" },
      other: { en: "Other", ar: "أخرى" },
    };

    expect(categoryLabels.pest.ar).toBe("حشرات");
    expect(categoryLabels.disease.ar).toBe("أمراض");
  });

  it("should map severity to descriptions", () => {
    const severityLabels: Record<Severity, { en: string; ar: string }> = {
      1: { en: "Very Low", ar: "منخفض جداً" },
      2: { en: "Low", ar: "منخفض" },
      3: { en: "Moderate", ar: "متوسط" },
      4: { en: "High", ar: "مرتفع" },
      5: { en: "Critical", ar: "حرج" },
    };

    expect(severityLabels[5].ar).toBe("حرج");
    expect(severityLabels[1].en).toBe("Very Low");
  });
});
