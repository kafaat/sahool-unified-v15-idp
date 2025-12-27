/// Inventory Models - نماذج المخزون
/// مطابقة لـ FastAPI Inventory Service
library;

import 'package:flutter/foundation.dart';

/// فئة المنتج
enum ItemCategory {
  fertilizer('fertilizer', 'أسمدة', 'Fertilizer'),
  pesticide('pesticide', 'مبيدات', 'Pesticide'),
  seed('seed', 'بذور', 'Seed'),
  equipment('equipment', 'معدات', 'Equipment'),
  tool('tool', 'أدوات', 'Tool'),
  chemical('chemical', 'كيماويات', 'Chemical'),
  feed('feed', 'أعلاف', 'Feed'),
  spare('spare', 'قطع غيار', 'Spare Parts'),
  other('other', 'أخرى', 'Other');

  final String value;
  final String nameAr;
  final String nameEn;

  const ItemCategory(this.value, this.nameAr, this.nameEn);

  String getName(String locale) => locale == 'ar' ? nameAr : nameEn;

  static ItemCategory fromString(String value) {
    return ItemCategory.values.firstWhere(
      (e) => e.value == value,
      orElse: () => ItemCategory.other,
    );
  }
}

/// وحدة القياس
enum Unit {
  kg('kg', 'كجم', 'Kilogram'),
  liter('liter', 'لتر', 'Liter'),
  piece('piece', 'قطعة', 'Piece'),
  bag('bag', 'كيس', 'Bag'),
  bottle('bottle', 'زجاجة', 'Bottle'),
  box('box', 'صندوق', 'Box'),
  ton('ton', 'طن', 'Ton'),
  gallon('gallon', 'جالون', 'Gallon'),
  meter('meter', 'متر', 'Meter');

  final String value;
  final String nameAr;
  final String nameEn;

  const Unit(this.value, this.nameAr, this.nameEn);

  String getName(String locale) => locale == 'ar' ? nameAr : nameEn;

  static Unit fromString(String value) {
    return Unit.values.firstWhere(
      (e) => e.value == value,
      orElse: () => Unit.piece,
    );
  }
}

/// نوع حركة المخزون
enum MovementType {
  stockIn('stock_in', 'إدخال', 'Stock In'),
  stockOut('stock_out', 'إخراج', 'Stock Out'),
  fieldApplication('field_application', 'استخدام في الحقل', 'Field Application'),
  adjustment('adjustment', 'تعديل', 'Adjustment'),
  damaged('damaged', 'تالف', 'Damaged'),
  expired('expired', 'منتهي الصلاحية', 'Expired'),
  transfer('transfer', 'نقل', 'Transfer'),
  returned('returned', 'مرتجع', 'Returned');

  final String value;
  final String nameAr;
  final String nameEn;

  const MovementType(this.value, this.nameAr, this.nameEn);

  String getName(String locale) => locale == 'ar' ? nameAr : nameEn;

  static MovementType fromString(String value) {
    return MovementType.values.firstWhere(
      (e) => e.value == value,
      orElse: () => MovementType.adjustment,
    );
  }
}

/// حالة المخزون
enum StockStatus {
  good('good', 'جيد', 'Good'),
  low('low', 'منخفض', 'Low'),
  critical('critical', 'حرج', 'Critical'),
  outOfStock('out_of_stock', 'نفد', 'Out of Stock'),
  expiring('expiring', 'قرب الانتهاء', 'Expiring Soon');

  final String value;
  final String nameAr;
  final String nameEn;

  const StockStatus(this.value, this.nameAr, this.nameEn);

  String getName(String locale) => locale == 'ar' ? nameAr : nameEn;

  static StockStatus fromString(String value) {
    return StockStatus.values.firstWhere(
      (e) => e.value == value,
      orElse: () => StockStatus.good,
    );
  }
}

// ═════════════════════════════════════════════════════════════════════════════
// Models
// ═════════════════════════════════════════════════════════════════════════════

/// نموذج عنصر المخزون
@immutable
class InventoryItem {
  final String itemId;
  final String tenantId;
  final String name;
  final String? nameAr;
  final String? sku;
  final String? barcode;
  final ItemCategory category;
  final Unit unit;
  final double currentStock;
  final double reorderLevel;
  final double maxCapacity;
  final String? warehouseId;
  final String? supplierId;
  final String? supplierName;
  final double? unitPrice;
  final String? batchNumber;
  final String? lotNumber;
  final DateTime? expiryDate;
  final DateTime? manufactureDate;
  final String? imageUrl;
  final String? description;
  final String? descriptionAr;
  final DateTime? lastStockIn;
  final DateTime? lastStockOut;
  final DateTime createdAt;
  final DateTime updatedAt;
  final Map<String, dynamic>? metadata;

