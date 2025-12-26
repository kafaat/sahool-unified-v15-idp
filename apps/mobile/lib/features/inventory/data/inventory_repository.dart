/// Inventory Repository - مستودع بيانات المخزون
/// يتواصل مع FastAPI Inventory Service
library;

import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/config/api_config.dart';
import 'inventory_models.dart';

/// Inventory Repository Provider
final inventoryRepositoryProvider = Provider<InventoryRepository>((ref) {
  return InventoryRepository();
});

/// نتيجة API
class ApiResult<T> {
  final T? data;
  final String? error;
  final String? errorAr;
  final bool isSuccess;

  const ApiResult._({this.data, this.error, this.errorAr, required this.isSuccess});

  factory ApiResult.success(T data) => ApiResult._(data: data, isSuccess: true);
  factory ApiResult.failure(String error, [String? errorAr]) =>
      ApiResult._(error: error, errorAr: errorAr, isSuccess: false);
}

/// Inventory Repository
class InventoryRepository {
  final Dio _dio;

  InventoryRepository({Dio? dio})
      : _dio = dio ??
            Dio(BaseOptions(
              baseUrl: ApiConfig.inventoryServiceUrl,
              connectTimeout: ApiConfig.connectTimeout,
              sendTimeout: ApiConfig.sendTimeout,
              receiveTimeout: ApiConfig.receiveTimeout,
              headers: ApiConfig.defaultHeaders,
            ));

  // ─────────────────────────────────────────────────────────────────────────────
  // Inventory Items CRUD
  // ─────────────────────────────────────────────────────────────────────────────

