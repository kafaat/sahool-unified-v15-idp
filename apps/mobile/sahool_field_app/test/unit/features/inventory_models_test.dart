import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/features/inventory/data/inventory_models.dart';

void main() {
  // ═══════════════════════════════════════════════════════════════════════════
  // ItemCategory enum
  // ═══════════════════════════════════════════════════════════════════════════
  group('ItemCategory', () {
    test('has exactly 9 values', () {
      expect(ItemCategory.values.length, 9);
    });

    test('fertilizer has correct properties', () {
      expect(ItemCategory.fertilizer.value, 'fertilizer');
      expect(ItemCategory.fertilizer.nameAr, 'أسمدة');
      expect(ItemCategory.fertilizer.nameEn, 'Fertilizer');
    });

    test('pesticide has correct properties', () {
      expect(ItemCategory.pesticide.value, 'pesticide');
      expect(ItemCategory.pesticide.nameAr, 'مبيدات');
    });

    test('seed has correct properties', () {
      expect(ItemCategory.seed.value, 'seed');
      expect(ItemCategory.seed.nameEn, 'Seed');
    });

    test('equipment has correct properties', () {
      expect(ItemCategory.equipment.value, 'equipment');
    });

    test('tool has correct properties', () {
      expect(ItemCategory.tool.value, 'tool');
      expect(ItemCategory.tool.nameAr, 'أدوات');
    });

    test('chemical has correct properties', () {
      expect(ItemCategory.chemical.value, 'chemical');
    });

    test('feed has correct properties', () {
      expect(ItemCategory.feed.value, 'feed');
      expect(ItemCategory.feed.nameAr, 'أعلاف');
    });

    test('spare has correct properties', () {
      expect(ItemCategory.spare.value, 'spare');
      expect(ItemCategory.spare.nameEn, 'Spare Parts');
    });

    test('other has correct properties', () {
      expect(ItemCategory.other.value, 'other');
      expect(ItemCategory.other.nameAr, 'أخرى');
    });

    test('getName returns Arabic for ar locale', () {
      expect(ItemCategory.fertilizer.getName('ar'), 'أسمدة');
    });

    test('getName returns English for en locale', () {
      expect(ItemCategory.fertilizer.getName('en'), 'Fertilizer');
    });

    test('fromString returns correct category', () {
      expect(ItemCategory.fromString('fertilizer'), ItemCategory.fertilizer);
      expect(ItemCategory.fromString('pesticide'), ItemCategory.pesticide);
      expect(ItemCategory.fromString('seed'), ItemCategory.seed);
      expect(ItemCategory.fromString('equipment'), ItemCategory.equipment);
      expect(ItemCategory.fromString('tool'), ItemCategory.tool);
      expect(ItemCategory.fromString('chemical'), ItemCategory.chemical);
      expect(ItemCategory.fromString('feed'), ItemCategory.feed);
      expect(ItemCategory.fromString('spare'), ItemCategory.spare);
      expect(ItemCategory.fromString('other'), ItemCategory.other);
    });

    test('fromString returns other for unknown value', () {
      expect(ItemCategory.fromString('unknown'), ItemCategory.other);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Unit enum
  // ═══════════════════════════════════════════════════════════════════════════
  group('Unit', () {
    test('has exactly 9 values', () {
      expect(Unit.values.length, 9);
    });

    test('kg has correct properties', () {
      expect(Unit.kg.value, 'kg');
      expect(Unit.kg.nameAr, 'كجم');
      expect(Unit.kg.nameEn, 'Kilogram');
    });

    test('liter has correct properties', () {
      expect(Unit.liter.value, 'liter');
      expect(Unit.liter.nameAr, 'لتر');
    });

    test('piece has correct properties', () {
      expect(Unit.piece.value, 'piece');
      expect(Unit.piece.nameAr, 'قطعة');
    });

    test('bag has correct properties', () {
      expect(Unit.bag.value, 'bag');
    });

    test('ton has correct properties', () {
      expect(Unit.ton.value, 'ton');
      expect(Unit.ton.nameAr, 'طن');
    });

    test('meter has correct properties', () {
      expect(Unit.meter.value, 'meter');
      expect(Unit.meter.nameAr, 'متر');
    });

    test('getName returns Arabic for ar locale', () {
      expect(Unit.kg.getName('ar'), 'كجم');
    });

    test('getName returns English for en locale', () {
      expect(Unit.kg.getName('en'), 'Kilogram');
    });

    test('fromString returns correct unit', () {
      expect(Unit.fromString('kg'), Unit.kg);
      expect(Unit.fromString('liter'), Unit.liter);
      expect(Unit.fromString('piece'), Unit.piece);
      expect(Unit.fromString('ton'), Unit.ton);
    });

    test('fromString returns piece for unknown value', () {
      expect(Unit.fromString('unknown'), Unit.piece);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // MovementType enum
  // ═══════════════════════════════════════════════════════════════════════════
  group('MovementType', () {
    test('has exactly 8 values', () {
      expect(MovementType.values.length, 8);
    });

    test('stockIn has correct properties', () {
      expect(MovementType.stockIn.value, 'stock_in');
      expect(MovementType.stockIn.nameAr, 'إدخال');
      expect(MovementType.stockIn.nameEn, 'Stock In');
    });

    test('stockOut has correct properties', () {
      expect(MovementType.stockOut.value, 'stock_out');
      expect(MovementType.stockOut.nameAr, 'إخراج');
    });

    test('fieldApplication has correct properties', () {
      expect(MovementType.fieldApplication.value, 'field_application');
      expect(MovementType.fieldApplication.nameAr, 'استخدام في الحقل');
    });

    test('damaged has correct properties', () {
      expect(MovementType.damaged.value, 'damaged');
    });

    test('expired has correct properties', () {
      expect(MovementType.expired.value, 'expired');
    });

    test('transfer has correct properties', () {
      expect(MovementType.transfer.value, 'transfer');
      expect(MovementType.transfer.nameAr, 'نقل');
    });

    test('returned has correct properties', () {
      expect(MovementType.returned.value, 'returned');
      expect(MovementType.returned.nameAr, 'مرتجع');
    });

    test('adjustment has correct properties', () {
      expect(MovementType.adjustment.value, 'adjustment');
      expect(MovementType.adjustment.nameAr, 'تعديل');
    });

    test('fromString returns correct type', () {
      expect(
          MovementType.fromString('stock_in'), MovementType.stockIn);
      expect(
          MovementType.fromString('stock_out'), MovementType.stockOut);
      expect(MovementType.fromString('field_application'),
          MovementType.fieldApplication);
      expect(MovementType.fromString('returned'), MovementType.returned);
    });

    test('fromString returns adjustment for unknown value', () {
      expect(MovementType.fromString('unknown'), MovementType.adjustment);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // StockStatus enum
  // ═══════════════════════════════════════════════════════════════════════════
  group('StockStatus', () {
    test('has exactly 5 values', () {
      expect(StockStatus.values.length, 5);
    });

    test('good has correct properties', () {
      expect(StockStatus.good.value, 'good');
      expect(StockStatus.good.nameAr, 'جيد');
      expect(StockStatus.good.nameEn, 'Good');
    });

    test('low has correct properties', () {
      expect(StockStatus.low.value, 'low');
      expect(StockStatus.low.nameAr, 'منخفض');
    });

    test('critical has correct properties', () {
      expect(StockStatus.critical.value, 'critical');
      expect(StockStatus.critical.nameAr, 'حرج');
    });

    test('outOfStock has correct properties', () {
      expect(StockStatus.outOfStock.value, 'out_of_stock');
      expect(StockStatus.outOfStock.nameAr, 'نفد');
    });

    test('expiring has correct properties', () {
      expect(StockStatus.expiring.value, 'expiring');
      expect(StockStatus.expiring.nameAr, 'قرب الانتهاء');
    });

    test('fromString returns correct status', () {
      expect(StockStatus.fromString('good'), StockStatus.good);
      expect(StockStatus.fromString('low'), StockStatus.low);
      expect(StockStatus.fromString('critical'), StockStatus.critical);
      expect(
          StockStatus.fromString('out_of_stock'), StockStatus.outOfStock);
      expect(StockStatus.fromString('expiring'), StockStatus.expiring);
    });

    test('fromString returns good for unknown value', () {
      expect(StockStatus.fromString('unknown'), StockStatus.good);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // InventoryItem
  // ═══════════════════════════════════════════════════════════════════════════
  group('InventoryItem', () {
    Map<String, dynamic> makeItemJson({
      double currentStock = 100.0,
      double reorderLevel = 20.0,
      double maxCapacity = 200.0,
      String? expiryDate,
    }) =>
        {
          'item_id': 'item-1',
          'tenant_id': 't1',
          'name': 'Urea 46%',
          'name_ar': 'يوريا 46%',
          'sku': 'SKU-001',
          'barcode': '1234567890',
          'category': 'fertilizer',
          'unit': 'kg',
          'current_stock': currentStock,
          'reorder_level': reorderLevel,
          'max_capacity': maxCapacity,
          'warehouse_id': 'w1',
          'supplier_id': 's1',
          'supplier_name': 'AgriCo',
          'unit_price': 15.0,
          'batch_number': 'B001',
          'lot_number': 'L001',
          if (expiryDate != null) 'expiry_date': expiryDate,
          'manufacture_date': '2025-01-01T00:00:00.000Z',
          'image_url': 'https://example.com/urea.jpg',
          'description': 'Nitrogen fertilizer',
          'description_ar': 'سماد نيتروجيني',
          'last_stock_in': '2025-03-01T00:00:00.000Z',
          'last_stock_out': '2025-03-10T00:00:00.000Z',
          'created_at': '2025-01-01T00:00:00.000Z',
          'updated_at': '2025-03-10T00:00:00.000Z',
          'metadata': {'grade': 'A'},
        };

    test('fromJson creates correct instance', () {
      final item = InventoryItem.fromJson(makeItemJson());
      expect(item.itemId, 'item-1');
      expect(item.tenantId, 't1');
      expect(item.name, 'Urea 46%');
      expect(item.nameAr, 'يوريا 46%');
      expect(item.sku, 'SKU-001');
      expect(item.barcode, '1234567890');
      expect(item.category, ItemCategory.fertilizer);
      expect(item.unit, Unit.kg);
      expect(item.currentStock, 100.0);
      expect(item.reorderLevel, 20.0);
      expect(item.maxCapacity, 200.0);
      expect(item.unitPrice, 15.0);
    });

    test('stockStatus returns outOfStock when stock is 0', () {
      final item = InventoryItem.fromJson(makeItemJson(currentStock: 0));
      expect(item.stockStatus, StockStatus.outOfStock);
    });

    test('stockStatus returns outOfStock when stock is negative', () {
      final item = InventoryItem.fromJson(makeItemJson(currentStock: -5));
      expect(item.stockStatus, StockStatus.outOfStock);
    });

    test('stockStatus returns critical when stock <= reorderLevel * 0.5', () {
      // reorderLevel=20, 0.5*20=10, stock=10 => critical
      final item = InventoryItem.fromJson(
          makeItemJson(currentStock: 10, reorderLevel: 20));
      expect(item.stockStatus, StockStatus.critical);
    });

    test('stockStatus returns critical when stock is 5 with reorderLevel 20',
        () {
      final item = InventoryItem.fromJson(
          makeItemJson(currentStock: 5, reorderLevel: 20));
      expect(item.stockStatus, StockStatus.critical);
    });

    test('stockStatus returns low when stock <= reorderLevel', () {
      // reorderLevel=20, stock=15 (> 10 but <= 20) => low
      final item = InventoryItem.fromJson(
          makeItemJson(currentStock: 15, reorderLevel: 20));
      expect(item.stockStatus, StockStatus.low);
    });

    test('stockStatus returns low when stock equals reorderLevel', () {
      final item = InventoryItem.fromJson(
          makeItemJson(currentStock: 20, reorderLevel: 20));
      expect(item.stockStatus, StockStatus.low);
    });

    test('stockStatus returns good when stock is above reorderLevel', () {
      final item = InventoryItem.fromJson(
          makeItemJson(currentStock: 100, reorderLevel: 20));
      expect(item.stockStatus, StockStatus.good);
    });

    test('stockStatus returns expiring when expiry is within 30 days', () {
      final expiry =
          DateTime.now().add(const Duration(days: 15)).toIso8601String();
      final item = InventoryItem.fromJson(
          makeItemJson(currentStock: 100, expiryDate: expiry));
      expect(item.stockStatus, StockStatus.expiring);
    });

    test('stockStatus returns good when expiry is more than 30 days away', () {
      final expiry =
          DateTime.now().add(const Duration(days: 60)).toIso8601String();
      final item = InventoryItem.fromJson(
          makeItemJson(currentStock: 100, expiryDate: expiry));
      expect(item.stockStatus, StockStatus.good);
    });

    test('isLowStock returns true when at reorderLevel', () {
      final item = InventoryItem.fromJson(
          makeItemJson(currentStock: 20, reorderLevel: 20));
      expect(item.isLowStock, true);
    });

    test('isLowStock returns true when below reorderLevel', () {
      final item = InventoryItem.fromJson(
          makeItemJson(currentStock: 10, reorderLevel: 20));
      expect(item.isLowStock, true);
    });

    test('isLowStock returns false when above reorderLevel', () {
      final item = InventoryItem.fromJson(
          makeItemJson(currentStock: 50, reorderLevel: 20));
      expect(item.isLowStock, false);
    });

    test('isCritical returns true when at half reorderLevel', () {
      final item = InventoryItem.fromJson(
          makeItemJson(currentStock: 10, reorderLevel: 20));
      expect(item.isCritical, true);
    });

    test('isCritical returns true when below half reorderLevel', () {
      final item = InventoryItem.fromJson(
          makeItemJson(currentStock: 5, reorderLevel: 20));
      expect(item.isCritical, true);
    });

    test('isCritical returns false when above half reorderLevel', () {
      final item = InventoryItem.fromJson(
          makeItemJson(currentStock: 15, reorderLevel: 20));
      expect(item.isCritical, false);
    });

    test('isOutOfStock returns true when stock is 0', () {
      final item = InventoryItem.fromJson(makeItemJson(currentStock: 0));
      expect(item.isOutOfStock, true);
    });

    test('isOutOfStock returns true when stock is negative', () {
      final item = InventoryItem.fromJson(makeItemJson(currentStock: -1));
      expect(item.isOutOfStock, true);
    });

    test('isOutOfStock returns false when stock is positive', () {
      final item = InventoryItem.fromJson(makeItemJson(currentStock: 1));
      expect(item.isOutOfStock, false);
    });

    test('isExpiringSoon returns false when expiryDate is null', () {
      final item = InventoryItem.fromJson(makeItemJson());
      expect(item.isExpiringSoon, false);
    });

    test('isExpiringSoon returns true when within 30 days', () {
      final expiry =
          DateTime.now().add(const Duration(days: 10)).toIso8601String();
      final item = InventoryItem.fromJson(makeItemJson(expiryDate: expiry));
      expect(item.isExpiringSoon, true);
    });

    test('isExpiringSoon returns false when more than 30 days', () {
      final expiry =
          DateTime.now().add(const Duration(days: 60)).toIso8601String();
      final item = InventoryItem.fromJson(makeItemJson(expiryDate: expiry));
      expect(item.isExpiringSoon, false);
    });

    test('isExpiringSoon returns false when already expired', () {
      final expiry =
          DateTime.now().subtract(const Duration(days: 5)).toIso8601String();
      final item = InventoryItem.fromJson(makeItemJson(expiryDate: expiry));
      expect(item.isExpiringSoon, false);
    });

    test('stockPercentage calculates correctly', () {
      final item = InventoryItem.fromJson(
          makeItemJson(currentStock: 100, maxCapacity: 200));
      expect(item.stockPercentage, 0.5);
    });

    test('stockPercentage clamps to 1.0 when over capacity', () {
      final item = InventoryItem.fromJson(
          makeItemJson(currentStock: 300, maxCapacity: 200));
      expect(item.stockPercentage, 1.0);
    });

    test('stockPercentage clamps to 0.0 when negative stock', () {
      final item = InventoryItem.fromJson(
          makeItemJson(currentStock: -10, maxCapacity: 200));
      expect(item.stockPercentage, 0.0);
    });

    test('stockPercentage returns 0 when maxCapacity is 0', () {
      final item = InventoryItem.fromJson(
          makeItemJson(currentStock: 50, maxCapacity: 0));
      expect(item.stockPercentage, 0);
    });

    test('getDisplayName returns Arabic for ar locale', () {
      final item = InventoryItem.fromJson(makeItemJson());
      expect(item.getDisplayName('ar'), 'يوريا 46%');
    });

    test('getDisplayName returns English for en locale', () {
      final item = InventoryItem.fromJson(makeItemJson());
      expect(item.getDisplayName('en'), 'Urea 46%');
    });

    test('getDescription returns Arabic for ar locale', () {
      final item = InventoryItem.fromJson(makeItemJson());
      expect(item.getDescription('ar'), 'سماد نيتروجيني');
    });

    test('getDescription returns English for en locale', () {
      final item = InventoryItem.fromJson(makeItemJson());
      expect(item.getDescription('en'), 'Nitrogen fertilizer');
    });

    test('toJson produces correct map', () {
      final item = InventoryItem.fromJson(makeItemJson());
      final json = item.toJson();
      expect(json['item_id'], 'item-1');
      expect(json['category'], 'fertilizer');
      expect(json['unit'], 'kg');
      expect(json['current_stock'], 100.0);
    });

    test('fromJson/toJson roundtrip preserves data', () {
      final item = InventoryItem.fromJson(makeItemJson());
      final json = item.toJson();
      final restored = InventoryItem.fromJson(json);
      expect(restored.itemId, item.itemId);
      expect(restored.category, item.category);
      expect(restored.currentStock, item.currentStock);
      expect(restored.unitPrice, item.unitPrice);
    });

    test('daysUntilStockOut returns null', () {
      final item = InventoryItem.fromJson(makeItemJson());
      expect(item.daysUntilStockOut, isNull);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // StockMovement
  // ═══════════════════════════════════════════════════════════════════════════
  group('StockMovement', () {
    Map<String, dynamic> makeMovementJson({String movementType = 'stock_in'}) =>
        {
          'movement_id': 'm1',
          'item_id': 'item-1',
          'item_name': 'Urea',
          'movement_type': movementType,
          'quantity': 50.0,
          'unit': 'kg',
          'previous_stock': 100.0,
          'new_stock': 150.0,
          'field_id': 'f1',
          'field_name': 'Field 1',
          'warehouse_id': 'w1',
          'user_id': 'u1',
          'user_name': 'John',
          'notes': 'Monthly delivery',
          'notes_ar': 'توصيل شهري',
          'batch_number': 'B001',
          'reference': 'REF-001',
          'movement_date': '2025-03-15T00:00:00.000Z',
          'created_at': '2025-03-15T10:00:00.000Z',
          'metadata': {'order_id': 'ORD-001'},
        };

    test('fromJson creates correct instance', () {
      final m = StockMovement.fromJson(makeMovementJson());
      expect(m.movementId, 'm1');
      expect(m.itemId, 'item-1');
      expect(m.itemName, 'Urea');
      expect(m.movementType, MovementType.stockIn);
      expect(m.quantity, 50.0);
      expect(m.unit, Unit.kg);
      expect(m.previousStock, 100.0);
      expect(m.newStock, 150.0);
    });

    test('isStockIncrease returns true for stockIn', () {
      final m = StockMovement.fromJson(
          makeMovementJson(movementType: 'stock_in'));
      expect(m.isStockIncrease, true);
    });

    test('isStockIncrease returns true for returned', () {
      final m = StockMovement.fromJson(
          makeMovementJson(movementType: 'returned'));
      expect(m.isStockIncrease, true);
    });

    test('isStockIncrease returns false for stock_out', () {
      final m = StockMovement.fromJson(
          makeMovementJson(movementType: 'stock_out'));
      expect(m.isStockIncrease, false);
    });

    test('isStockIncrease returns false for field_application', () {
      final m = StockMovement.fromJson(
          makeMovementJson(movementType: 'field_application'));
      expect(m.isStockIncrease, false);
    });

    test('isStockIncrease returns false for damaged', () {
      final m = StockMovement.fromJson(
          makeMovementJson(movementType: 'damaged'));
      expect(m.isStockIncrease, false);
    });

    test('isStockDecrease returns true for stock_out', () {
      final m = StockMovement.fromJson(
          makeMovementJson(movementType: 'stock_out'));
      expect(m.isStockDecrease, true);
    });

    test('isStockDecrease returns true for field_application', () {
      final m = StockMovement.fromJson(
          makeMovementJson(movementType: 'field_application'));
      expect(m.isStockDecrease, true);
    });

    test('isStockDecrease returns true for damaged', () {
      final m = StockMovement.fromJson(
          makeMovementJson(movementType: 'damaged'));
      expect(m.isStockDecrease, true);
    });

    test('isStockDecrease returns true for expired', () {
      final m = StockMovement.fromJson(
          makeMovementJson(movementType: 'expired'));
      expect(m.isStockDecrease, true);
    });

    test('isStockDecrease returns false for stock_in', () {
      final m = StockMovement.fromJson(
          makeMovementJson(movementType: 'stock_in'));
      expect(m.isStockDecrease, false);
    });

    test('isStockDecrease returns false for returned', () {
      final m = StockMovement.fromJson(
          makeMovementJson(movementType: 'returned'));
      expect(m.isStockDecrease, false);
    });

    test('isStockDecrease returns false for transfer', () {
      final m = StockMovement.fromJson(
          makeMovementJson(movementType: 'transfer'));
      expect(m.isStockDecrease, false);
    });

    test('isStockDecrease returns false for adjustment', () {
      final m = StockMovement.fromJson(
          makeMovementJson(movementType: 'adjustment'));
      expect(m.isStockDecrease, false);
    });

    test('getNotes returns Arabic for ar locale', () {
      final m = StockMovement.fromJson(makeMovementJson());
      expect(m.getNotes('ar'), 'توصيل شهري');
    });

    test('getNotes returns English for en locale', () {
      final m = StockMovement.fromJson(makeMovementJson());
      expect(m.getNotes('en'), 'Monthly delivery');
    });

    test('toJson produces correct map', () {
      final m = StockMovement.fromJson(makeMovementJson());
      final json = m.toJson();
      expect(json['movement_id'], 'm1');
      expect(json['movement_type'], 'stock_in');
      expect(json['quantity'], 50.0);
      expect(json['unit'], 'kg');
    });

    test('fromJson/toJson roundtrip preserves data', () {
      final m = StockMovement.fromJson(makeMovementJson());
      final json = m.toJson();
      final restored = StockMovement.fromJson(json);
      expect(restored.movementId, m.movementId);
      expect(restored.movementType, m.movementType);
      expect(restored.quantity, m.quantity);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Warehouse
  // ═══════════════════════════════════════════════════════════════════════════
  group('Warehouse', () {
    Map<String, dynamic> makeWarehouseJson() => {
          'warehouse_id': 'w1',
          'tenant_id': 't1',
          'name': 'Main Warehouse',
          'name_ar': 'المستودع الرئيسي',
          'location': 'Sanaa',
          'latitude': 15.369,
          'longitude': 44.191,
          'capacity': 1000.0,
          'contact_person': 'Ahmed',
          'contact_phone': '+967123456789',
          'is_active': true,
          'created_at': '2025-01-01T00:00:00.000Z',
          'updated_at': '2025-01-01T00:00:00.000Z',
          'metadata': {'type': 'cold_storage'},
        };

    test('fromJson creates correct instance', () {
      final w = Warehouse.fromJson(makeWarehouseJson());
      expect(w.warehouseId, 'w1');
      expect(w.tenantId, 't1');
      expect(w.name, 'Main Warehouse');
      expect(w.nameAr, 'المستودع الرئيسي');
      expect(w.latitude, 15.369);
      expect(w.longitude, 44.191);
      expect(w.capacity, 1000.0);
      expect(w.isActive, true);
    });

    test('getDisplayName returns Arabic for ar locale', () {
      final w = Warehouse.fromJson(makeWarehouseJson());
      expect(w.getDisplayName('ar'), 'المستودع الرئيسي');
    });

    test('getDisplayName returns English for en locale', () {
      final w = Warehouse.fromJson(makeWarehouseJson());
      expect(w.getDisplayName('en'), 'Main Warehouse');
    });

    test('isActive defaults to true when missing', () {
      final json = makeWarehouseJson();
      json.remove('is_active');
      final w = Warehouse.fromJson(json);
      expect(w.isActive, true);
    });

    test('toJson produces correct map', () {
      final w = Warehouse.fromJson(makeWarehouseJson());
      final json = w.toJson();
      expect(json['warehouse_id'], 'w1');
      expect(json['is_active'], true);
      expect(json['capacity'], 1000.0);
    });

    test('fromJson/toJson roundtrip', () {
      final w = Warehouse.fromJson(makeWarehouseJson());
      final restored = Warehouse.fromJson(w.toJson());
      expect(restored.warehouseId, w.warehouseId);
      expect(restored.name, w.name);
      expect(restored.latitude, w.latitude);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Supplier
  // ═══════════════════════════════════════════════════════════════════════════
  group('Supplier', () {
    Map<String, dynamic> makeSupplierJson() => {
          'supplier_id': 's1',
          'tenant_id': 't1',
          'name': 'AgriCo',
          'name_ar': 'أجريكو',
          'contact_person': 'Ali',
          'phone': '+967111222333',
          'email': 'ali@agrico.com',
          'address': 'Sanaa, Yemen',
          'address_ar': 'صنعاء، اليمن',
          'tax_id': 'TAX-001',
          'license_number': 'LIC-001',
          'is_active': true,
          'rating': 4.5,
          'created_at': '2025-01-01T00:00:00.000Z',
          'updated_at': '2025-01-01T00:00:00.000Z',
          'metadata': {'tier': 'gold'},
        };

    test('fromJson creates correct instance', () {
      final s = Supplier.fromJson(makeSupplierJson());
      expect(s.supplierId, 's1');
      expect(s.name, 'AgriCo');
      expect(s.nameAr, 'أجريكو');
      expect(s.rating, 4.5);
      expect(s.isActive, true);
      expect(s.taxId, 'TAX-001');
    });

    test('getDisplayName returns Arabic for ar locale', () {
      final s = Supplier.fromJson(makeSupplierJson());
      expect(s.getDisplayName('ar'), 'أجريكو');
    });

    test('getDisplayName returns English for en locale', () {
      final s = Supplier.fromJson(makeSupplierJson());
      expect(s.getDisplayName('en'), 'AgriCo');
    });

    test('getAddress returns Arabic for ar locale', () {
      final s = Supplier.fromJson(makeSupplierJson());
      expect(s.getAddress('ar'), 'صنعاء، اليمن');
    });

    test('getAddress returns English for en locale', () {
      final s = Supplier.fromJson(makeSupplierJson());
      expect(s.getAddress('en'), 'Sanaa, Yemen');
    });

    test('isActive defaults to true when missing', () {
      final json = makeSupplierJson();
      json.remove('is_active');
      final s = Supplier.fromJson(json);
      expect(s.isActive, true);
    });

    test('toJson produces correct map', () {
      final s = Supplier.fromJson(makeSupplierJson());
      final json = s.toJson();
      expect(json['supplier_id'], 's1');
      expect(json['rating'], 4.5);
      expect(json['is_active'], true);
    });

    test('fromJson/toJson roundtrip', () {
      final s = Supplier.fromJson(makeSupplierJson());
      final restored = Supplier.fromJson(s.toJson());
      expect(restored.supplierId, s.supplierId);
      expect(restored.name, s.name);
      expect(restored.rating, s.rating);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // InventoryStats
  // ═══════════════════════════════════════════════════════════════════════════
  group('InventoryStats', () {
    test('fromJson creates correct instance', () {
      final json = {
        'total_items': 150,
        'low_stock_items': 12,
        'out_of_stock_items': 3,
        'expiring_items': 5,
        'total_value': 125000.0,
        'by_category': {'fertilizer': 50, 'pesticide': 30, 'seed': 70},
      };
      final stats = InventoryStats.fromJson(json);
      expect(stats.totalItems, 150);
      expect(stats.lowStockItems, 12);
      expect(stats.outOfStockItems, 3);
      expect(stats.expiringItems, 5);
      expect(stats.totalValue, 125000.0);
      expect(stats.byCategory['fertilizer'], 50);
      expect(stats.byCategory['pesticide'], 30);
      expect(stats.byCategory['seed'], 70);
    });

    test('fromJson handles empty byCategory map', () {
      final json = {
        'total_items': 0,
        'low_stock_items': 0,
        'out_of_stock_items': 0,
        'expiring_items': 0,
        'total_value': 0.0,
        'by_category': <String, int>{},
      };
      final stats = InventoryStats.fromJson(json);
      expect(stats.totalItems, 0);
      expect(stats.byCategory, isEmpty);
    });

    test('fromJson handles integer totalValue', () {
      final json = {
        'total_items': 10,
        'low_stock_items': 1,
        'out_of_stock_items': 0,
        'expiring_items': 0,
        'total_value': 5000,
        'by_category': {'other': 10},
      };
      final stats = InventoryStats.fromJson(json);
      expect(stats.totalValue, 5000.0);
    });
  });
}