  const InventoryItem({
    required this.itemId,
    required this.tenantId,
    required this.name,
    this.nameAr,
    this.sku,
    this.barcode,
    required this.category,
    required this.unit,
    required this.currentStock,
    required this.reorderLevel,
    required this.maxCapacity,
    this.warehouseId,
    this.supplierId,
    this.supplierName,
    this.unitPrice,
    this.batchNumber,
    this.lotNumber,
    this.expiryDate,
    this.manufactureDate,
    this.imageUrl,
    this.description,
    this.descriptionAr,
    this.lastStockIn,
    this.lastStockOut,
    required this.createdAt,
    required this.updatedAt,
    this.metadata,
  });

  /// Get display name based on locale
  String getDisplayName(String locale) {
    return locale == 'ar' && nameAr != null ? nameAr! : name;
  }

  /// Get description based on locale
  String? getDescription(String locale) {
    return locale == 'ar' && descriptionAr != null ? descriptionAr : description;
  }

  /// حساب حالة المخزون
  StockStatus get stockStatus {
    if (currentStock <= 0) return StockStatus.outOfStock;
    if (currentStock <= reorderLevel * 0.5) return StockStatus.critical;
    if (currentStock <= reorderLevel) return StockStatus.low;

    // تحقق من تاريخ الانتهاء
    if (expiryDate != null) {
      final daysUntilExpiry = expiryDate!.difference(DateTime.now()).inDays;
      if (daysUntilExpiry <= 30 && daysUntilExpiry > 0) {
        return StockStatus.expiring;
      }
    }

    return StockStatus.good;
  }

  /// هل المخزون منخفض؟
  bool get isLowStock => currentStock <= reorderLevel;

  /// هل المخزون حرج؟
  bool get isCritical => currentStock <= reorderLevel * 0.5;

  /// هل المخزون نفد؟
  bool get isOutOfStock => currentStock <= 0;

  /// هل قرب الانتهاء؟
  bool get isExpiringSoon {
    if (expiryDate == null) return false;
    final daysUntilExpiry = expiryDate!.difference(DateTime.now()).inDays;
    return daysUntilExpiry <= 30 && daysUntilExpiry > 0;
  }

  /// نسبة المخزون (0-1)
  double get stockPercentage {
    if (maxCapacity <= 0) return 0;
    return (currentStock / maxCapacity).clamp(0.0, 1.0);
  }

  /// الأيام حتى نفاد المخزون (تقدير)
  int? get daysUntilStockOut {
    // هذا تقدير بسيط - يمكن تحسينه باستخدام بيانات الاستهلاك التاريخية
    return null;
  }

  factory InventoryItem.fromJson(Map<String, dynamic> json) {
    return InventoryItem(
      itemId: json['item_id'] as String,
      tenantId: json['tenant_id'] as String,
      name: json['name'] as String,
      nameAr: json['name_ar'] as String?,
      sku: json['sku'] as String?,
      barcode: json['barcode'] as String?,
      category: ItemCategory.fromString(json['category'] as String),
      unit: Unit.fromString(json['unit'] as String),
      currentStock: (json['current_stock'] as num).toDouble(),
      reorderLevel: (json['reorder_level'] as num).toDouble(),
      maxCapacity: (json['max_capacity'] as num).toDouble(),
      warehouseId: json['warehouse_id'] as String?,
      supplierId: json['supplier_id'] as String?,
      supplierName: json['supplier_name'] as String?,
      unitPrice: (json['unit_price'] as num?)?.toDouble(),
      batchNumber: json['batch_number'] as String?,
      lotNumber: json['lot_number'] as String?,
      expiryDate: json['expiry_date'] != null
          ? DateTime.parse(json['expiry_date'] as String)
          : null,
      manufactureDate: json['manufacture_date'] != null
          ? DateTime.parse(json['manufacture_date'] as String)
          : null,
      imageUrl: json['image_url'] as String?,
      description: json['description'] as String?,
      descriptionAr: json['description_ar'] as String?,
      lastStockIn: json['last_stock_in'] != null
          ? DateTime.parse(json['last_stock_in'] as String)
          : null,
      lastStockOut: json['last_stock_out'] != null
          ? DateTime.parse(json['last_stock_out'] as String)
          : null,
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: DateTime.parse(json['updated_at'] as String),
      metadata: json['metadata'] as Map<String, dynamic>?,
    );
  }