  /// جلب جميع العناصر
  Future<ApiResult<List<InventoryItem>>> getItems({
    ItemCategory? category,
    String? search,
    bool? lowStockOnly,
    bool? expiringOnly,
    int limit = 50,
    int offset = 0,
  }) async {
    try {
      final queryParams = <String, dynamic>{
        'limit': limit,
        'offset': offset,
      };
      if (category != null) queryParams['category'] = category.value;
      if (search != null && search.isNotEmpty) queryParams['search'] = search;
      if (lowStockOnly != null) queryParams['low_stock_only'] = lowStockOnly;
      if (expiringOnly != null) queryParams['expiring_only'] = expiringOnly;

      final response = await _dio.get(
        '/v1/inventory/items',
        queryParameters: queryParams,
      );

      final data = response.data as Map<String, dynamic>;
      final items = (data['items'] as List)
          .map((e) => InventoryItem.fromJson(e as Map<String, dynamic>))
          .toList();

      return ApiResult.success(items);
    } on DioException catch (e) {
      return ApiResult.failure(
        e.message ?? 'Failed to fetch inventory items',
        'فشل في جلب عناصر المخزون',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// جلب عنصر محدد
  Future<ApiResult<InventoryItem>> getItemById(String itemId) async {
    try {
      final response = await _dio.get('/v1/inventory/items/$itemId');
      return ApiResult.success(
        InventoryItem.fromJson(response.data as Map<String, dynamic>),
      );
    } on DioException catch (e) {
      if (e.response?.statusCode == 404) {
        return ApiResult.failure('Item not found', 'العنصر غير موجود');
      }
      return ApiResult.failure(
        e.message ?? 'Failed to fetch item',
        'فشل في جلب العنصر',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// جلب عنصر عبر الباركود
  Future<ApiResult<InventoryItem>> getItemByBarcode(String barcode) async {
    try {
      final response = await _dio.get('/v1/inventory/items/barcode/$barcode');
      return ApiResult.success(
        InventoryItem.fromJson(response.data as Map<String, dynamic>),
      );
    } on DioException catch (e) {
      if (e.response?.statusCode == 404) {
        return ApiResult.failure('Item not found', 'العنصر غير موجود');
      }
      return ApiResult.failure(
        e.message ?? 'Failed to fetch item',
        'فشل في جلب العنصر',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// جلب عنصر عبر SKU
  Future<ApiResult<InventoryItem>> getItemBySku(String sku) async {
    try {
      final response = await _dio.get('/v1/inventory/items/sku/$sku');
      return ApiResult.success(
        InventoryItem.fromJson(response.data as Map<String, dynamic>),
      );
    } on DioException catch (e) {
      if (e.response?.statusCode == 404) {
        return ApiResult.failure('Item not found', 'العنصر غير موجود');
      }
      return ApiResult.failure(
        e.message ?? 'Failed to fetch item',
        'فشل في جلب العنصر',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// جلب العناصر ذات المخزون المنخفض
  Future<ApiResult<List<InventoryItem>>> getLowStockItems() async {
    try {
      final response = await _dio.get('/v1/inventory/items/low-stock');

      final data = response.data as Map<String, dynamic>;
      final items = (data['items'] as List)
          .map((e) => InventoryItem.fromJson(e as Map<String, dynamic>))
          .toList();

      return ApiResult.success(items);
    } on DioException catch (e) {
      return ApiResult.failure(
        e.message ?? 'Failed to fetch low stock items',
        'فشل في جلب العناصر ذات المخزون المنخفض',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// إنشاء عنصر جديد
  Future<ApiResult<InventoryItem>> createItem({
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
    try {
      final response = await _dio.post(
        '/v1/inventory/items',
        data: {
          'name': name,
          'name_ar': nameAr,
          'sku': sku,
          'barcode': barcode,
          'category': category.value,
          'unit': unit.value,
          'reorder_level': reorderLevel,
          'max_capacity': maxCapacity,
          'warehouse_id': warehouseId,
          'supplier_id': supplierId,
          'unit_price': unitPrice,
          'batch_number': batchNumber,
          'lot_number': lotNumber,
          'expiry_date': expiryDate?.toIso8601String(),
          'manufacture_date': manufactureDate?.toIso8601String(),
          'image_url': imageUrl,
          'description': description,
          'description_ar': descriptionAr,
          'metadata': metadata,
        },
      );

      return ApiResult.success(
        InventoryItem.fromJson(response.data as Map<String, dynamic>),
      );
    } on DioException catch (e) {
      return ApiResult.failure(
        e.message ?? 'Failed to create item',
        'فشل في إنشاء العنصر',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// تحديث عنصر
  Future<ApiResult<InventoryItem>> updateItem(
    String itemId,
    Map<String, dynamic> updates,
  ) async {
    try {
      final response = await _dio.put(
        '/v1/inventory/items/$itemId',
        data: updates,
      );

      return ApiResult.success(
        InventoryItem.fromJson(response.data as Map<String, dynamic>),
      );
    } on DioException catch (e) {
      if (e.response?.statusCode == 404) {
        return ApiResult.failure('Item not found', 'العنصر غير موجود');
      }
      return ApiResult.failure(
        e.message ?? 'Failed to update item',
        'فشل في تحديث العنصر',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// حذف عنصر
  Future<ApiResult<void>> deleteItem(String itemId) async {
    try {
      await _dio.delete('/v1/inventory/items/$itemId');
      return ApiResult.success(null);
    } on DioException catch (e) {
      if (e.response?.statusCode == 404) {
        return ApiResult.failure('Item not found', 'العنصر غير موجود');
      }
      return ApiResult.failure(
        e.message ?? 'Failed to delete item',
        'فشل في حذف العنصر',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Stock Movements
  // ─────────────────────────────────────────────────────────────────────────────

  /// إدخال مخزون
  Future<ApiResult<StockMovement>> stockIn({
    required String itemId,
    required double quantity,
    String? warehouseId,
    String? batchNumber,
    String? reference,
    String? notes,
    String? notesAr,
    DateTime? movementDate,
  }) async {
    try {
      final response = await _dio.post(
        '/v1/inventory/stock/in',
        data: {
          'item_id': itemId,
          'quantity': quantity,
          'warehouse_id': warehouseId,
          'batch_number': batchNumber,
          'reference': reference,
          'notes': notes,
          'notes_ar': notesAr,
          'movement_date': movementDate?.toIso8601String(),
        },
      );

      return ApiResult.success(
        StockMovement.fromJson(response.data as Map<String, dynamic>),
      );
    } on DioException catch (e) {
      return ApiResult.failure(
        e.message ?? 'Failed to record stock in',
        'فشل في تسجيل إدخال المخزون',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// إخراج مخزون
  Future<ApiResult<StockMovement>> stockOut({
    required String itemId,
    required double quantity,
    String? warehouseId,
    String? reference,
    String? notes,
    String? notesAr,
    DateTime? movementDate,
  }) async {
    try {
      final response = await _dio.post(
        '/v1/inventory/stock/out',
        data: {
          'item_id': itemId,
          'quantity': quantity,
          'warehouse_id': warehouseId,
          'reference': reference,
          'notes': notes,
          'notes_ar': notesAr,
          'movement_date': movementDate?.toIso8601String(),
        },
      );

      return ApiResult.success(
        StockMovement.fromJson(response.data as Map<String, dynamic>),
      );
    } on DioException catch (e) {
      return ApiResult.failure(
        e.message ?? 'Failed to record stock out',
        'فشل في تسجيل إخراج المخزون',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// تطبيق على الحقل
  Future<ApiResult<StockMovement>> applyToField({
    required String itemId,
    required double quantity,
    required String fieldId,
    String? notes,
    String? notesAr,
    DateTime? movementDate,
  }) async {
    try {
      final response = await _dio.post(
        '/v1/inventory/stock/apply',
        data: {
          'item_id': itemId,
          'quantity': quantity,
          'field_id': fieldId,
          'notes': notes,
          'notes_ar': notesAr,
          'movement_date': movementDate?.toIso8601String(),
        },
      );

      return ApiResult.success(
        StockMovement.fromJson(response.data as Map<String, dynamic>),
      );
    } on DioException catch (e) {
      return ApiResult.failure(
        e.message ?? 'Failed to record field application',
        'فشل في تسجيل التطبيق على الحقل',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// تعديل المخزون
  Future<ApiResult<StockMovement>> adjustStock({
    required String itemId,
    required double quantity,
    String? notes,
    String? notesAr,
    DateTime? movementDate,
  }) async {
    try {
      final response = await _dio.post(
        '/v1/inventory/stock/adjust',
        data: {
          'item_id': itemId,
          'quantity': quantity,
          'notes': notes,
          'notes_ar': notesAr,
          'movement_date': movementDate?.toIso8601String(),
        },
      );

      return ApiResult.success(
        StockMovement.fromJson(response.data as Map<String, dynamic>),
      );
    } on DioException catch (e) {
      return ApiResult.failure(
        e.message ?? 'Failed to adjust stock',
        'فشل في تعديل المخزون',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// جلب حركات المخزون لعنصر
  Future<ApiResult<List<StockMovement>>> getMovements(
    String itemId, {
    int limit = 50,
    int offset = 0,
  }) async {
    try {
      final response = await _dio.get(
        '/v1/inventory/movements/$itemId',
        queryParameters: {
          'limit': limit,
          'offset': offset,
        },
      );

      final data = response.data as Map<String, dynamic>;
      final movements = (data['movements'] as List)
          .map((e) => StockMovement.fromJson(e as Map<String, dynamic>))
          .toList();

      return ApiResult.success(movements);
    } on DioException catch (e) {
      return ApiResult.failure(
        e.message ?? 'Failed to fetch movements',
        'فشل في جلب حركات المخزون',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Warehouses
  // ─────────────────────────────────────────────────────────────────────────────

  /// جلب جميع المستودعات
  Future<ApiResult<List<Warehouse>>> getWarehouses() async {
    try {
      final response = await _dio.get('/v1/inventory/warehouses');

      final data = response.data as Map<String, dynamic>;
      final warehouses = (data['warehouses'] as List)
          .map((e) => Warehouse.fromJson(e as Map<String, dynamic>))
          .toList();

      return ApiResult.success(warehouses);
    } on DioException catch (e) {
      return ApiResult.failure(
        e.message ?? 'Failed to fetch warehouses',
        'فشل في جلب المستودعات',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Suppliers
  // ─────────────────────────────────────────────────────────────────────────────

  /// جلب جميع الموردين
  Future<ApiResult<List<Supplier>>> getSuppliers() async {
    try {
      final response = await _dio.get('/v1/inventory/suppliers');

      final data = response.data as Map<String, dynamic>;
      final suppliers = (data['suppliers'] as List)
          .map((e) => Supplier.fromJson(e as Map<String, dynamic>))
          .toList();

      return ApiResult.success(suppliers);
    } on DioException catch (e) {
      return ApiResult.failure(
        e.message ?? 'Failed to fetch suppliers',
        'فشل في جلب الموردين',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Statistics
  // ─────────────────────────────────────────────────────────────────────────────

  /// جلب إحصائيات المخزون
  Future<ApiResult<InventoryStats>> getStats() async {
    try {
      final response = await _dio.get('/v1/inventory/stats');
      return ApiResult.success(
        InventoryStats.fromJson(response.data as Map<String, dynamic>),
      );
    } on DioException catch (e) {
      return ApiResult.failure(
        e.message ?? 'Failed to fetch stats',
        'فشل في جلب الإحصائيات',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }
}
