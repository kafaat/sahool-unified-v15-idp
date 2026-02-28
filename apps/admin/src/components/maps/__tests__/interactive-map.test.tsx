/**
 * Interactive Map Tests
 * اختبارات الخريطة التفاعلية
 *
 * Tests MapOverview and FarmsMap interactivity, controls, and display.
 */

import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import React from "react";

// Mock next/dynamic to render a FarmsMap-like mock inline
vi.mock("next/dynamic", () => ({
  __esModule: true,
  default: (_loader: () => Promise<{ default: React.ComponentType<any> }>, _opts?: any) => {
    const _React = require("react");
    const DynamicComponent = (props: any) => {
      return _React.createElement(
        "div",
        { "data-testid": "farms-map" },
        props.farms?.map((farm: any) =>
          _React.createElement(
            "div",
            {
              key: farm.id,
              "data-testid": `farm-marker-${farm.id}`,
              onClick: () => props.onFarmClick?.(farm),
            },
            farm.nameAr || farm.name,
          ),
        ),
      );
    };
    DynamicComponent.displayName = "DynamicComponent";
    return DynamicComponent;
  },
}));

// Mock next/link
vi.mock("next/link", () => ({
  __esModule: true,
  default: ({ href, children, ...props }: any) =>
    React.createElement("a", { href, ...props }, children),
}));

// Mock lucide-react icons
vi.mock("lucide-react", () => {
  const _React = require("react");
  const createIcon = (name: string) => {
    const Icon = (props: Record<string, unknown>) =>
      _React.createElement("svg", { "data-testid": `icon-${name}`, ...props });
    Icon.displayName = name;
    return Icon;
  };
  return {
    __esModule: true,
    MapPin: createIcon("MapPin"),
    Layers: createIcon("Layers"),
    Eye: createIcon("Eye"),
    EyeOff: createIcon("EyeOff"),
  };
});

// Mock @/lib/utils
vi.mock("@/lib/utils", () => ({
  cn: (...inputs: string[]) => inputs.filter(Boolean).join(" "),
  getHealthScoreColor: (score: number) => {
    if (score >= 70) return "text-green-600";
    if (score >= 50) return "text-yellow-600";
    return "text-red-600";
  },
}));

import MapOverview, { type MapFarm } from "../../dashboard/MapOverview";

const sampleFarms: MapFarm[] = [
  {
    id: "f1",
    name: "Farm A",
    nameAr: "مزرعة أ",
    coordinates: { lat: 15.55, lng: 48.51 },
    healthScore: 85,
    area: 10,
    crops: ["قمح", "شعير"],
    status: "active",
  },
  {
    id: "f2",
    name: "Farm B",
    nameAr: "مزرعة ب",
    coordinates: { lat: 15.4, lng: 48.3 },
    healthScore: 55,
    area: 8,
    crops: ["طماطم"],
    status: "active",
  },
  {
    id: "f3",
    name: "Farm C",
    nameAr: "مزرعة ج",
    coordinates: { lat: 15.3, lng: 48.2 },
    healthScore: 30,
    area: 15,
    crops: ["نخيل"],
    status: "warning",
  },
];

// ═══════════════════════════════════════════════════════════════════════════
// MapOverview Component Tests | اختبارات مكون نظرة الخريطة
// ═══════════════════════════════════════════════════════════════════════════