  Map<String, dynamic> toJson() => {
        'item_id': itemId,
        'tenant_id': tenantId,
        'name': name,
        'name_ar': nameAr,
        'sku': sku,
        'barcode': barcode,
        'category': category.value,
        'unit': unit.value,
        'current_stock': currentStock,
        'reorder_level': reorderLevel,
        'max_capacity': maxCapacity,
        'warehouse_id': warehouseId,
        'supplier_id': supplierId,
        'supplier_name': supplierName,
        'unit_price': unitPrice,
        'batch_number': batchNumber,
        'lot_number': lotNumber,
        'expiry_date': expiryDate?.toIso8601String(),
        'manufacture_date': manufactureDate?.toIso8601String(),
        'image_url': imageUrl,
        'description': description,
        'description_ar': descriptionAr,
        'last_stock_in': lastStockIn?.toIso8601String(),
        'last_stock_out': lastStockOut?.toIso8601String(),
        'created_at': createdAt.toIso8601String(),
        'updated_at': updatedAt.toIso8601String(),
        'metadata': metadata,
      };
}

/// نموذج حركة المخزون
@immutable
class StockMovement {
  final String movementId;
  final String itemId;
  final String itemName;
  final MovementType movementType;
  final double quantity;
  final Unit unit;
  final double? previousStock;
  final double? newStock;
  final String? fieldId;
  final String? fieldName;
  final String? warehouseId;
  final String? userId;
  final String? userName;
  final String? notes;
  final String? notesAr;
  final String? batchNumber;
  final String? reference;
  final DateTime movementDate;
  final DateTime createdAt;
  final Map<String, dynamic>? metadata;

  const StockMovement({
    required this.movementId,
    required this.itemId,
    required this.itemName,
    required this.movementType,
    required this.quantity,
    required this.unit,
    this.previousStock,
    this.newStock,
    this.fieldId,
    this.fieldName,
    this.warehouseId,
    this.userId,
    this.userName,
    this.notes,
    this.notesAr,
    this.batchNumber,
    this.reference,
    required this.movementDate,
    required this.createdAt,
    this.metadata,
  });

  /// Get notes based on locale
  String? getNotes(String locale) {
    return locale == 'ar' && notesAr != null ? notesAr : notes;
  }

  /// هل الحركة إضافة للمخزون؟
  bool get isStockIncrease =>
      movementType == MovementType.stockIn ||
      movementType == MovementType.returned;

  /// هل الحركة خصم من المخزون؟
  bool get isStockDecrease =>
      movementType == MovementType.stockOut ||
      movementType == MovementType.fieldApplication ||
      movementType == MovementType.damaged ||
      movementType == MovementType.expired;

  factory StockMovement.fromJson(Map<String, dynamic> json) {
    return StockMovement(
      movementId: json['movement_id'] as String,
      itemId: json['item_id'] as String,
      itemName: json['item_name'] as String,
      movementType: MovementType.fromString(json['movement_type'] as String),
      quantity: (json['quantity'] as num).toDouble(),
      unit: Unit.fromString(json['unit'] as String),
      previousStock: (json['previous_stock'] as num?)?.toDouble(),
      newStock: (json['new_stock'] as num?)?.toDouble(),
      fieldId: json['field_id'] as String?,
      fieldName: json['field_name'] as String?,
      warehouseId: json['warehouse_id'] as String?,
      userId: json['user_id'] as String?,
      userName: json['user_name'] as String?,
      notes: json['notes'] as String?,
      notesAr: json['notes_ar'] as String?,
      batchNumber: json['batch_number'] as String?,
      reference: json['reference'] as String?,
      movementDate: DateTime.parse(json['movement_date'] as String),
      createdAt: DateTime.parse(json['created_at'] as String),
      metadata: json['metadata'] as Map<String, dynamic>?,
    );
  }

  Map<String, dynamic> toJson() => {
        'movement_id': movementId,
        'item_id': itemId,
        'item_name': itemName,
        'movement_type': movementType.value,
        'quantity': quantity,
        'unit': unit.value,
        'previous_stock': previousStock,
        'new_stock': newStock,
        'field_id': fieldId,
        'field_name': fieldName,
        'warehouse_id': warehouseId,
        'user_id': userId,
        'user_name': userName,
        'notes': notes,
        'notes_ar': notesAr,
        'batch_number': batchNumber,
        'reference': reference,
        'movement_date': movementDate.toIso8601String(),
        'created_at': createdAt.toIso8601String(),
        'metadata': metadata,
      };
}

/// نموذج المستودع
@immutable
class Warehouse {
  final String warehouseId;
  final String tenantId;
  final String name;
  final String? nameAr;
  final String? location;
  final double? latitude;
  final double? longitude;
  final double? capacity;
  final String? contactPerson;
  final String? contactPhone;
  final bool isActive;
  final DateTime createdAt;
  final DateTime updatedAt;
  final Map<String, dynamic>? metadata;

  const Warehouse({
    required this.warehouseId,
    required this.tenantId,
    required this.name,
    this.nameAr,
    this.location,
    this.latitude,
    this.longitude,
    this.capacity,
    this.contactPerson,
    this.contactPhone,
    required this.isActive,
    required this.createdAt,
    required this.updatedAt,
    this.metadata,
  });

