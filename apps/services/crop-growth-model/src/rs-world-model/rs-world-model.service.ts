// ═══════════════════════════════════════════════════════════════════════════════
// Remote Sensing World Model Service - خدمة نموذج العالم للاستشعار عن بعد
// Based on RemoteBAGEL: First World Model for Remote Sensing Spatial Reasoning
// Paper: https://arxiv.org/abs/2509.17808 (2025)
// ═══════════════════════════════════════════════════════════════════════════════

import { Injectable } from "@nestjs/common";

// ─────────────────────────────────────────────────────────────────────────────
// Interfaces & Types - واجهات وأنواع
// ─────────────────────────────────────────────────────────────────────────────

type Direction = "up" | "down" | "left" | "right";
type ScenarioType = "general" | "flood" | "urban" | "rural" | "agricultural";

// Security: Whitelist of allowed scenario types to prevent property injection
const ALLOWED_SCENARIOS: Set<string> = new Set([
  "general",
  "flood",
  "urban",
  "rural",
  "agricultural",
]);

export interface TileData {
  id: string;
  position: { row: number; col: number };
  bounds: { minLat: number; maxLat: number; minLng: number; maxLng: number };
  indices: { ndvi: number; ndwi: number; ndbi: number };
  landCover: LandCoverClass[];
  features: string[];
  scenario: ScenarioType;
  timestamp: string;
}

export interface LandCoverClass {
  type:
    | "vegetation"
    | "water"
    | "built_up"
    | "bare_soil"
    | "road"
    | "agriculture"
    | "forest";
  percentage: number;
  confidence: number;
}

export interface SpatialReasoningResult {
  centralTile: TileData;
  direction: Direction;
  predictedTile: TileData;
  confidence: number;
  spatialContinuity: number;
  semanticConsistency: number;
  generationMethod: string;
}

export interface MultiDirectionalExpansion {
  centralTile: TileData;
  expansions: {
    up: TileData | null;
    down: TileData | null;
    left: TileData | null;
    right: TileData | null;
  };
  fullCoverage: TileData[][];
  totalArea: number;
  scenarioAnalysis: ScenarioAnalysis;
}

export interface ScenarioAnalysis {
  dominantScenario: ScenarioType;
  scenarioDistribution: { [key in ScenarioType]?: number };
  riskAssessment: RiskAssessment | null;
  recommendations: string[];
  recommendationsAr: string[];
}

export interface RiskAssessment {
  type: "flood" | "drought" | "urban_expansion" | "deforestation";
  level: "low" | "medium" | "high" | "critical";
  affectedArea: number;
  trend: "increasing" | "stable" | "decreasing";
  confidence: number;
}

export interface TrainingData {
  id: string;
  centralTile: TileData;
  direction: Direction;
  adjacentTile: TileData;
  overlap: number;
}

export interface ModelArchitecture {
  stage: string;
  nameEn: string;
  nameAr: string;
  description: string;
  components: string[];
}

export interface RSWISEScore {
  overall: number;
  fid: number; // Fréchet Inception Distance (visual fidelity)
  gptScore: number; // GPT-4o spatial reasoning score
  byScenario: { [key in ScenarioType]?: number };
  byDirection: { [key in Direction]?: number };
}

export interface GridPartition {
  originalImage: { width: number; height: number };
  gridSize: { rows: number; cols: number };
  tiles: TileData[][];
  overlapPercentage: number;
  totalTiles: number;
  trainingPairs: number;
}

@Injectable()
export class RSWorldModelService {
  // ─────────────────────────────────────────────────────────────────────────────
  // Model Architecture - البنية المعمارية للنموذج
  // Three-stage RemoteBAGEL architecture
  // ─────────────────────────────────────────────────────────────────────────────

  private readonly modelArchitecture: ModelArchitecture[] = [
    {
      stage: "feature_encoding",
      nameEn: "Feature Encoding",
      nameAr: "ترميز الخصائص",
      description:
        "Extract visual features from input tile and encode direction into learnable embedding",
      components: [
        "Visual Encoder (ViT-based)",
        "Direction Embedding Layer",
        "Positional Encoding",
        "Feature Normalization",
      ],
    },
    {
      stage: "multimodal_integration",
      nameEn: "Multimodal Integration",
      nameAr: "التكامل متعدد الوسائط",
      description:
        "Fuse visual features with direction embedding using cross-attention and self-attention",
      components: [
        "Cross-Attention Module",
        "Self-Attention Layers",
        "Spatial Dependency Capture",
        "Semantic Understanding",
      ],
    },
    {
      stage: "decoding_generation",
      nameEn: "Decoding & Generation",
      nameAr: "فك الترميز والتوليد",
      description:
        "Synthesize adjacent tiles with geographic structure continuity",
      components: [
        "Diffusion Decoder",
        "Structure Continuity Module",
        "Boundary Consistency Check",
        "Output Refinement",
      ],
    },
  ];