describe("MapOverview", () => {
  it("renders map header with Arabic title", () => {
    render(<MapOverview farms={sampleFarms} />);
    expect(screen.getByText("خريطة المزارع")).toBeInTheDocument();
  });

  it("renders MapPin icon", () => {
    render(<MapOverview farms={sampleFarms} />);
    expect(screen.getByTestId("icon-MapPin")).toBeInTheDocument();
  });

  it("shows health statistics bar by default", () => {
    render(<MapOverview farms={sampleFarms} />);
    expect(screen.getByText("صحي:")).toBeInTheDocument();
    expect(screen.getByText("تحذير:")).toBeInTheDocument();
    expect(screen.getByText("حرج:")).toBeInTheDocument();
  });

  it("calculates health categories correctly", () => {
    render(<MapOverview farms={sampleFarms} />);
    // f1 (85) = healthy, f2 (55) = warning, f3 (30) = critical
    // Each category has count 1, total farms = 3
    const allOnes = screen.getAllByText("1");
    expect(allOnes.length).toBeGreaterThanOrEqual(3); // healthy, warning, critical
    expect(screen.getByText("3")).toBeInTheDocument(); // total farms
  });

  it("shows total farms count", () => {
    render(<MapOverview farms={sampleFarms} />);
    expect(screen.getByText((content) => content.includes("3"))).toBeInTheDocument();
  });

  it("toggles health overlay on button click", () => {
    render(<MapOverview farms={sampleFarms} showControls={true} />);
    const overlayButton = screen.getByTitle("إخفاء طبقة الصحة");
    fireEvent.click(overlayButton);

    // After toggle, title should change
    expect(screen.getByTitle("عرض طبقة الصحة")).toBeInTheDocument();
  });

  it("hides health stats when overlay is disabled", () => {
    render(<MapOverview farms={sampleFarms} showHealthOverlay={false} />);
    expect(screen.queryByText("صحي:")).not.toBeInTheDocument();
  });

  it("shows map view selector", () => {
    render(<MapOverview farms={sampleFarms} showControls={true} />);
    const selector = screen.getByDisplayValue("خريطة عادية");
    expect(selector).toBeInTheDocument();
  });

  it("changes map view option", () => {
    render(<MapOverview farms={sampleFarms} showControls={true} />);
    const selector = screen.getByDisplayValue("خريطة عادية");
    fireEvent.change(selector, { target: { value: "satellite" } });
    expect(screen.getByDisplayValue("صور الأقمار")).toBeInTheDocument();
  });

  it("renders 'view all' link to farms page", () => {
    render(<MapOverview farms={sampleFarms} showControls={true} />);
    expect(screen.getByText("عرض الكل ←")).toBeInTheDocument();
    expect(
      screen.getByText("عرض الكل ←").closest("a"),
    ).toHaveAttribute("href", "/farms");
  });

  it("hides controls when showControls is false", () => {
    render(<MapOverview farms={sampleFarms} showControls={false} />);
    expect(screen.queryByTitle("إخفاء طبقة الصحة")).not.toBeInTheDocument();
    expect(screen.queryByText("عرض الكل ←")).not.toBeInTheDocument();
  });

  it("calls onFarmClick when farm marker is clicked", () => {
    const onFarmClick = vi.fn();
    render(<MapOverview farms={sampleFarms} onFarmClick={onFarmClick} />);

    const farmMarker = screen.getByTestId("farm-marker-f1");
    fireEvent.click(farmMarker);

    expect(onFarmClick).toHaveBeenCalledWith(
      expect.objectContaining({ id: "f1", nameAr: "مزرعة أ" }),
    );
  });

  it("shows legend when overlay is enabled", () => {
    render(<MapOverview farms={sampleFarms} />);
    expect(screen.getByText(/الألوان تمثل مستوى صحة المحصول/)).toBeInTheDocument();
    expect(screen.getByText("أخضر (70-100)")).toBeInTheDocument();
    expect(screen.getByText("أصفر (50-69)")).toBeInTheDocument();
  });

  it("renders with empty farms array", () => {
    render(<MapOverview farms={[]} />);
    expect(screen.getByText("خريطة المزارع")).toBeInTheDocument();
  });

  it("passes selectedFarmId to map", () => {
    render(<MapOverview farms={sampleFarms} selectedFarmId="f2" />);
    // Map should still render
    expect(screen.getByTestId("farms-map")).toBeInTheDocument();
  });

  it("accepts custom className", () => {
    const { container } = render(
      <MapOverview farms={sampleFarms} className="custom-class" />,
    );
    expect(container.firstChild).toHaveClass("custom-class");
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// FarmsMap Source Verification | التحقق من مصدر خريطة المزارع
// ═══════════════════════════════════════════════════════════════════════════

describe("FarmsMap Source Verification", () => {
  const fs = require("fs");
  const path = require("path");
  const farmsMapPath = path.resolve(
    __dirname,
    "../../maps/FarmsMap.tsx",
  );

  it("FarmsMap file exists", () => {
    expect(fs.existsSync(farmsMapPath)).toBe(true);
  });

  it("uses Yemen center coordinates", () => {
    const content = fs.readFileSync(farmsMapPath, "utf-8");
    expect(content).toContain("15.5527");
    expect(content).toContain("48.5164");
  });

  it("supports polygon boundaries for fields", () => {
    const content = fs.readFileSync(farmsMapPath, "utf-8");
    expect(content).toContain("Polygon");
    expect(content).toContain("boundary");
  });

  it("supports circle markers as fallback", () => {
    const content = fs.readFileSync(farmsMapPath, "utf-8");
    expect(content).toContain("CircleMarker");
  });

  it("has satellite imagery tile layer", () => {
    const content = fs.readFileSync(farmsMapPath, "utf-8");
    expect(content).toContain("صور الأقمار الصناعية");
    expect(content).toContain("arcgisonline");
  });

  it("has terrain tile layer", () => {
    const content = fs.readFileSync(farmsMapPath, "utf-8");
    expect(content).toContain("التضاريس");
    expect(content).toContain("opentopomap");
  });

  it("renders popup with farm details in Arabic", () => {
    const content = fs.readFileSync(farmsMapPath, "utf-8");
    expect(content).toContain("المحافظة");
    expect(content).toContain("المساحة");
    expect(content).toContain("المحاصيل");
    expect(content).toContain("مستوى الصحة");
  });

  it("has click handler for farm selection", () => {
    const content = fs.readFileSync(farmsMapPath, "utf-8");
    expect(content).toContain("onFarmClick");
    expect(content).toContain("eventHandlers");
  });

  it("shows health score color-coded legend", () => {
    const content = fs.readFileSync(farmsMapPath, "utf-8");
    expect(content).toContain("ممتاز");
    expect(content).toContain("جيد");
    expect(content).toContain("متوسط");
    expect(content).toContain("ضعيف");
  });

  it("supports scrollWheelZoom for interactivity", () => {
    const content = fs.readFileSync(farmsMapPath, "utf-8");
    expect(content).toContain("scrollWheelZoom={true}");
  });

  it("has farm count badge overlay", () => {
    const content = fs.readFileSync(farmsMapPath, "utf-8");
    expect(content).toContain("مزرعة");
    expect(content).toContain("farms.length");
  });
});
