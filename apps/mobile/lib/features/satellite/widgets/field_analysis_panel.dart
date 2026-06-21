/// Field AI Analysis Panel — لوحة التحليل الموحد بالذكاء الاصطناعي
///
/// Displays a unified 13-section field analysis from field-intelligence service.
/// Single scrollable panel with collapsible sections, no tabs.
///
/// Schema mirrors FieldAnalysisResponse from field-intelligence service.
library;

import 'dart:convert';
import 'package:flutter/material.dart';

// ── Data models ───────────────────────────────────────────────────────────────

class ActionItem {
  final String priority; // critical | this_week | this_month
  final String text;

  const ActionItem({required this.priority, required this.text});

  factory ActionItem.fromJson(Map<String, dynamic> j) =>
      ActionItem(priority: j['priority'] as String? ?? 'this_month', text: j['text'] as String? ?? '');
}

class SectionContent {
  final String title;
  final String titleEn;
  final String status; // good | moderate | warning | critical
  final String statusColor; // green | yellow | orange | red
  final String summary;
  final List<String> details;
  final Map<String, dynamic>? metrics;
  final double confidence;

  const SectionContent({
    required this.title,
    required this.titleEn,
    required this.status,
    required this.statusColor,
    required this.summary,
    required this.details,
    this.metrics,
    this.confidence = 0.7,
  });

  factory SectionContent.fromJson(Map<String, dynamic> j) => SectionContent(
        title: j['title'] as String? ?? '',
        titleEn: j['title_en'] as String? ?? '',
        status: j['status'] as String? ?? 'moderate',
        statusColor: j['status_color'] as String? ?? 'yellow',
        summary: j['summary'] as String? ?? '',
        details: (j['details'] as List<dynamic>?)?.cast<String>() ?? [],
        metrics: j['metrics'] as Map<String, dynamic>?,
        confidence: (j['confidence'] as num?)?.toDouble() ?? 0.7,
      );
}

class AnalysisSections {
  final SectionContent healthOverview;
  final SectionContent vegetationHealth;
  final SectionContent waterStress;
  final SectionContent growthStage;
  final SectionContent nutrientStatus;
  final SectionContent pestDiseaseRisk;
  final SectionContent irrigationRecommendation;
  final SectionContent weatherImpact;
  final SectionContent yieldPrediction;
  final SectionContent soilHealth;
  final SectionContent historicalTrends;
  final SectionContent actionPlan;
  final SectionContent economicImpact;

  const AnalysisSections({
    required this.healthOverview,
    required this.vegetationHealth,
    required this.waterStress,
    required this.growthStage,
    required this.nutrientStatus,
    required this.pestDiseaseRisk,
    required this.irrigationRecommendation,
    required this.weatherImpact,
    required this.yieldPrediction,
    required this.soilHealth,
    required this.historicalTrends,
    required this.actionPlan,
    required this.economicImpact,
  });

  factory AnalysisSections.fromJson(Map<String, dynamic> j) {
    SectionContent _s(String key) =>
        SectionContent.fromJson(j[key] as Map<String, dynamic>? ?? {});
    return AnalysisSections(
      healthOverview: _s('health_overview'),
      vegetationHealth: _s('vegetation_health'),
      waterStress: _s('water_stress'),
      growthStage: _s('growth_stage'),
      nutrientStatus: _s('nutrient_status'),
      pestDiseaseRisk: _s('pest_disease_risk'),
      irrigationRecommendation: _s('irrigation_recommendation'),
      weatherImpact: _s('weather_impact'),
      yieldPrediction: _s('yield_prediction'),
      soilHealth: _s('soil_health'),
      historicalTrends: _s('historical_trends'),
      actionPlan: _s('action_plan'),
      economicImpact: _s('economic_impact'),
    );
  }