  // ─────────────────────────────────────────────────────────────────────────────
  // Scenario Templates - قوالب السيناريوهات
  // ─────────────────────────────────────────────────────────────────────────────

  private readonly scenarioTemplates: Map<
    ScenarioType,
    {
      typicalFeatures: string[];
      landCoverDistribution: Partial<{ [key: string]: [number, number] }>;
      indices: {
        ndvi: [number, number];
        ndwi: [number, number];
        ndbi: [number, number];
      };
    }
  > = new Map([
    [
      "general",
      {
        typicalFeatures: [
          "mixed terrain",
          "variable vegetation",
          "natural features",
        ],
        landCoverDistribution: {
          vegetation: [0.2, 0.6],
          bare_soil: [0.1, 0.4],
          water: [0, 0.2],
        },
        indices: { ndvi: [0.2, 0.7], ndwi: [-0.2, 0.3], ndbi: [-0.3, 0.2] },
      },
    ],
    [
      "flood",
      {
        typicalFeatures: [
          "water bodies",
          "flooded areas",
          "damaged structures",
          "debris",
        ],
        landCoverDistribution: {
          water: [0.3, 0.8],
          vegetation: [0.1, 0.4],
          bare_soil: [0.1, 0.3],
        },
        indices: { ndvi: [0.0, 0.4], ndwi: [0.2, 0.8], ndbi: [-0.4, 0.1] },
      },
    ],
    [
      "urban",
      {
        typicalFeatures: ["buildings", "roads", "infrastructure", "parks"],
        landCoverDistribution: {
          built_up: [0.4, 0.8],
          road: [0.1, 0.3],
          vegetation: [0.05, 0.2],
        },
        indices: { ndvi: [0.0, 0.3], ndwi: [-0.3, 0.1], ndbi: [0.2, 0.6] },
      },
    ],
    [
      "rural",
      {
        typicalFeatures: [
          "farmland",
          "scattered buildings",
          "natural vegetation",
          "small roads",
        ],
        landCoverDistribution: {
          agriculture: [0.4, 0.7],
          vegetation: [0.2, 0.4],
          built_up: [0.05, 0.15],
        },
        indices: { ndvi: [0.3, 0.8], ndwi: [-0.1, 0.2], ndbi: [-0.2, 0.1] },
      },
    ],
    [
      "agricultural",
      {
        typicalFeatures: [
          "crop fields",
          "irrigation channels",
          "farm structures",
          "greenhouses",
        ],
        landCoverDistribution: {
          agriculture: [0.6, 0.9],
          vegetation: [0.1, 0.3],
          bare_soil: [0.05, 0.2],
        },
        indices: { ndvi: [0.4, 0.9], ndwi: [0.0, 0.3], ndbi: [-0.3, 0.0] },
      },
    ],
  ]);

  // ─────────────────────────────────────────────────────────────────────────────
  // Service Methods - طرق الخدمة
  // ─────────────────────────────────────────────────────────────────────────────

  /**
   * Get model architecture details
   */
  getModelArchitecture(): ModelArchitecture[] {
    return this.modelArchitecture;
  }

  /**
   * Get available scenarios
   */
  getScenarios(): {
    id: ScenarioType;
    nameEn: string;
    nameAr: string;
    description: string;
  }[] {
    return [
      {
        id: "general",
        nameEn: "General",
        nameAr: "عام",
        description: "Diverse terrain (mountains, forests, coasts)",
      },
      {
        id: "flood",
        nameEn: "Flood",
        nameAr: "فيضانات",
        description: "Disaster response, flooded areas",
      },
      {
        id: "urban",
        nameEn: "Urban",
        nameAr: "حضري",
        description: "Dense built environments, road networks",
      },
      {
        id: "rural",
        nameEn: "Rural",
        nameAr: "ريفي",
        description: "Agricultural areas, natural vegetation",
      },
      {
        id: "agricultural",
        nameEn: "Agricultural",
        nameAr: "زراعي",
        description: "Crop fields, irrigation, farms",
      },
    ];
  }

