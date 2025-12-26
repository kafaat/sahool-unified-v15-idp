/// Inventory Providers - مزودات بيانات المخزون
/// Riverpod providers للتواصل مع Inventory Service
library;

import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/inventory_models.dart';
import '../data/inventory_repository.dart';

/// مزود قائمة عناصر المخزون
final inventoryItemsProvider = FutureProvider.autoDispose
    .family<List<InventoryItem>, InventoryFilter?>((ref, filter) async {
  final repo = ref.watch(inventoryRepositoryProvider);
  final result = await repo.getItems(
    category: filter?.category,
    search: filter?.search,
    lowStockOnly: filter?.lowStockOnly,
    expiringOnly: filter?.expiringOnly,
  );

  if (result.isSuccess) {
    return result.data ?? [];
  }
  throw Exception(result.errorAr ?? result.error ?? 'فشل في جلب عناصر المخزون');
});

/// مزود العناصر ذات المخزون المنخفض
final lowStockItemsProvider = FutureProvider.autoDispose<List<InventoryItem>>((ref) async {
  final repo = ref.watch(inventoryRepositoryProvider);
  final result = await repo.getLowStockItems();

  if (result.isSuccess) {
    return result.data ?? [];
  }
  throw Exception(result.errorAr ?? result.error ?? 'فشل في جلب العناصر ذات المخزون المنخفض');
});

/// مزود إحصائيات المخزون
final inventoryStatsProvider = FutureProvider.autoDispose<InventoryStats>((ref) async {
  final repo = ref.watch(inventoryRepositoryProvider);
  final result = await repo.getStats();

  if (result.isSuccess && result.data != null) {
    return result.data!;
  }
  throw Exception(result.errorAr ?? result.error ?? 'فشل في جلب الإحصائيات');
});

/// مزود تفاصيل عنصر محدد
final inventoryItemDetailsProvider = FutureProvider.autoDispose
    .family<InventoryItem, String>((ref, itemId) async {
  final repo = ref.watch(inventoryRepositoryProvider);
  final result = await repo.getItemById(itemId);

  if (result.isSuccess && result.data != null) {
    return result.data!;
  }
  throw Exception(result.errorAr ?? result.error ?? 'العنصر غير موجود');
});

/// مزود البحث عبر الباركود
final inventoryItemByBarcodeProvider = FutureProvider.autoDispose
    .family<InventoryItem, String>((ref, barcode) async {
  final repo = ref.watch(inventoryRepositoryProvider);
  final result = await repo.getItemByBarcode(barcode);

  if (result.isSuccess && result.data != null) {
    return result.data!;
  }
  throw Exception(result.errorAr ?? result.error ?? 'العنصر غير موجود');
});

/// مزود البحث عبر SKU
final inventoryItemBySkuProvider = FutureProvider.autoDispose
    .family<InventoryItem, String>((ref, sku) async {
  final repo = ref.watch(inventoryRepositoryProvider);
  final result = await repo.getItemBySku(sku);

  if (result.isSuccess && result.data != null) {
    return result.data!;
  }
  throw Exception(result.errorAr ?? result.error ?? 'العنصر غير موجود');
});

/// مزود حركات المخزون لعنصر
final stockMovementsProvider = FutureProvider.autoDispose
    .family<List<StockMovement>, String>((ref, itemId) async {
  final repo = ref.watch(inventoryRepositoryProvider);
  final result = await repo.getMovements(itemId);

  if (result.isSuccess) {
    return result.data ?? [];
  }
  throw Exception(result.errorAr ?? result.error ?? 'فشل في جلب حركات المخزون');
});

/// مزود المستودعات
final warehousesProvider = FutureProvider.autoDispose<List<Warehouse>>((ref) async {
  final repo = ref.watch(inventoryRepositoryProvider);
  final result = await repo.getWarehouses();

  if (result.isSuccess) {
    return result.data ?? [];
  }
  throw Exception(result.errorAr ?? result.error ?? 'فشل في جلب المستودعات');
});

/// مزود الموردين
final suppliersProvider = FutureProvider.autoDispose<List<Supplier>>((ref) async {
  final repo = ref.watch(inventoryRepositoryProvider);
  final result = await repo.getSuppliers();

  if (result.isSuccess) {
    return result.data ?? [];
  }
  throw Exception(result.errorAr ?? result.error ?? 'فشل في جلب الموردين');
});

/// حالة الفلتر المحددة
final selectedInventoryFilterProvider = StateProvider<InventoryFilter?>((ref) => null);