  List<MapEntry<String, SectionContent>> get orderedEntries => [
        MapEntry('health_overview', healthOverview),
        MapEntry('vegetation_health', vegetationHealth),
        MapEntry('water_stress', waterStress),
        MapEntry('growth_stage', growthStage),
        MapEntry('nutrient_status', nutrientStatus),
        MapEntry('pest_disease_risk', pestDiseaseRisk),
        MapEntry('irrigation_recommendation', irrigationRecommendation),
        MapEntry('weather_impact', weatherImpact),
        MapEntry('yield_prediction', yieldPrediction),
        MapEntry('soil_health', soilHealth),
        MapEntry('historical_trends', historicalTrends),
        MapEntry('action_plan', actionPlan),
        MapEntry('economic_impact', economicImpact),
      ];
}

class ImageryPayload {
  final String? trueColor;
  final String? ndviHeatmap;
  final String? ndmiHeatmap;
  final String? ndreHeatmap;

  const ImageryPayload({this.trueColor, this.ndviHeatmap, this.ndmiHeatmap, this.ndreHeatmap});

  factory ImageryPayload.fromJson(Map<String, dynamic> j) => ImageryPayload(
        trueColor: j['true_color'] as String?,
        ndviHeatmap: j['ndvi_heatmap'] as String?,
        ndmiHeatmap: j['ndmi_heatmap'] as String?,
        ndreHeatmap: j['ndre_heatmap'] as String?,
      );

  bool get hasAny => trueColor != null || ndviHeatmap != null || ndmiHeatmap != null || ndreHeatmap != null;

  List<MapEntry<String, String>> get available {
    final items = <MapEntry<String, String>>[];
    if (trueColor != null) items.add(MapEntry('الألوان الحقيقية', trueColor!));
    if (ndviHeatmap != null) items.add(MapEntry('NDVI', ndviHeatmap!));
    if (ndmiHeatmap != null) items.add(MapEntry('NDMI', ndmiHeatmap!));
    if (ndreHeatmap != null) items.add(MapEntry('NDRE', ndreHeatmap!));
    return items;
  }
}

class FieldAnalysisResult {
  final String fieldId;
  final String analyzedAt;
  final bool cached;
  final int healthScore;
  final String healthClass; // healthy | moderate | stressed | critical
  final double healthConfidence;
  final ImageryPayload? imagery;
  final AnalysisSections? sections;
  final Map<String, double?> indicesSummary;
  final String? satelliteDate;
  final double? cloudCoverPct;
  final List<String> dataSources;
  final String indice;
  // Legacy compat
  final List<String> currentStatus;
  final List<String> recommendations;

  const FieldAnalysisResult({
    required this.fieldId,
    required this.analyzedAt,
    required this.cached,
    required this.healthScore,
    required this.healthClass,
    required this.healthConfidence,
    this.imagery,
    this.sections,
    required this.indicesSummary,
    this.satelliteDate,
    this.cloudCoverPct,
    required this.dataSources,
    required this.indice,
    required this.currentStatus,
    required this.recommendations,
  });

  factory FieldAnalysisResult.fromJson(Map<String, dynamic> j) => FieldAnalysisResult(
        fieldId: j['field_id'] as String? ?? '',
        analyzedAt: j['analyzed_at'] as String? ?? '',
        cached: j['cached'] as bool? ?? false,
        healthScore: j['health_score'] as int? ?? 0,
        healthClass: j['health_class'] as String? ?? 'moderate',
        healthConfidence: (j['health_confidence'] as num?)?.toDouble() ?? 0.0,
        imagery: j['imagery'] != null ? ImageryPayload.fromJson(j['imagery'] as Map<String, dynamic>) : null,
        sections: j['sections'] != null ? AnalysisSections.fromJson(j['sections'] as Map<String, dynamic>) : null,
        indicesSummary: (j['indices_summary'] as Map<String, dynamic>?)
                ?.map((k, v) => MapEntry(k, (v as num?)?.toDouble())) ??
            {},
        satelliteDate: j['satellite_date'] as String?,
        cloudCoverPct: (j['cloud_cover_pct'] as num?)?.toDouble(),
        dataSources: (j['data_sources'] as List<dynamic>?)?.cast<String>() ?? [],
        indice: j['indice'] as String? ?? 'NDVI',
        currentStatus: (j['current_status'] as List<dynamic>?)?.cast<String>() ?? [],
        recommendations: (j['recommendations'] as List<dynamic>?)?.cast<String>() ?? [],
      );
}