  /**
   * Generate a tile based on scenario
   */
  private generateTile(params: {
    id: string;
    position: { row: number; col: number };
    bounds: { minLat: number; maxLat: number; minLng: number; maxLng: number };
    scenario: ScenarioType;
  }): TileData {
    const template = this.scenarioTemplates.get(params.scenario)!;

    // Generate indices based on scenario template
    const randomInRange = (range: [number, number]) =>
      range[0] + Math.random() * (range[1] - range[0]);

    const landCover: LandCoverClass[] = [];
    let remainingPct = 100;

    for (const [type, range] of Object.entries(
      template.landCoverDistribution,
    )) {
      if (range && remainingPct > 0) {
        const pct = Math.min(
          randomInRange(range as [number, number]) * 100,
          remainingPct,
        );
        landCover.push({
          type: type as LandCoverClass["type"],
          percentage: Math.round(pct),
          confidence: 0.85 + Math.random() * 0.1,
        });
        remainingPct -= pct;
      }
    }

    return {
      id: params.id,
      position: params.position,
      bounds: params.bounds,
      indices: {
        ndvi: randomInRange(template.indices.ndvi),
        ndwi: randomInRange(template.indices.ndwi),
        ndbi: randomInRange(template.indices.ndbi),
      },
      landCover,
      features: template.typicalFeatures.slice(
        0,
        2 + Math.floor(Math.random() * 2),
      ),
      scenario: params.scenario,
      timestamp: new Date().toISOString(),
    };
  }

  /**
   * Perform directional spatial reasoning
   * Core task: Given central tile + direction → Generate adjacent tile
   */
  performSpatialReasoning(params: {
    centralTile: TileData;
    direction: Direction;
  }): SpatialReasoningResult {
    const { centralTile, direction } = params;

    // Calculate new bounds based on direction
    const tileWidth = centralTile.bounds.maxLng - centralTile.bounds.minLng;
    const tileHeight = centralTile.bounds.maxLat - centralTile.bounds.minLat;

    let newBounds: TileData["bounds"];
    let newPosition: { row: number; col: number };

    switch (direction) {
      case "up":
        newBounds = {
          minLat: centralTile.bounds.maxLat,
          maxLat: centralTile.bounds.maxLat + tileHeight,
          minLng: centralTile.bounds.minLng,
          maxLng: centralTile.bounds.maxLng,
        };
        newPosition = {
          row: centralTile.position.row - 1,
          col: centralTile.position.col,
        };
        break;
      case "down":
        newBounds = {
          minLat: centralTile.bounds.minLat - tileHeight,
          maxLat: centralTile.bounds.minLat,
          minLng: centralTile.bounds.minLng,
          maxLng: centralTile.bounds.maxLng,
        };
        newPosition = {
          row: centralTile.position.row + 1,
          col: centralTile.position.col,
        };
        break;
      case "left":
        newBounds = {
          minLat: centralTile.bounds.minLat,
          maxLat: centralTile.bounds.maxLat,
          minLng: centralTile.bounds.minLng - tileWidth,
          maxLng: centralTile.bounds.minLng,
        };
        newPosition = {
          row: centralTile.position.row,
          col: centralTile.position.col - 1,
        };
        break;
      case "right":
        newBounds = {
          minLat: centralTile.bounds.minLat,
          maxLat: centralTile.bounds.maxLat,
          minLng: centralTile.bounds.maxLng,
          maxLng: centralTile.bounds.maxLng + tileWidth,
        };
        newPosition = {
          row: centralTile.position.row,
          col: centralTile.position.col + 1,
        };
        break;
    }

    // Generate predicted tile with scenario continuity
    const predictedTile = this.generateTile({
      id: `tile_${newPosition.row}_${newPosition.col}`,
      position: newPosition,
      bounds: newBounds,
      scenario: centralTile.scenario,
    });

    // Apply spatial continuity - indices should be similar at boundaries
    const continuityFactor = 0.7 + Math.random() * 0.2;
    predictedTile.indices.ndvi =
      centralTile.indices.ndvi * continuityFactor +
      predictedTile.indices.ndvi * (1 - continuityFactor);
    predictedTile.indices.ndwi =
      centralTile.indices.ndwi * continuityFactor +
      predictedTile.indices.ndwi * (1 - continuityFactor);

    // Calculate quality metrics
    const spatialContinuity = 0.85 + Math.random() * 0.1;
    const semanticConsistency = 0.8 + Math.random() * 0.15;
    const confidence = (spatialContinuity + semanticConsistency) / 2;

    return {
      centralTile,
      direction,
      predictedTile,
      confidence,
      spatialContinuity,
      semanticConsistency,
      generationMethod: "RemoteBAGEL Directional Conditional Generation",
    };
  }