  /// Get display name based on locale
  String getDisplayName(String locale) {
    return locale == 'ar' && nameAr != null ? nameAr! : name;
  }

  factory Warehouse.fromJson(Map<String, dynamic> json) {
    return Warehouse(
      warehouseId: json['warehouse_id'] as String,
      tenantId: json['tenant_id'] as String,
      name: json['name'] as String,
      nameAr: json['name_ar'] as String?,
      location: json['location'] as String?,
      latitude: (json['latitude'] as num?)?.toDouble(),
      longitude: (json['longitude'] as num?)?.toDouble(),
      capacity: (json['capacity'] as num?)?.toDouble(),
      contactPerson: json['contact_person'] as String?,
      contactPhone: json['contact_phone'] as String?,
      isActive: json['is_active'] as bool? ?? true,
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: DateTime.parse(json['updated_at'] as String),
      metadata: json['metadata'] as Map<String, dynamic>?,
    );
  }

  Map<String, dynamic> toJson() => {
        'warehouse_id': warehouseId,
        'tenant_id': tenantId,
        'name': name,
        'name_ar': nameAr,
        'location': location,
        'latitude': latitude,
        'longitude': longitude,
        'capacity': capacity,
        'contact_person': contactPerson,
        'contact_phone': contactPhone,
        'is_active': isActive,
        'created_at': createdAt.toIso8601String(),
        'updated_at': updatedAt.toIso8601String(),
        'metadata': metadata,
      };
}

/// نموذج المورد
@immutable
class Supplier {
  final String supplierId;
  final String tenantId;
  final String name;
  final String? nameAr;
  final String? contactPerson;
  final String? phone;
  final String? email;
  final String? address;
  final String? addressAr;
  final String? taxId;
  final String? licenseNumber;
  final bool isActive;
  final double? rating;
  final DateTime createdAt;
  final DateTime updatedAt;
  final Map<String, dynamic>? metadata;

  const Supplier({
    required this.supplierId,
    required this.tenantId,
    required this.name,
    this.nameAr,
    this.contactPerson,
    this.phone,
    this.email,
    this.address,
    this.addressAr,
    this.taxId,
    this.licenseNumber,
    required this.isActive,
    this.rating,
    required this.createdAt,
    required this.updatedAt,
    this.metadata,
  });

  /// Get display name based on locale
  String getDisplayName(String locale) {
    return locale == 'ar' && nameAr != null ? nameAr! : name;
  }

  /// Get address based on locale
  String? getAddress(String locale) {
    return locale == 'ar' && addressAr != null ? addressAr : address;
  }

  factory Supplier.fromJson(Map<String, dynamic> json) {
    return Supplier(
      supplierId: json['supplier_id'] as String,
      tenantId: json['tenant_id'] as String,
      name: json['name'] as String,
      nameAr: json['name_ar'] as String?,
      contactPerson: json['contact_person'] as String?,
      phone: json['phone'] as String?,
      email: json['email'] as String?,
      address: json['address'] as String?,
      addressAr: json['address_ar'] as String?,
      taxId: json['tax_id'] as String?,
      licenseNumber: json['license_number'] as String?,
      isActive: json['is_active'] as bool? ?? true,
      rating: (json['rating'] as num?)?.toDouble(),
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: DateTime.parse(json['updated_at'] as String),
      metadata: json['metadata'] as Map<String, dynamic>?,
    );
  }

  Map<String, dynamic> toJson() => {
        'supplier_id': supplierId,
        'tenant_id': tenantId,
        'name': name,
        'name_ar': nameAr,
        'contact_person': contactPerson,
        'phone': phone,
        'email': email,
        'address': address,
        'address_ar': addressAr,
        'tax_id': taxId,
        'license_number': licenseNumber,
        'is_active': isActive,
        'rating': rating,
        'created_at': createdAt.toIso8601String(),
        'updated_at': updatedAt.toIso8601String(),
        'metadata': metadata,
      };
}

/// إحصائيات المخزون
@immutable
class InventoryStats {
  final int totalItems;
  final int lowStockItems;
  final int outOfStockItems;
  final int expiringItems;
  final double totalValue;
  final Map<String, int> byCategory;

  const InventoryStats({
    required this.totalItems,
    required this.lowStockItems,
    required this.outOfStockItems,
    required this.expiringItems,
    required this.totalValue,
    required this.byCategory,
  });

  factory InventoryStats.fromJson(Map<String, dynamic> json) {
    return InventoryStats(
      totalItems: json['total_items'] as int,
      lowStockItems: json['low_stock_items'] as int,
      outOfStockItems: json['out_of_stock_items'] as int,
      expiringItems: json['expiring_items'] as int,
      totalValue: (json['total_value'] as num).toDouble(),
      byCategory: Map<String, int>.from(json['by_category'] as Map),
    );
  }
}