/// حالة عرض القائمة (grid/list)
final inventoryViewModeProvider = StateProvider<InventoryViewMode>((ref) => InventoryViewMode.grid);

/// فلتر المخزون
class InventoryFilter {
  final ItemCategory? category;
  final String? search;
  final bool? lowStockOnly;
  final bool? expiringOnly;

  const InventoryFilter({
    this.category,
    this.search,
    this.lowStockOnly,
    this.expiringOnly,
  });

  InventoryFilter copyWith({
    ItemCategory? category,
    String? search,
    bool? lowStockOnly,
    bool? expiringOnly,
    bool clearCategory = false,
    bool clearSearch = false,
    bool clearLowStockOnly = false,
    bool clearExpiringOnly = false,
  }) {
    return InventoryFilter(
      category: clearCategory ? null : (category ?? this.category),
      search: clearSearch ? null : (search ?? this.search),
      lowStockOnly: clearLowStockOnly ? null : (lowStockOnly ?? this.lowStockOnly),
      expiringOnly: clearExpiringOnly ? null : (expiringOnly ?? this.expiringOnly),
    );
  }

  bool get hasFilters =>
      category != null ||
      (search != null && search!.isNotEmpty) ||
      lowStockOnly == true ||
      expiringOnly == true;
}

/// وضع عرض القائمة
enum InventoryViewMode {
  grid,
  list,
}

/// Controller للعمليات (CRUD)
class InventoryController extends StateNotifier<AsyncValue<void>> {
  final InventoryRepository _repo;
  final Ref _ref;

  InventoryController(this._repo, this._ref) : super(const AsyncValue.data(null));

  /// إدخال مخزون
  Future<bool> stockIn({
    required String itemId,
    required double quantity,
    String? warehouseId,
    String? batchNumber,
    String? reference,
    String? notes,
    String? notesAr,
    DateTime? movementDate,
  }) async {
    state = const AsyncValue.loading();

    final result = await _repo.stockIn(
      itemId: itemId,
      quantity: quantity,
      warehouseId: warehouseId,
      batchNumber: batchNumber,
      reference: reference,
      notes: notes,
      notesAr: notesAr,
      movementDate: movementDate,
    );

    if (result.isSuccess) {
      state = const AsyncValue.data(null);
      // Invalidate related providers
      _ref.invalidate(inventoryItemsProvider);
      _ref.invalidate(inventoryItemDetailsProvider);
      _ref.invalidate(stockMovementsProvider);
      _ref.invalidate(inventoryStatsProvider);
      _ref.invalidate(lowStockItemsProvider);
      return true;
    }

    state = AsyncValue.error(
      result.errorAr ?? result.error ?? 'فشل في تسجيل إدخال المخزون',
      StackTrace.current,
    );
    return false;
  }

  /// إخراج مخزون
  Future<bool> stockOut({
    required String itemId,
    required double quantity,
    String? warehouseId,
    String? reference,
    String? notes,
    String? notesAr,
    DateTime? movementDate,
  }) async {
    state = const AsyncValue.loading();

    final result = await _repo.stockOut(
      itemId: itemId,
      quantity: quantity,
      warehouseId: warehouseId,
      reference: reference,
      notes: notes,
      notesAr: notesAr,
      movementDate: movementDate,
    );

    if (result.isSuccess) {
      state = const AsyncValue.data(null);
      _ref.invalidate(inventoryItemsProvider);
      _ref.invalidate(inventoryItemDetailsProvider);
      _ref.invalidate(stockMovementsProvider);
      _ref.invalidate(inventoryStatsProvider);
      _ref.invalidate(lowStockItemsProvider);
      return true;
    }

    state = AsyncValue.error(
      result.errorAr ?? result.error ?? 'فشل في تسجيل إخراج المخزون',
      StackTrace.current,
    );
    return false;
  }

  /// تطبيق على الحقل
  Future<bool> applyToField({
    required String itemId,
    required double quantity,
    required String fieldId,
    String? notes,
    String? notesAr,
    DateTime? movementDate,
  }) async {
    state = const AsyncValue.loading();

    final result = await _repo.applyToField(
      itemId: itemId,
      quantity: quantity,
      fieldId: fieldId,
      notes: notes,
      notesAr: notesAr,
      movementDate: movementDate,
    );

    if (result.isSuccess) {
      state = const AsyncValue.data(null);
      _ref.invalidate(inventoryItemsProvider);
      _ref.invalidate(inventoryItemDetailsProvider);
      _ref.invalidate(stockMovementsProvider);
      _ref.invalidate(inventoryStatsProvider);
      _ref.invalidate(lowStockItemsProvider);
      return true;
    }

    state = AsyncValue.error(
      result.errorAr ?? result.error ?? 'فشل في تسجيل التطبيق على الحقل',
      StackTrace.current,
    );
    return false;
  }