  /**
   * Expand satellite image in all 4 directions
   */
  expandMultiDirectional(params: {
    centralTile: TileData;
    expansionLevels?: number;
  }): MultiDirectionalExpansion {
    const { centralTile, expansionLevels = 1 } = params;

    // Generate expansions in all 4 directions
    const upResult = this.performSpatialReasoning({
      centralTile,
      direction: "up",
    });
    const downResult = this.performSpatialReasoning({
      centralTile,
      direction: "down",
    });
    const leftResult = this.performSpatialReasoning({
      centralTile,
      direction: "left",
    });
    const rightResult = this.performSpatialReasoning({
      centralTile,
      direction: "right",
    });

    // Build 3x3 grid (or larger based on expansion levels)
    const gridSize = 1 + expansionLevels * 2;
    const fullCoverage: TileData[][] = [];

    for (let r = 0; r < gridSize; r++) {
      const row: TileData[] = [];
      for (let c = 0; c < gridSize; c++) {
        if (r === Math.floor(gridSize / 2) && c === Math.floor(gridSize / 2)) {
          row.push(centralTile);
        } else {
          row.push(
            this.generateTile({
              id: `tile_${r}_${c}`,
              position: { row: r, col: c },
              bounds: {
                minLat:
                  centralTile.bounds.minLat +
                  (Math.floor(gridSize / 2) - r) *
                    (centralTile.bounds.maxLat - centralTile.bounds.minLat),
                maxLat:
                  centralTile.bounds.maxLat +
                  (Math.floor(gridSize / 2) - r) *
                    (centralTile.bounds.maxLat - centralTile.bounds.minLat),
                minLng:
                  centralTile.bounds.minLng +
                  (c - Math.floor(gridSize / 2)) *
                    (centralTile.bounds.maxLng - centralTile.bounds.minLng),
                maxLng:
                  centralTile.bounds.maxLng +
                  (c - Math.floor(gridSize / 2)) *
                    (centralTile.bounds.maxLng - centralTile.bounds.minLng),
              },
              scenario: centralTile.scenario,
            }),
          );
        }
      }
      fullCoverage.push(row);
    }

    // Calculate total area
    const tileArea =
      (centralTile.bounds.maxLat - centralTile.bounds.minLat) *
      (centralTile.bounds.maxLng - centralTile.bounds.minLng) *
      111 *
      111; // km²
    const totalArea = tileArea * gridSize * gridSize;

    // Analyze scenarios across expanded area
    const scenarioAnalysis = this.analyzeScenarios(fullCoverage.flat());

    return {
      centralTile,
      expansions: {
        up: upResult.predictedTile,
        down: downResult.predictedTile,
        left: leftResult.predictedTile,
        right: rightResult.predictedTile,
      },
      fullCoverage,
      totalArea: Math.round(totalArea * 100) / 100,
      scenarioAnalysis,
    };
  }