// ── Widget ────────────────────────────────────────────────────────────────────

class FieldAnalysisPanel extends StatefulWidget {
  final FieldAnalysisResult result;
  final String fieldName;
  final VoidCallback? onClose;

  const FieldAnalysisPanel({
    super.key,
    required this.result,
    required this.fieldName,
    this.onClose,
  });

  @override
  State<FieldAnalysisPanel> createState() => _FieldAnalysisPanelState();
}

class _FieldAnalysisPanelState extends State<FieldAnalysisPanel> {
  // First 5 sections expanded by default
  final Set<String> _expanded = {
    'health_overview',
    'vegetation_health',
    'water_stress',
    'growth_stage',
    'nutrient_status',
  };

  Color get _healthColor {
    final score = widget.result.healthScore;
    if (score >= 70) return const Color(0xFF4CAF50);
    if (score >= 40) return const Color(0xFFFFC107);
    return const Color(0xFFF44336);
  }

  String get _healthLabel {
    switch (widget.result.healthClass) {
      case 'healthy':
        return 'صحي';
      case 'moderate':
        return 'متوسط';
      case 'stressed':
        return 'مجهد';
      case 'critical':
      case 'diseased':
        return 'حرج';
      default:
        return 'غير محدد';
    }
  }

  String _statusIcon(String status) {
    switch (status) {
      case 'good':
        return '✅';
      case 'moderate':
        return '🟡';
      case 'warning':
        return '🟠';
      case 'critical':
        return '🔴';
      default:
        return '⚪';
    }
  }

  Color _statusColor(String color) {
    switch (color) {
      case 'green':
        return const Color(0xFF3FB950);
      case 'yellow':
        return const Color(0xFFFFC107);
      case 'orange':
        return const Color(0xFFFF9800);
      case 'red':
        return const Color(0xFFF44336);
      default:
        return const Color(0xFF8B949E);
    }
  }