  /// تعديل المخزون
  Future<bool> adjustStock({
    required String itemId,
    required double quantity,
    String? notes,
    String? notesAr,
    DateTime? movementDate,
  }) async {
    state = const AsyncValue.loading();

    final result = await _repo.adjustStock(
      itemId: itemId,
      quantity: quantity,
      notes: notes,
      notesAr: notesAr,
      movementDate: movementDate,
    );

    if (result.isSuccess) {
      state = const AsyncValue.data(null);
      _ref.invalidate(inventoryItemsProvider);
      _ref.invalidate(inventoryItemDetailsProvider);
      _ref.invalidate(stockMovementsProvider);
      _ref.invalidate(inventoryStatsProvider);
      _ref.invalidate(lowStockItemsProvider);
      return true;
    }

    state = AsyncValue.error(
      result.errorAr ?? result.error ?? 'فشل في تعديل المخزون',
      StackTrace.current,
    );
    return false;
  }

  /// إنشاء عنصر جديد
  Future<bool> createItem({
    required String name,
    String? nameAr,
    String? sku,
    String? barcode,
    required ItemCategory category,
    required Unit unit,
    required double reorderLevel,
    required double maxCapacity,
    String? warehouseId,
    String? supplierId,
    double? unitPrice,
    String? batchNumber,
    String? lotNumber,
    DateTime? expiryDate,
    DateTime? manufactureDate,
    String? imageUrl,
    String? description,
    String? descriptionAr,
    Map<String, dynamic>? metadata,
  }) async {
    state = const AsyncValue.loading();

    final result = await _repo.createItem(
      name: name,
      nameAr: nameAr,
      sku: sku,
      barcode: barcode,
      category: category,
      unit: unit,
      reorderLevel: reorderLevel,
      maxCapacity: maxCapacity,
      warehouseId: warehouseId,
      supplierId: supplierId,
      unitPrice: unitPrice,
      batchNumber: batchNumber,
      lotNumber: lotNumber,
      expiryDate: expiryDate,
      manufactureDate: manufactureDate,
      imageUrl: imageUrl,
      description: description,
      descriptionAr: descriptionAr,
      metadata: metadata,
    );

    if (result.isSuccess) {
      state = const AsyncValue.data(null);
      _ref.invalidate(inventoryItemsProvider);
      _ref.invalidate(inventoryStatsProvider);
      return true;
    }

    state = AsyncValue.error(
      result.errorAr ?? result.error ?? 'فشل في إنشاء العنصر',
      StackTrace.current,
    );
    return false;
  }

  /// تحديث عنصر
  Future<bool> updateItem(
    String itemId,
    Map<String, dynamic> updates,
  ) async {
    state = const AsyncValue.loading();

    final result = await _repo.updateItem(itemId, updates);

    if (result.isSuccess) {
      state = const AsyncValue.data(null);
      _ref.invalidate(inventoryItemsProvider);
      _ref.invalidate(inventoryItemDetailsProvider);
      _ref.invalidate(inventoryStatsProvider);
      return true;
    }

    state = AsyncValue.error(
      result.errorAr ?? result.error ?? 'فشل في تحديث العنصر',
      StackTrace.current,
    );
    return false;
  }

  /// حذف عنصر
  Future<bool> deleteItem(String itemId) async {
    state = const AsyncValue.loading();

    final result = await _repo.deleteItem(itemId);

    if (result.isSuccess) {
      state = const AsyncValue.data(null);
      _ref.invalidate(inventoryItemsProvider);
      _ref.invalidate(inventoryStatsProvider);
      _ref.invalidate(lowStockItemsProvider);
      return true;
    }

    state = AsyncValue.error(
      result.errorAr ?? result.error ?? 'فشل في حذف العنصر',
      StackTrace.current,
    );
    return false;
  }
}

/// مزود Controller
final inventoryControllerProvider =
    StateNotifierProvider<InventoryController, AsyncValue<void>>((ref) {
  final repo = ref.watch(inventoryRepositoryProvider);
  return InventoryController(repo, ref);
});