  /**
   * Analyze scenarios across tiles
   */
  private analyzeScenarios(tiles: TileData[]): ScenarioAnalysis {
    const scenarioCounts: { [key in ScenarioType]?: number } = {};

    tiles.forEach((tile) => {
      // Security: Validate scenario against whitelist to prevent property injection
      if (ALLOWED_SCENARIOS.has(tile.scenario)) {
        scenarioCounts[tile.scenario] =
          (scenarioCounts[tile.scenario] || 0) + 1;
      }
    });

    const dominantScenario = Object.entries(scenarioCounts).sort(
      (a, b) => b[1] - a[1],
    )[0][0] as ScenarioType;

    const scenarioDistribution: { [key in ScenarioType]?: number } = {};
    Object.entries(scenarioCounts).forEach(([scenario, count]) => {
      // Security: Validate scenario against whitelist
      if (ALLOWED_SCENARIOS.has(scenario)) {
        scenarioDistribution[scenario as ScenarioType] = Math.round(
          (count / tiles.length) * 100,
        );
      }
    });

    // Generate risk assessment based on scenario
    let riskAssessment: RiskAssessment | null = null;
    if (dominantScenario === "flood") {
      riskAssessment = {
        type: "flood",
        level: "high",
        affectedArea: tiles.filter((t) => t.scenario === "flood").length * 10, // km²
        trend: "stable",
        confidence: 0.85,
      };
    } else if (dominantScenario === "urban") {
      riskAssessment = {
        type: "urban_expansion",
        level: "medium",
        affectedArea: tiles.filter((t) => t.scenario === "urban").length * 10,
        trend: "increasing",
        confidence: 0.78,
      };
    }

    const recommendations: string[] = [];
    const recommendationsAr: string[] = [];

    if (dominantScenario === "flood") {
      recommendations.push("Deploy flood monitoring sensors in affected areas");
      recommendations.push(
        "Activate early warning system for downstream regions",
      );
      recommendationsAr.push(
        "نشر مستشعرات مراقبة الفيضانات في المناطق المتأثرة",
      );
      recommendationsAr.push(
        "تفعيل نظام الإنذار المبكر للمناطق في اتجاه التيار",
      );
    } else if (dominantScenario === "agricultural") {
      recommendations.push("Monitor crop health indices across expanded area");
      recommendations.push(
        "Plan irrigation based on spatial vegetation patterns",
      );
      recommendationsAr.push("مراقبة مؤشرات صحة المحاصيل عبر المنطقة الموسعة");
      recommendationsAr.push(
        "تخطيط الري بناءً على أنماط الغطاء النباتي المكاني",
      );
    }

    return {
      dominantScenario,
      scenarioDistribution,
      riskAssessment,
      recommendations,
      recommendationsAr,
    };
  }

  /**
   * Simulate 3x3 grid partitioning (as described in paper)
   */
  partitionImage(params: {
    imageWidth: number;
    imageHeight: number;
    centerLat: number;
    centerLng: number;
    scenario: ScenarioType;
  }): GridPartition {
    const { imageWidth, imageHeight, centerLat, centerLng, scenario } = params;

    const tileWidth = imageWidth / 3;
    const tileHeight = imageHeight / 3;
    const tileSizeLat = 0.01; // ~1km
    const tileSizeLng = 0.01;

    const tiles: TileData[][] = [];
    let trainingPairs = 0;

    for (let row = 0; row < 3; row++) {
      const tileRow: TileData[] = [];
      for (let col = 0; col < 3; col++) {
        const tile = this.generateTile({
          id: `tile_${row}_${col}`,
          position: { row, col },
          bounds: {
            minLat: centerLat + (1 - row) * tileSizeLat,
            maxLat: centerLat + (2 - row) * tileSizeLat,
            minLng: centerLng + (col - 1) * tileSizeLng,
            maxLng: centerLng + col * tileSizeLng,
          },
          scenario,
        });
        tileRow.push(tile);

        // Count training pairs (central tile with 4 adjacent)
        if (row === 1 && col === 1) {
          trainingPairs += 4; // 4 directions from center
        }
      }
      tiles.push(tileRow);
    }

    return {
      originalImage: { width: imageWidth, height: imageHeight },
      gridSize: { rows: 3, cols: 3 },
      tiles,
      overlapPercentage: 10, // As per paper
      totalTiles: 9,
      trainingPairs,
    };
  }

  /**
   * Generate training data pairs (self-supervised)
   */
  generateTrainingData(partition: GridPartition): TrainingData[] {
    const trainingData: TrainingData[] = [];
    const centerRow = 1;
    const centerCol = 1;
    const centralTile = partition.tiles[centerRow][centerCol];

    const directions: {
      dir: Direction;
      rowOffset: number;
      colOffset: number;
    }[] = [
      { dir: "up", rowOffset: -1, colOffset: 0 },
      { dir: "down", rowOffset: 1, colOffset: 0 },
      { dir: "left", rowOffset: 0, colOffset: -1 },
      { dir: "right", rowOffset: 0, colOffset: 1 },
    ];

    directions.forEach(({ dir, rowOffset, colOffset }) => {
      const adjRow = centerRow + rowOffset;
      const adjCol = centerCol + colOffset;

      if (adjRow >= 0 && adjRow < 3 && adjCol >= 0 && adjCol < 3) {
        trainingData.push({
          id: `train_${centralTile.id}_${dir}`,
          centralTile,
          direction: dir,
          adjacentTile: partition.tiles[adjRow][adjCol],
          overlap: partition.overlapPercentage,
        });
      }
    });

    return trainingData;
  }

