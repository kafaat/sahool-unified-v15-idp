import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/features/profitability/models/profitability_models.dart';

void main() {
  // ═══════════════════════════════════════════════════════════════════════════
  // CostType Enum
  // ═══════════════════════════════════════════════════════════════════════════

  group('CostType', () {
    test('has exactly 10 values', () {
      expect(CostType.values.length, 10);
    });

    test('getName returns Arabic name for ar locale', () {
      expect(CostType.seeds.getName('ar'), 'بذور');
      expect(CostType.fertilizer.getName('ar'), 'أسمدة');
      expect(CostType.pesticides.getName('ar'), 'مبيدات');
      expect(CostType.labor.getName('ar'), 'عمالة');
      expect(CostType.irrigation.getName('ar'), 'ري');
      expect(CostType.equipment.getName('ar'), 'معدات');
      expect(CostType.land.getName('ar'), 'إيجار أرض');
      expect(CostType.transport.getName('ar'), 'نقل');
      expect(CostType.storage.getName('ar'), 'تخزين');
      expect(CostType.other.getName('ar'), 'أخرى');
    });

    test('getName returns English name for en locale', () {
      expect(CostType.seeds.getName('en'), 'Seeds');
      expect(CostType.fertilizer.getName('en'), 'Fertilizer');
      expect(CostType.land.getName('en'), 'Land Rent');
    });

    test('getName returns English for non-ar locale', () {
      expect(CostType.seeds.getName('fr'), 'Seeds');
    });

    test('fromString parses valid values', () {
      expect(CostType.fromString('seeds'), CostType.seeds);
      expect(CostType.fromString('fertilizer'), CostType.fertilizer);
      expect(CostType.fromString('pesticides'), CostType.pesticides);
      expect(CostType.fromString('labor'), CostType.labor);
      expect(CostType.fromString('irrigation'), CostType.irrigation);
      expect(CostType.fromString('equipment'), CostType.equipment);
      expect(CostType.fromString('land'), CostType.land);
      expect(CostType.fromString('transport'), CostType.transport);
      expect(CostType.fromString('storage'), CostType.storage);
      expect(CostType.fromString('other'), CostType.other);
    });

    test('fromString returns other for unknown value', () {
      expect(CostType.fromString('unknown'), CostType.other);
      expect(CostType.fromString(''), CostType.other);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // RevenueType Enum
  // ═══════════════════════════════════════════════════════════════════════════

  group('RevenueType', () {
    test('has exactly 4 values', () {
      expect(RevenueType.values.length, 4);
    });

    test('getName returns Arabic name for ar locale', () {
      expect(RevenueType.crop.getName('ar'), 'محصول');
      expect(RevenueType.byProduct.getName('ar'), 'منتج ثانوي');
      expect(RevenueType.subsidy.getName('ar'), 'دعم');
      expect(RevenueType.other.getName('ar'), 'أخرى');
    });

    test('getName returns English name for en locale', () {
      expect(RevenueType.crop.getName('en'), 'Crop');
      expect(RevenueType.byProduct.getName('en'), 'By-product');
      expect(RevenueType.subsidy.getName('en'), 'Subsidy');
      expect(RevenueType.other.getName('en'), 'Other');
    });

    test('fromString parses valid values', () {
      expect(RevenueType.fromString('crop'), RevenueType.crop);
      expect(RevenueType.fromString('by_product'), RevenueType.byProduct);
      expect(RevenueType.fromString('subsidy'), RevenueType.subsidy);
      expect(RevenueType.fromString('other'), RevenueType.other);
    });

    test('fromString returns other for unknown value', () {
      expect(RevenueType.fromString('unknown'), RevenueType.other);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // CostCategory
  // ═══════════════════════════════════════════════════════════════════════════

  group('CostCategory', () {
    final sampleDate = DateTime(2025, 6, 15);
    final sampleJson = <String, dynamic>{
      'category_id': 'cost-001',
      'type': 'fertilizer',
      'name': 'Urea 46%',
      'name_ar': 'يوريا 46%',
      'amount': 5000.0,
      'unit': 'kg',
      'unit_ar': 'كجم',
      'quantity': 100.0,
      'unit_cost': 50.0,
      'description': 'Top dressing',
      'description_ar': 'تسميد سطحي',
      'date': '2025-06-15T00:00:00.000',
      'metadata': {'batch': 'B001'},
    };

    test('fromJson creates correct instance', () {
      final cost = CostCategory.fromJson(sampleJson);
      expect(cost.categoryId, 'cost-001');
      expect(cost.type, CostType.fertilizer);
      expect(cost.name, 'Urea 46%');
      expect(cost.nameAr, 'يوريا 46%');
      expect(cost.amount, 5000.0);
      expect(cost.unit, 'kg');
      expect(cost.unitAr, 'كجم');
      expect(cost.quantity, 100.0);
      expect(cost.unitCost, 50.0);
      expect(cost.description, 'Top dressing');
      expect(cost.descriptionAr, 'تسميد سطحي');
      expect(cost.metadata, {'batch': 'B001'});
    });

    test('toJson produces correct map', () {
      final cost = CostCategory.fromJson(sampleJson);
      final json = cost.toJson();
      expect(json['category_id'], 'cost-001');
      expect(json['type'], 'fertilizer');
      expect(json['amount'], 5000.0);
      expect(json['quantity'], 100.0);
      expect(json['unit_cost'], 50.0);
    });

    test('fromJson -> toJson round-trip preserves data', () {
      final cost = CostCategory.fromJson(sampleJson);
      final json = cost.toJson();
      final restored = CostCategory.fromJson(json);
      expect(restored.categoryId, cost.categoryId);
      expect(restored.type, cost.type);
      expect(restored.amount, cost.amount);
      expect(restored.quantity, cost.quantity);
    });

    test('getDisplayName returns Arabic when locale is ar', () {
      final cost = CostCategory.fromJson(sampleJson);
      expect(cost.getDisplayName('ar'), 'يوريا 46%');
    });

    test('getDisplayName returns English when locale is en', () {
      final cost = CostCategory.fromJson(sampleJson);
      expect(cost.getDisplayName('en'), 'Urea 46%');
    });

    test('getDisplayName returns English when nameAr is null', () {
      final json = Map<String, dynamic>.from(sampleJson)..['name_ar'] = null;
      final cost = CostCategory.fromJson(json);
      expect(cost.getDisplayName('ar'), 'Urea 46%');
    });

    test('getUnit returns Arabic when locale is ar', () {
      final cost = CostCategory.fromJson(sampleJson);
      expect(cost.getUnit('ar'), 'كجم');
    });

    test('getUnit returns English when locale is en', () {
      final cost = CostCategory.fromJson(sampleJson);
      expect(cost.getUnit('en'), 'kg');
    });

    test('getDescription returns Arabic when locale is ar', () {
      final cost = CostCategory.fromJson(sampleJson);
      expect(cost.getDescription('ar'), 'تسميد سطحي');
    });

    test('getDescription returns English when locale is en', () {
      final cost = CostCategory.fromJson(sampleJson);
      expect(cost.getDescription('en'), 'Top dressing');
    });

    test('getDescription returns null when both are null', () {
      final json = Map<String, dynamic>.from(sampleJson)
        ..['description'] = null
        ..['description_ar'] = null;
      final cost = CostCategory.fromJson(json);
      expect(cost.getDescription('en'), isNull);
    });

    test('fromJson handles null optional fields', () {
      final json = <String, dynamic>{
        'category_id': 'cost-002',
        'type': 'seeds',
        'name': 'Wheat Seeds',
        'amount': 2000,
        'unit': 'kg',
        'quantity': 50,
        'unit_cost': 40,
        'date': '2025-01-01T00:00:00.000',
      };
      final cost = CostCategory.fromJson(json);
      expect(cost.nameAr, isNull);
      expect(cost.unitAr, isNull);
      expect(cost.description, isNull);
      expect(cost.descriptionAr, isNull);
      expect(cost.metadata, isNull);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Revenue
  // ═══════════════════════════════════════════════════════════════════════════

  group('Revenue', () {
    final sampleJson = <String, dynamic>{
      'revenue_id': 'rev-001',
      'type': 'crop',
      'name': 'Wheat Harvest',
      'name_ar': 'حصاد القمح',
      'amount': 15000.0,
      'quantity': 5.0,
      'unit': 'ton',
      'unit_ar': 'طن',
      'unit_price': 3000.0,
      'date': '2025-07-01T00:00:00.000',
      'description': 'Main harvest',
      'description_ar': 'الحصاد الرئيسي',
      'metadata': {'grade': 'A'},
    };

    test('fromJson creates correct instance', () {
      final rev = Revenue.fromJson(sampleJson);
      expect(rev.revenueId, 'rev-001');
      expect(rev.type, RevenueType.crop);
      expect(rev.name, 'Wheat Harvest');
      expect(rev.amount, 15000.0);
      expect(rev.quantity, 5.0);
      expect(rev.unitPrice, 3000.0);
    });

    test('toJson produces correct map', () {
      final rev = Revenue.fromJson(sampleJson);
      final json = rev.toJson();
      expect(json['revenue_id'], 'rev-001');
      expect(json['type'], 'crop');
      expect(json['unit_price'], 3000.0);
    });

    test('fromJson -> toJson round-trip', () {
      final rev = Revenue.fromJson(sampleJson);
      final restored = Revenue.fromJson(rev.toJson());
      expect(restored.revenueId, rev.revenueId);
      expect(restored.amount, rev.amount);
    });

    test('getDisplayName locale support', () {
      final rev = Revenue.fromJson(sampleJson);
      expect(rev.getDisplayName('ar'), 'حصاد القمح');
      expect(rev.getDisplayName('en'), 'Wheat Harvest');
    });

    test('getUnit locale support', () {
      final rev = Revenue.fromJson(sampleJson);
      expect(rev.getUnit('ar'), 'طن');
      expect(rev.getUnit('en'), 'ton');
    });

    test('getDescription locale support', () {
      final rev = Revenue.fromJson(sampleJson);
      expect(rev.getDescription('ar'), 'الحصاد الرئيسي');
      expect(rev.getDescription('en'), 'Main harvest');
    });

    test('fromJson handles by_product type', () {
      final json = Map<String, dynamic>.from(sampleJson)
        ..['type'] = 'by_product';
      final rev = Revenue.fromJson(json);
      expect(rev.type, RevenueType.byProduct);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // BreakEvenAnalysis
  // ═══════════════════════════════════════════════════════════════════════════

  group('BreakEvenAnalysis', () {
    final sampleJson = <String, dynamic>{
      'fixed_costs': 5000.0,
      'variable_costs': 10000.0,
      'total_costs': 15000.0,
      'expected_revenue': 25000.0,
      'break_even_quantity': 3.0,
      'break_even_revenue': 15000.0,
      'unit': 'ton',
      'unit_ar': 'طن',
      'parameters': {'price_per_unit': 5000.0},
    };

    test('fromJson creates correct instance', () {
      final bea = BreakEvenAnalysis.fromJson(sampleJson);
      expect(bea.fixedCosts, 5000.0);
      expect(bea.variableCosts, 10000.0);
      expect(bea.totalCosts, 15000.0);
      expect(bea.expectedRevenue, 25000.0);
      expect(bea.breakEvenQuantity, 3.0);
      expect(bea.breakEvenRevenue, 15000.0);
      expect(bea.unit, 'ton');
      expect(bea.unitAr, 'طن');
    });

    test('toJson produces correct map', () {
      final bea = BreakEvenAnalysis.fromJson(sampleJson);
      final json = bea.toJson();
      expect(json['fixed_costs'], 5000.0);
      expect(json['variable_costs'], 10000.0);
      expect(json['unit'], 'ton');
    });

    test('fromJson -> toJson round-trip', () {
      final bea = BreakEvenAnalysis.fromJson(sampleJson);
      final restored = BreakEvenAnalysis.fromJson(bea.toJson());
      expect(restored.fixedCosts, bea.fixedCosts);
      expect(restored.breakEvenQuantity, bea.breakEvenQuantity);
    });

    test('getSafetyMargin calculates correctly', () {
      final bea = BreakEvenAnalysis.fromJson(sampleJson);
      // (25000 - 15000) / 25000 * 100 = 40.0
      expect(bea.getSafetyMargin(), 40.0);
    });

    test('getSafetyMargin returns 0 when expectedRevenue is 0', () {
      final json = Map<String, dynamic>.from(sampleJson)
        ..['expected_revenue'] = 0;
      final bea = BreakEvenAnalysis.fromJson(json);
      expect(bea.getSafetyMargin(), 0);
    });

    test('getSafetyMargin negative when breakEven exceeds expected', () {
      final json = Map<String, dynamic>.from(sampleJson)
        ..['expected_revenue'] = 10000.0
        ..['break_even_revenue'] = 15000.0;
      final bea = BreakEvenAnalysis.fromJson(json);
      // (10000 - 15000) / 10000 * 100 = -50.0
      expect(bea.getSafetyMargin(), -50.0);
    });

    test('getUnit locale support', () {
      final bea = BreakEvenAnalysis.fromJson(sampleJson);
      expect(bea.getUnit('ar'), 'طن');
      expect(bea.getUnit('en'), 'ton');
    });

    test('fromJson handles null optional fields', () {
      final json = <String, dynamic>{
        'fixed_costs': 100,
        'variable_costs': 200,
        'total_costs': 300,
        'expected_revenue': 500,
        'break_even_quantity': 1,
        'break_even_revenue': 300,
        'unit': 'kg',
      };
      final bea = BreakEvenAnalysis.fromJson(json);
      expect(bea.unitAr, isNull);
      expect(bea.parameters, isNull);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // CropProfitability
  // ═══════════════════════════════════════════════════════════════════════════

  group('CropProfitability', () {
    Map<String, dynamic> _makeCropJson({
      double netProfit = 10000,
      double roi = 50,
      List<Map<String, dynamic>>? costs,
      List<Map<String, dynamic>>? revenues,
      Map<String, dynamic>? breakEvenAnalysis,
    }) {
      return {
        'profitability_id': 'prof-001',
        'tenant_id': 'tenant-001',
        'field_id': 'field-001',
        'field_name': 'North Field',
        'field_name_ar': 'الحقل الشمالي',
        'crop_type': 'wheat',
        'crop_name': 'Winter Wheat',
        'crop_name_ar': 'قمح شتوي',
        'season': 'Winter 2025',
        'season_ar': 'شتاء 2025',
        'area': 10.0,
        'yield': 4.5,
        'total_yield': 45.0,
        'costs': costs ??
            [
              {
                'category_id': 'c1',
                'type': 'seeds',
                'name': 'Seeds',
                'amount': 2000.0,
                'unit': 'kg',
                'quantity': 100,
                'unit_cost': 20,
                'date': '2025-01-01T00:00:00.000',
              },
              {
                'category_id': 'c2',
                'type': 'fertilizer',
                'name': 'Urea',
                'amount': 3000.0,
                'unit': 'kg',
                'quantity': 60,
                'unit_cost': 50,
                'date': '2025-02-01T00:00:00.000',
              },
              {
                'category_id': 'c3',
                'type': 'fertilizer',
                'name': 'DAP',
                'amount': 1500.0,
                'unit': 'kg',
                'quantity': 30,
                'unit_cost': 50,
                'date': '2025-02-15T00:00:00.000',
              },
            ],
        'total_costs': 6500.0,
        'revenues': revenues ??
            [
              {
                'revenue_id': 'r1',
                'type': 'crop',
                'name': 'Wheat',
                'amount': 15000.0,
                'quantity': 45,
                'unit': 'ton',
                'unit_price': 333.33,
                'date': '2025-06-01T00:00:00.000',
              },
              {
                'revenue_id': 'r2',
                'type': 'by_product',
                'name': 'Straw',
                'amount': 1500.0,
                'quantity': 10,
                'unit': 'ton',
                'unit_price': 150,
                'date': '2025-06-15T00:00:00.000',
              },
            ],
        'total_revenue': 16500.0,
        'net_profit': netProfit,
        'profit_margin': 60.6,
        'roi': roi,
        'cost_per_hectare': 650.0,
        'revenue_per_hectare': 1650.0,
        'profit_per_hectare': 1000.0,
        'break_even_analysis': breakEvenAnalysis,
        'start_date': '2025-01-01T00:00:00.000',
        'end_date': '2025-06-30T00:00:00.000',
        'created_at': '2025-01-01T00:00:00.000',
        'updated_at': '2025-06-30T00:00:00.000',
        'metadata': {'version': 1},
      };
    }

    test('fromJson creates correct instance', () {
      final crop = CropProfitability.fromJson(_makeCropJson());
      expect(crop.profitabilityId, 'prof-001');
      expect(crop.cropType, 'wheat');
      expect(crop.area, 10.0);
      expect(crop.costs.length, 3);
      expect(crop.revenues.length, 2);
    });

    test('toJson produces correct map', () {
      final crop = CropProfitability.fromJson(_makeCropJson());
      final json = crop.toJson();
      expect(json['profitability_id'], 'prof-001');
      expect(json['crop_type'], 'wheat');
      expect(json['area'], 10.0);
      expect((json['costs'] as List).length, 3);
    });

    test('fromJson -> toJson round-trip', () {
      final crop = CropProfitability.fromJson(_makeCropJson());
      final restored = CropProfitability.fromJson(crop.toJson());
      expect(restored.profitabilityId, crop.profitabilityId);
      expect(restored.costs.length, crop.costs.length);
      expect(restored.revenues.length, crop.revenues.length);
    });

    test('isProfitable returns true when netProfit > 0', () {
      final crop = CropProfitability.fromJson(_makeCropJson(netProfit: 5000));
      expect(crop.isProfitable, isTrue);
    });

    test('isProfitable returns false when netProfit <= 0', () {
      final crop = CropProfitability.fromJson(_makeCropJson(netProfit: 0));
      expect(crop.isProfitable, isFalse);
    });

    test('isProfitable returns false when netProfit is negative', () {
      final crop = CropProfitability.fromJson(_makeCropJson(netProfit: -1000));
      expect(crop.isProfitable, isFalse);
    });

    test('getCostsByType aggregates correctly', () {
      final crop = CropProfitability.fromJson(_makeCropJson());
      final costMap = crop.getCostsByType();
      expect(costMap[CostType.seeds], 2000.0);
      // fertilizer: 3000 + 1500 = 4500
      expect(costMap[CostType.fertilizer], 4500.0);
      expect(costMap[CostType.labor], isNull);
    });

    test('getRevenuesByType aggregates correctly', () {
      final crop = CropProfitability.fromJson(_makeCropJson());
      final revMap = crop.getRevenuesByType();
      expect(revMap[RevenueType.crop], 15000.0);
      expect(revMap[RevenueType.byProduct], 1500.0);
      expect(revMap[RevenueType.subsidy], isNull);
    });

    test('getFieldName locale support', () {
      final crop = CropProfitability.fromJson(_makeCropJson());
      expect(crop.getFieldName('ar'), 'الحقل الشمالي');
      expect(crop.getFieldName('en'), 'North Field');
    });

    test('getCropName locale support', () {
      final crop = CropProfitability.fromJson(_makeCropJson());
      expect(crop.getCropName('ar'), 'قمح شتوي');
      expect(crop.getCropName('en'), 'Winter Wheat');
    });

    test('getSeason locale support', () {
      final crop = CropProfitability.fromJson(_makeCropJson());
      expect(crop.getSeason('ar'), 'شتاء 2025');
      expect(crop.getSeason('en'), 'Winter 2025');
    });

    test('fromJson with breakEvenAnalysis', () {
      final beaJson = {
        'fixed_costs': 2000.0,
        'variable_costs': 4500.0,
        'total_costs': 6500.0,
        'expected_revenue': 16500.0,
        'break_even_quantity': 20.0,
        'break_even_revenue': 6500.0,
        'unit': 'ton',
      };
      final crop =
          CropProfitability.fromJson(_makeCropJson(breakEvenAnalysis: beaJson));
      expect(crop.breakEvenAnalysis, isNotNull);
      expect(crop.breakEvenAnalysis!.fixedCosts, 2000.0);
    });

    test('fromJson with null breakEvenAnalysis', () {
      final crop = CropProfitability.fromJson(_makeCropJson());
      expect(crop.breakEvenAnalysis, isNull);
    });

    test('fromJson handles null endDate', () {
      final json = _makeCropJson()..['end_date'] = null;
      final crop = CropProfitability.fromJson(json);
      expect(crop.endDate, isNull);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // SeasonSummary
  // ═══════════════════════════════════════════════════════════════════════════

  group('SeasonSummary', () {
    Map<String, dynamic> _makeCropJson(
        String id, double netProfit, double roi) {
      return {
        'profitability_id': id,
        'tenant_id': 't1',
        'field_id': 'f1',
        'field_name': 'F1',
        'crop_type': 'wheat',
        'crop_name': 'Wheat',
        'season': 'W25',
        'area': 5.0,
        'yield': 3.0,
        'total_yield': 15.0,
        'costs': <Map<String, dynamic>>[],
        'total_costs': 5000.0,
        'revenues': <Map<String, dynamic>>[],
        'total_revenue': 5000.0 + netProfit,
        'net_profit': netProfit,
        'profit_margin': 20.0,
        'roi': roi,
        'cost_per_hectare': 1000.0,
        'revenue_per_hectare': 1000.0 + netProfit / 5,
        'profit_per_hectare': netProfit / 5,
        'start_date': '2025-01-01T00:00:00.000',
        'created_at': '2025-01-01T00:00:00.000',
        'updated_at': '2025-06-01T00:00:00.000',
      };
    }

    Map<String, dynamic> _makeSummaryJson() {
      return {
        'summary_id': 'sum-001',
        'tenant_id': 't1',
        'farm_id': 'farm-001',
        'farm_name': 'Al-Rashid Farm',
        'farm_name_ar': 'مزرعة الرشيد',
        'season': 'Winter 2025',
        'season_ar': 'شتاء 2025',
        'fields_count': 3,
        'total_area': 25.0,
        'crops': [
          _makeCropJson('p1', 8000, 60),
          _makeCropJson('p2', 12000, 45),
          _makeCropJson('p3', 3000, 80),
        ],
        'total_revenue': 50000.0,
        'total_costs': 27000.0,
        'net_profit': 23000.0,
        'profit_margin': 46.0,
        'avg_roi': 61.67,
        'costs_by_category': {'seeds': 5000.0, 'fertilizer': 12000.0},
        'revenues_by_crop': {'wheat': 30000.0, 'barley': 20000.0},
        'start_date': '2025-01-01T00:00:00.000',
        'end_date': '2025-06-30T00:00:00.000',
        'created_at': '2025-07-01T00:00:00.000',
      };
    }

    test('fromJson creates correct instance', () {
      final summary = SeasonSummary.fromJson(_makeSummaryJson());
      expect(summary.summaryId, 'sum-001');
      expect(summary.fieldsCount, 3);
      expect(summary.crops.length, 3);
      expect(summary.totalRevenue, 50000.0);
    });

    test('toJson produces correct map', () {
      final summary = SeasonSummary.fromJson(_makeSummaryJson());
      final json = summary.toJson();
      expect(json['summary_id'], 'sum-001');
      expect(json['fields_count'], 3);
      expect(json['costs_by_category']['seeds'], 5000.0);
    });

    test('fromJson -> toJson round-trip', () {
      final summary = SeasonSummary.fromJson(_makeSummaryJson());
      final restored = SeasonSummary.fromJson(summary.toJson());
      expect(restored.summaryId, summary.summaryId);
      expect(restored.crops.length, summary.crops.length);
    });

    test('getTopCropsByProfit returns sorted descending', () {
      final summary = SeasonSummary.fromJson(_makeSummaryJson());
      final top = summary.getTopCropsByProfit();
      expect(top[0].netProfit, 12000);
      expect(top[1].netProfit, 8000);
      expect(top[2].netProfit, 3000);
    });

    test('getTopCropsByProfit respects limit', () {
      final summary = SeasonSummary.fromJson(_makeSummaryJson());
      final top = summary.getTopCropsByProfit(limit: 2);
      expect(top.length, 2);
      expect(top[0].netProfit, 12000);
    });

    test('getTopCropsByRoi returns sorted descending', () {
      final summary = SeasonSummary.fromJson(_makeSummaryJson());
      final top = summary.getTopCropsByRoi();
      expect(top[0].roi, 80);
      expect(top[1].roi, 60);
      expect(top[2].roi, 45);
    });

    test('getTopCropsByRoi respects limit', () {
      final summary = SeasonSummary.fromJson(_makeSummaryJson());
      final top = summary.getTopCropsByRoi(limit: 1);
      expect(top.length, 1);
      expect(top[0].roi, 80);
    });

    test('getFarmName locale support', () {
      final summary = SeasonSummary.fromJson(_makeSummaryJson());
      expect(summary.getFarmName('ar'), 'مزرعة الرشيد');
      expect(summary.getFarmName('en'), 'Al-Rashid Farm');
    });

    test('getSeason locale support', () {
      final summary = SeasonSummary.fromJson(_makeSummaryJson());
      expect(summary.getSeason('ar'), 'شتاء 2025');
      expect(summary.getSeason('en'), 'Winter 2025');
    });

    test('fromJson handles null endDate', () {
      final json = _makeSummaryJson()..['end_date'] = null;
      final summary = SeasonSummary.fromJson(json);
      expect(summary.endDate, isNull);
    });

    test('fromJson handles null costs_by_category', () {
      final json = _makeSummaryJson()..['costs_by_category'] = null;
      final summary = SeasonSummary.fromJson(json);
      expect(summary.costsByCategory, isEmpty);
    });

    test('fromJson handles null revenues_by_crop', () {
      final json = _makeSummaryJson()..['revenues_by_crop'] = null;
      final summary = SeasonSummary.fromJson(json);
      expect(summary.revenuesByCrop, isEmpty);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // ProfitabilityComparison
  // ═══════════════════════════════════════════════════════════════════════════

  group('ProfitabilityComparison', () {
    Map<String, dynamic> _makeComparisonJson() {
      return {
        'crops': <Map<String, dynamic>>[],
        'avg_yield_by_crop': {'wheat': 4.5, 'barley': 3.2},
        'avg_cost_by_crop': {'wheat': 6500.0, 'barley': 5000.0},
        'avg_revenue_by_crop': {'wheat': 16500.0, 'barley': 12000.0},
        'avg_profit_by_crop': {'wheat': 10000.0, 'barley': 7000.0},
        'avg_roi_by_crop': {'wheat': 153.8, 'barley': 140.0},
        'best_crop_by_profit': 'wheat',
        'best_crop_by_roi': 'wheat',
        'lowest_cost_crop': 'barley',
        'metadata': {'period': '2025'},
      };
    }

    test('fromJson creates correct instance', () {
      final comp = ProfitabilityComparison.fromJson(_makeComparisonJson());
      expect(comp.bestCropByProfit, 'wheat');
      expect(comp.bestCropByRoi, 'wheat');
      expect(comp.lowestCostCrop, 'barley');
      expect(comp.avgYieldByCrop['wheat'], 4.5);
    });

    test('toJson produces correct map', () {
      final comp = ProfitabilityComparison.fromJson(_makeComparisonJson());
      final json = comp.toJson();
      expect(json['best_crop_by_profit'], 'wheat');
      expect(json['lowest_cost_crop'], 'barley');
    });

    test('fromJson -> toJson round-trip', () {
      final comp = ProfitabilityComparison.fromJson(_makeComparisonJson());
      final restored = ProfitabilityComparison.fromJson(comp.toJson());
      expect(restored.avgYieldByCrop, comp.avgYieldByCrop);
      expect(restored.bestCropByProfit, comp.bestCropByProfit);
    });

    test('fromJson handles null maps', () {
      final json = <String, dynamic>{
        'crops': <Map<String, dynamic>>[],
        'avg_yield_by_crop': null,
        'avg_cost_by_crop': null,
        'avg_revenue_by_crop': null,
        'avg_profit_by_crop': null,
        'avg_roi_by_crop': null,
      };
      final comp = ProfitabilityComparison.fromJson(json);
      expect(comp.avgYieldByCrop, isEmpty);
      expect(comp.avgCostByCrop, isEmpty);
      expect(comp.avgRevenueByCrop, isEmpty);
      expect(comp.avgProfitByCrop, isEmpty);
      expect(comp.avgRoiByCrop, isEmpty);
    });

    test('fromJson handles null optional strings', () {
      final json = <String, dynamic>{
        'crops': <Map<String, dynamic>>[],
        'avg_yield_by_crop': null,
        'avg_cost_by_crop': null,
        'avg_revenue_by_crop': null,
        'avg_profit_by_crop': null,
        'avg_roi_by_crop': null,
        'best_crop_by_profit': null,
        'best_crop_by_roi': null,
        'lowest_cost_crop': null,
        'metadata': null,
      };
      final comp = ProfitabilityComparison.fromJson(json);
      expect(comp.bestCropByProfit, isNull);
      expect(comp.bestCropByRoi, isNull);
      expect(comp.lowestCostCrop, isNull);
      expect(comp.metadata, isNull);
    });
  });
}