  @override
  Widget build(BuildContext context) {
    const bg = Color(0xFF0D1117);
    const cardBg = Color(0xFF161B22);
    const border = Color(0xFF30363D);
    final r = widget.result;

    return Directionality(
      textDirection: TextDirection.rtl,
      child: Container(
        decoration: const BoxDecoration(
          color: bg,
          borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            // Drag handle
            Container(
              width: 40, height: 4,
              margin: const EdgeInsets.only(top: 10, bottom: 6),
              decoration: BoxDecoration(color: border, borderRadius: BorderRadius.circular(2)),
            ),

            // Header
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              child: Row(
                children: [
                  const Icon(Icons.psychology, color: Color(0xFFAB8BFF), size: 18),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(widget.fieldName, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 14)),
                        Row(
                          children: [
                            _StatusChip(label: _healthLabel, color: _healthColor),
                            const SizedBox(width: 6),
                            _MonoBadge(label: r.indice),
                            if (r.cached) ...[const SizedBox(width: 6), _MonoBadge(label: 'مخزّن', color: border)],
                          ],
                        ),
                      ],
                    ),
                  ),
                  if (widget.onClose != null)
                    IconButton(icon: const Icon(Icons.close, size: 18, color: Color(0xFF8B949E)), onPressed: widget.onClose, padding: EdgeInsets.zero, constraints: const BoxConstraints()),
                ],
              ),
            ),

            // Scrollable content
            Expanded(
              child: ListView(
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                children: [
                  // Imagery gallery
                  if (r.imagery != null && r.imagery!.hasAny)
                    SizedBox(
                      height: 120,
                      child: ListView.separated(
                        scrollDirection: Axis.horizontal,
                        itemCount: r.imagery!.available.length,
                        separatorBuilder: (_, __) => const SizedBox(width: 8),
                        itemBuilder: (ctx, i) {
                          final img = r.imagery!.available[i];
                          return Column(
                            children: [
                              ClipRRect(
                                borderRadius: BorderRadius.circular(8),
                                child: Image.memory(base64Decode(img.value), width: 120, height: 90, fit: BoxFit.cover),
                              ),
                              const SizedBox(height: 4),
                              Text(img.key, style: const TextStyle(color: Color(0xFF8B949E), fontSize: 10)),
                            ],
                          );
                        },
                      ),
                    ),

                  const SizedBox(height: 12),

                  // Health score badge
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(color: cardBg, borderRadius: BorderRadius.circular(12), border: Border.all(color: border)),
                    child: Row(
                      children: [
                        SizedBox(
                          width: 56, height: 56,
                          child: Stack(
                            alignment: Alignment.center,
                            children: [
                              CircularProgressIndicator(
                                value: r.healthScore / 100,
                                strokeWidth: 4,
                                backgroundColor: const Color(0xFF374151),
                                valueColor: AlwaysStoppedAnimation(_healthColor),
                              ),
                              Text('${r.healthScore}', style: TextStyle(color: _healthColor, fontWeight: FontWeight.bold, fontSize: 16)),
                            ],
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(_healthLabel, style: TextStyle(color: _healthColor, fontWeight: FontWeight.w600, fontSize: 14)),
                              Text('ثقة: ${(r.healthConfidence * 100).toStringAsFixed(0)}% | ${r.indice}', style: const TextStyle(color: Color(0xFF8B949E), fontSize: 11)),
                              if (r.satelliteDate != null) Text('تاريخ الصورة: ${r.satelliteDate}', style: const TextStyle(color: Color(0xFF6B7280), fontSize: 10)),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),

                  const SizedBox(height: 12),

                  // 13 sections
                  if (r.sections != null)
                    ...r.sections!.orderedEntries.map((entry) => _buildSection(entry.key, entry.value, cardBg, border)),

                  // Legacy fallback
                  if (r.sections == null && r.currentStatus.isNotEmpty)
                    _buildLegacyFallback(r, cardBg, border),

                  const SizedBox(height: 16),
                ],
              ),
            ),

            // Footer
            Container(
              padding: const EdgeInsets.symmetric(vertical: 8),
              decoration: const BoxDecoration(border: Border(top: BorderSide(color: border, width: 1))),
              child: Text(
                'AgriGuard · ${(r.healthConfidence * 100).toStringAsFixed(0)}% ثقة · Claude Sonnet',
                textAlign: TextAlign.center,
                style: const TextStyle(color: Color(0xFF8B949E), fontSize: 11),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSection(String key, SectionContent section, Color cardBg, Color border) {
    final isExpanded = _expanded.contains(key);
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Container(
        decoration: BoxDecoration(color: cardBg, borderRadius: BorderRadius.circular(8), border: Border.all(color: border)),
        child: Column(
          children: [
            InkWell(
              onTap: () => setState(() => isExpanded ? _expanded.remove(key) : _expanded.add(key)),
              borderRadius: BorderRadius.circular(8),
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                child: Row(
                  children: [
                    Text(_statusIcon(section.status), style: const TextStyle(fontSize: 14)),
                    const SizedBox(width: 8),
                    Expanded(child: Text(section.title, style: const TextStyle(color: Colors.white, fontSize: 13, fontWeight: FontWeight.w500))),
                    Text(section.titleEn, style: const TextStyle(color: Color(0xFF6B7280), fontSize: 10)),
                    const SizedBox(width: 4),
                    Icon(isExpanded ? Icons.expand_less : Icons.expand_more, size: 16, color: const Color(0xFF8B949E)),
                  ],
                ),
              ),
            ),
            if (isExpanded)
              Container(
                width: double.infinity,
                padding: const EdgeInsets.fromLTRB(12, 0, 12, 12),
                decoration: const BoxDecoration(border: Border(top: BorderSide(color: Color(0xFF30363D), width: 0.5))),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const SizedBox(height: 8),
                    Text(section.summary, style: const TextStyle(color: Color(0xFFE6EDF3), fontSize: 12, height: 1.5)),
                    if (section.details.isNotEmpty) ...[
                      const SizedBox(height: 8),
                      ...section.details.map((d) => Padding(
                            padding: const EdgeInsets.only(bottom: 4),
                            child: Row(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                const Text('•  ', style: TextStyle(color: Color(0xFF3FB950), fontWeight: FontWeight.bold, fontSize: 10)),
                                Expanded(child: Text(d, style: const TextStyle(color: Color(0xFFC9D1D9), fontSize: 11, height: 1.4))),
                              ],
                            ),
                          )),
                    ],
                    if (section.confidence > 0)
                      Padding(
                        padding: const EdgeInsets.only(top: 8),
                        child: Row(
                          children: [
                            Expanded(
                              child: ClipRRect(
                                borderRadius: BorderRadius.circular(2),
                                child: LinearProgressIndicator(
                                  value: section.confidence,
                                  minHeight: 3,
                                  backgroundColor: const Color(0xFF374151),
                                  valueColor: AlwaysStoppedAnimation(section.confidence > 0.7 ? const Color(0xFF3FB950) : section.confidence > 0.4 ? const Color(0xFFFFC107) : const Color(0xFFF44336)),
                                ),
                              ),
                            ),
                            const SizedBox(width: 8),
                            Text('${(section.confidence * 100).toStringAsFixed(0)}%', style: const TextStyle(color: Color(0xFF6B7280), fontSize: 10)),
                          ],
                        ),
                      ),
                  ],
                ),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildLegacyFallback(FieldAnalysisResult r, Color cardBg, Color border) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(color: cardBg, borderRadius: BorderRadius.circular(8), border: Border.all(color: border)),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('التحليل', style: TextStyle(color: Colors.white, fontSize: 13, fontWeight: FontWeight.w600)),
          const SizedBox(height: 8),
          ...r.currentStatus.map((s) => Padding(
                padding: const EdgeInsets.only(bottom: 4),
                child: Text('• $s', style: const TextStyle(color: Color(0xFFE6EDF3), fontSize: 12, height: 1.4)),
              )),
          if (r.recommendations.isNotEmpty) ...[
            const SizedBox(height: 12),
            const Text('التوصيات', style: TextStyle(color: Colors.white, fontSize: 13, fontWeight: FontWeight.w600)),
            const SizedBox(height: 8),
            ...r.recommendations.map((s) => Padding(
                  padding: const EdgeInsets.only(bottom: 4),
                  child: Text('• $s', style: const TextStyle(color: Color(0xFFE6EDF3), fontSize: 12, height: 1.4)),
                )),
          ],
        ],
      ),
    );
  }
}

// ── Small sub-widgets ─────────────────────────────────────────────────────────

class _StatusChip extends StatelessWidget {
  final String label;
  final Color color;

  const _StatusChip({required this.label, required this.color});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.15),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: color.withValues(alpha: 0.4)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(width: 6, height: 6, decoration: BoxDecoration(shape: BoxShape.circle, color: color)),
          const SizedBox(width: 5),
          Text(label, style: TextStyle(color: color, fontSize: 12, fontWeight: FontWeight.w600)),
        ],
      ),
    );
  }
}

class _MonoBadge extends StatelessWidget {
  final String label;
  final Color? color;

  const _MonoBadge({required this.label, this.color});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
      decoration: BoxDecoration(
        color: (color ?? const Color(0xFF1F6FEB)).withValues(alpha: 0.15),
        borderRadius: BorderRadius.circular(4),
        border: Border.all(color: (color ?? const Color(0xFF1F6FEB)).withValues(alpha: 0.4)),
      ),
      child: Text(
        label,
        style: TextStyle(
          color: color ?? const Color(0xFF58A6FF),
          fontSize: 10,
          fontFamily: 'monospace',
          fontWeight: FontWeight.bold,
        ),
      ),
    );
  }
}