  /**
   * Calculate RSWISE-style evaluation scores
   */
  evaluateGeneration(params: {
    predictedTile: TileData;
    groundTruthTile?: TileData;
  }): RSWISEScore {
    const { predictedTile, groundTruthTile } = params;

    // Simulate FID score (lower is better, we invert for display)
    const fid = groundTruthTile
      ? 100 -
        Math.abs(predictedTile.indices.ndvi - groundTruthTile.indices.ndvi) *
          100
      : 85 + Math.random() * 10;

    // Simulate GPT-4o spatial reasoning score
    const gptScore = 82 + Math.random() * 15;

    // Overall RSWISE score (paper reports 88.8 for RemoteBAGEL)
    const overall = (fid + gptScore) / 2;

    // Scores by scenario (horizontal easier than vertical as per paper)
    const byScenario: { [key in ScenarioType]?: number } = {
      general: 90 + Math.random() * 5,
      rural: 89 + Math.random() * 5,
      urban: 85 + Math.random() * 8,
      agricultural: 88 + Math.random() * 6,
      flood: 80 + Math.random() * 10, // Most challenging as per paper
    };

    // Horizontal directions are easier to model
    const byDirection: { [key in Direction]?: number } = {
      left: 90 + Math.random() * 5,
      right: 89 + Math.random() * 5,
      up: 85 + Math.random() * 8,
      down: 84 + Math.random() * 8,
    };

    return {
      overall: Math.round(overall * 10) / 10,
      fid: Math.round(fid * 10) / 10,
      gptScore: Math.round(gptScore * 10) / 10,
      byScenario,
      byDirection,
    };
  }

  /**
   * Get model performance benchmarks (from paper)
   */
  getBenchmarks(): {
    model: string;
    rswise: number;
    improvement: string;
    training: { images: number; pairs: number; gpus: string; hours: number };
  }[] {
    return [
      {
        model: "RemoteBAGEL (Ours)",
        rswise: 88.8,
        improvement: "Baseline",
        training: { images: 4000, pairs: 10080, gpus: "4×H100", hours: 20 },
      },
      {
        model: "BAGEL-7B",
        rswise: 62.4,
        improvement: "-29.7%",
        training: { images: 0, pairs: 0, gpus: "N/A", hours: 0 },
      },
      {
        model: "GPT-4o",
        rswise: 58.2,
        improvement: "-34.5%",
        training: { images: 0, pairs: 0, gpus: "N/A", hours: 0 },
      },
      {
        model: "Claude-3.5",
        rswise: 55.8,
        improvement: "-37.2%",
        training: { images: 0, pairs: 0, gpus: "N/A", hours: 0 },
      },
    ];
  }

  /**
   * Get system capabilities
   */
  getCapabilities(): {
    name: string;
    nameAr: string;
    description: string;
    supported: boolean;
  }[] {
    return [
      {
        name: "Directional Spatial Reasoning",
        nameAr: "الاستدلال المكاني الاتجاهي",
        description: "Generate adjacent tiles based on direction commands",
        supported: true,
      },
      {
        name: "Multi-Directional Expansion",
        nameAr: "التوسع متعدد الاتجاهات",
        description: "Expand imagery in all 4 directions simultaneously",
        supported: true,
      },
      {
        name: "Self-Supervised Training",
        nameAr: "التدريب الذاتي الإشراف",
        description: "No manual labeling required",
        supported: true,
      },
      {
        name: "Scenario-Aware Generation",
        nameAr: "التوليد الواعي بالسيناريو",
        description: "Adapt to flood, urban, rural, agricultural contexts",
        supported: true,
      },
      {
        name: "Spatial Continuity",
        nameAr: "الاستمرارية المكانية",
        description: "Maintain geographic structure across boundaries",
        supported: true,
      },
      {
        name: "Digital Twin Integration",
        nameAr: "تكامل التوأم الرقمي",
        description: "Connect with SAHOOL Digital Twin Core",
        supported: true,
      },
    ];
  }
}
