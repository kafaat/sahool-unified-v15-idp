/// SAHOOL Marketplace Provider
/// مزود السوق - إدارة المنتجات والطلبات
///
/// Features:
/// - Product listing with filters
/// - Shopping cart management
/// - Order creation
/// - Smart harvest listing
library;

import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/config/api_config.dart';
import '../../core/utils/app_logger.dart';

// =============================================================================
// Models
// =============================================================================

/// تصنيف المنتج
enum ProductCategory {
  harvest,    // محصول
  seeds,      // بذور
  fertilizer, // أسمدة
  pesticide,  // مبيدات
  equipment,  // معدات
  irrigation, // أدوات ري
  other,      // أخرى
}

/// نوع البائع
enum SellerType {
  farmer,     // مزارع
  company,    // شركة
  cooperative, // تعاونية
}

/// المنتج
class Product {
  final String id;
  final String name;
  final String nameAr;
  final ProductCategory category;
  final double price;
  final double stock;
  final String unit;
  final String? description;
  final String? descriptionAr;
  final String? imageUrl;
  final String sellerId;
  final SellerType sellerType;
  final String? sellerName;
  final String? governorate;
  final String? cropType;
  final String? qualityGrade;
  final bool featured;
  final DateTime createdAt;

  const Product({
    required this.id,
    required this.name,
    required this.nameAr,
    required this.category,
    required this.price,
    required this.stock,
    required this.unit,
    this.description,
    this.descriptionAr,
    this.imageUrl,
    required this.sellerId,
    required this.sellerType,
    this.sellerName,
    this.governorate,
    this.cropType,
    this.qualityGrade,
    this.featured = false,
    required this.createdAt,
  });

  factory Product.fromJson(Map<String, dynamic> json) {
    return Product(
      id: json['id'] as String,
      name: json['name'] as String,
      nameAr: json['nameAr'] as String? ?? json['name'] as String,
      category: _parseCategory(json['category'] as String?),
      price: (json['price'] as num).toDouble(),
      stock: (json['stock'] as num).toDouble(),
      unit: json['unit'] as String? ?? 'unit',
      description: json['description'] as String?,
      descriptionAr: json['descriptionAr'] as String?,
      imageUrl: json['imageUrl'] as String?,
      sellerId: json['sellerId'] as String,
      sellerType: _parseSellerType(json['sellerType'] as String?),
      sellerName: json['sellerName'] as String?,
      governorate: json['governorate'] as String?,
      cropType: json['cropType'] as String?,
      qualityGrade: json['qualityGrade'] as String?,
      featured: json['featured'] as bool? ?? false,
      createdAt: json['createdAt'] != null
          ? DateTime.tryParse(json['createdAt'] as String) ?? DateTime.now()
          : DateTime.now(),
    );
  }

  static ProductCategory _parseCategory(String? category) {
    switch (category?.toUpperCase()) {
      case 'HARVEST':
        return ProductCategory.harvest;
      case 'SEEDS':
        return ProductCategory.seeds;
      case 'FERTILIZER':
        return ProductCategory.fertilizer;
      case 'PESTICIDE':
        return ProductCategory.pesticide;
      case 'EQUIPMENT':
        return ProductCategory.equipment;
      case 'IRRIGATION':
        return ProductCategory.irrigation;
      default:
        return ProductCategory.other;
    }
  }

  static SellerType _parseSellerType(String? type) {
    switch (type?.toUpperCase()) {
      case 'COMPANY':
        return SellerType.company;
      case 'COOPERATIVE':
        return SellerType.cooperative;
      default:
        return SellerType.farmer;
    }
  }

  /// الحصول على أيقونة التصنيف
  String get categoryIcon {
    switch (category) {
      case ProductCategory.harvest:
        return '🌾';
      case ProductCategory.seeds:
        return '🌱';
      case ProductCategory.fertilizer:
        return '🧪';
      case ProductCategory.pesticide:
        return '🛡️';
      case ProductCategory.equipment:
        return '🚜';
      case ProductCategory.irrigation:
        return '💧';
      case ProductCategory.other:
        return '📦';
    }
  }

  /// الحصول على اسم التصنيف بالعربية
  String get categoryNameAr {
    switch (category) {
      case ProductCategory.harvest:
        return 'محاصيل';
      case ProductCategory.seeds:
        return 'بذور';
      case ProductCategory.fertilizer:
        return 'أسمدة';
      case ProductCategory.pesticide:
        return 'مبيدات';
      case ProductCategory.equipment:
        return 'معدات';
      case ProductCategory.irrigation:
        return 'ري';
      case ProductCategory.other:
        return 'أخرى';
    }
  }

  /// الحصول على الوحدة بالعربية
  String get unitAr {
    switch (unit.toLowerCase()) {
      case 'ton':
        return 'طن';
      case 'kg':
        return 'كجم';
      case 'unit':
        return 'قطعة';
      case 'liter':
        return 'لتر';
      case 'bag':
        return 'كيس';
      default:
        return unit;
    }
  }
}

/// عنصر السلة
class CartItem {
  final Product product;
  final double quantity;

  const CartItem({
    required this.product,
    required this.quantity,
  });

  CartItem copyWith({double? quantity}) {
    return CartItem(
      product: product,
      quantity: quantity ?? this.quantity,
    );
  }

  double get totalPrice => product.price * quantity;
}

/// الطلب
class Order {
  final String id;
  final String orderNumber;
  final String buyerId;
  final double subtotal;
  final double deliveryFee;
  final double serviceFee;
  final double totalAmount;
  final String status;
  final DateTime createdAt;

  const Order({
    required this.id,
    required this.orderNumber,
    required this.buyerId,
    required this.subtotal,
    required this.deliveryFee,
    required this.serviceFee,
    required this.totalAmount,
    required this.status,
    required this.createdAt,
  });

  factory Order.fromJson(Map<String, dynamic> json) {
    return Order(
      id: json['id'] as String,
      orderNumber: json['orderNumber'] as String,
      buyerId: json['buyerId'] as String,
      subtotal: (json['subtotal'] as num).toDouble(),
      deliveryFee: (json['deliveryFee'] as num?)?.toDouble() ?? 0,
      serviceFee: (json['serviceFee'] as num?)?.toDouble() ?? 0,
      totalAmount: (json['totalAmount'] as num).toDouble(),
      status: json['status'] as String,
      createdAt: DateTime.tryParse(json['createdAt'] as String) ?? DateTime.now(),
    );
  }

  /// الحصول على حالة الطلب بالعربية
  String get statusAr {
    switch (status.toUpperCase()) {
      case 'PENDING':
        return 'قيد الانتظار';
      case 'CONFIRMED':
        return 'مؤكد';
      case 'PROCESSING':
        return 'جاري التجهيز';
      case 'SHIPPED':
        return 'تم الشحن';
      case 'DELIVERED':
        return 'تم التسليم';
      case 'CANCELLED':
        return 'ملغي';
      default:
        return status;
    }
  }
}

// =============================================================================
// State
// =============================================================================

/// حالة السوق
class MarketplaceState {
  final List<Product> products;
  final List<Product> featuredProducts;
  final List<CartItem> cart;
  final List<Order> orders;
  final ProductCategory? selectedCategory;
  final bool isLoading;
  final String? error;

  const MarketplaceState({
    this.products = const [],
    this.featuredProducts = const [],
    this.cart = const [],
    this.orders = const [],
    this.selectedCategory,
    this.isLoading = false,
    this.error,
  });

  MarketplaceState copyWith({
    List<Product>? products,
    List<Product>? featuredProducts,
    List<CartItem>? cart,
    List<Order>? orders,
    ProductCategory? selectedCategory,
    bool clearCategory = false,
    bool? isLoading,
    String? error,
  }) {
    return MarketplaceState(
      products: products ?? this.products,
      featuredProducts: featuredProducts ?? this.featuredProducts,
      cart: cart ?? this.cart,
      orders: orders ?? this.orders,
      selectedCategory: clearCategory ? null : (selectedCategory ?? this.selectedCategory),
      isLoading: isLoading ?? this.isLoading,
      error: error,
    );
  }

  /// إجمالي السلة
  double get cartTotal => cart.fold(0, (sum, item) => sum + item.totalPrice);

  /// عدد عناصر السلة
  int get cartItemCount => cart.length;

  /// هل السلة فارغة؟
  bool get isCartEmpty => cart.isEmpty;
}

// =============================================================================
// Provider
// =============================================================================

/// مزود السوق
/// يستخدم Dio مع ApiConfig (نمط موحد) بدلاً من http.Client المباشر
class MarketplaceNotifier extends StateNotifier<MarketplaceState> {
  final String _userId;
  final Dio _dio;

  MarketplaceNotifier({
    required String userId,
    Dio? dio,
  })  : _userId = userId,
        _dio = dio ??
            Dio(BaseOptions(
              baseUrl: ApiConfig.effectiveBaseUrl,
              connectTimeout: ApiConfig.connectTimeout,
              receiveTimeout: ApiConfig.receiveTimeout,
              headers: ApiConfig.defaultHeaders,
            )),
        super(const MarketplaceState());

  /// Initialize and load initial data. Call explicitly after construction
  /// to avoid firing network requests in the constructor.
  Future<void> init() async {
    if (!mounted) return;
    await loadProducts();
  }

  /// تحميل المنتجات من marketplace-service عبر ApiConfig
  Future<void> loadProducts({ProductCategory? category}) async {
    if (!mounted) return;
    state = state.copyWith(isLoading: true, error: null);

    try {
      final queryParams = <String, dynamic>{};
      if (category != null) {
        queryParams['category'] = category.name.toUpperCase();
      }

      final response = await _dio.get(
        ApiConfig.marketProducts,
        queryParameters: queryParams.isNotEmpty ? queryParams : null,
      );
      if (!mounted) return;

      final List data = response.data as List;
      final products = data
          .map((e) => Product.fromJson(e as Map<String, dynamic>))
          .toList();
      final featured = products.where((p) => p.featured).toList();

      state = state.copyWith(
        products: products,
        featuredProducts: featured,
        selectedCategory: category,
        clearCategory: category == null,
        isLoading: false,
      );
    } on DioException catch (e) {
      if (!mounted) return;
      AppLogger.w(
        'Marketplace products API unavailable (${e.type.name}), showing empty list',
        tag: 'MARKETPLACE',
      );
      state = state.copyWith(
        isLoading: false,
        error: 'فشل في تحميل المنتجات - تحقق من الاتصال',
      );
    } catch (e) {
      if (!mounted) return;
      state = state.copyWith(
        isLoading: false,
        error: 'خطأ في الاتصال: ${e.toString()}',
      );
    }
  }

  /// تصفية حسب التصنيف
  void filterByCategory(ProductCategory? category) {
    loadProducts(category: category);
  }

  /// إضافة إلى السلة
  void addToCart(Product product, {double quantity = 1}) {
    final existingIndex = state.cart.indexWhere(
      (item) => item.product.id == product.id,
    );

    List<CartItem> newCart;

    if (existingIndex >= 0) {
      // تحديث الكمية
      newCart = [...state.cart];
      final existingItem = newCart[existingIndex];
      newCart[existingIndex] = existingItem.copyWith(
        quantity: existingItem.quantity + quantity,
      );
    } else {
      // إضافة عنصر جديد
      newCart = [
        ...state.cart,
        CartItem(product: product, quantity: quantity),
      ];
    }

    state = state.copyWith(cart: newCart);
  }

  /// تحديث كمية في السلة
  void updateCartQuantity(String productId, double quantity) {
    if (quantity <= 0) {
      removeFromCart(productId);
      return;
    }

    final newCart = state.cart.map((item) {
      if (item.product.id == productId) {
        return item.copyWith(quantity: quantity);
      }
      return item;
    }).toList();

    state = state.copyWith(cart: newCart);
  }

  /// إزالة من السلة
  void removeFromCart(String productId) {
    final newCart = state.cart.where(
      (item) => item.product.id != productId,
    ).toList();

    state = state.copyWith(cart: newCart);
  }

  /// تفريغ السلة
  void clearCart() {
    state = state.copyWith(cart: []);
  }

  /// إنشاء طلب عبر marketplace-service
  Future<Order?> createOrder({
    String? deliveryAddress,
    String? paymentMethod,
  }) async {
    if (state.isCartEmpty) return null;

    try {
      final items = state.cart.map((item) => {
        'productId': item.product.id,
        'quantity': item.quantity,
      }).toList();

      final response = await _dio.post(
        ApiConfig.marketOrders,
        data: {
          'buyerId': _userId,
          'items': items,
          'deliveryAddress': deliveryAddress,
          'paymentMethod': paymentMethod,
        },
      );

      final data = response.data as Map<String, dynamic>;
      final order = Order.fromJson(data);

      // تفريغ السلة بعد الطلب الناجح
      clearCart();

      // تحديث قائمة الطلبات
      state = state.copyWith(orders: [order, ...state.orders]);

      return order;
    } on DioException catch (e) {
      AppLogger.w('Create order API failed (${e.type.name})', tag: 'MARKETPLACE');
      return null;
    } catch (e) {
      return null;
    }
  }

  /// تحميل طلبات المستخدم
  Future<void> loadOrders() async {
    try {
      final response = await _dio.get(
        ApiConfig.userMarketOrders(_userId),
      );

      final List data = response.data as List;
      final orders = data
          .map((e) => Order.fromJson(e as Map<String, dynamic>))
          .toList();

      state = state.copyWith(orders: orders);
    } on DioException catch (e) {
      AppLogger.w('Load orders API failed (${e.type.name})', tag: 'MARKETPLACE');
    } catch (e) {
      // صمت
    }
  }

  /// عرض الحصاد في السوق (من yield-engine)
  Future<Product?> listHarvest({
    required String crop,
    required String cropAr,
    required double predictedYieldTons,
    required double pricePerTon,
    String? harvestDate,
    String? qualityGrade,
    String? governorate,
  }) async {
    try {
      final response = await _dio.post(
        ApiConfig.listHarvest,
        data: {
          'userId': _userId,
          'yieldData': {
            'crop': crop,
            'cropAr': cropAr,
            'predictedYieldTons': predictedYieldTons,
            'pricePerTon': pricePerTon,
            'harvestDate': harvestDate,
            'qualityGrade': qualityGrade,
            'governorate': governorate,
          },
        },
      );

      final data = response.data as Map<String, dynamic>;
      final product = Product.fromJson(data);

      // إعادة تحميل المنتجات
      await loadProducts();

      return product;
    } on DioException catch (e) {
      AppLogger.w('List harvest API failed (${e.type.name})', tag: 'MARKETPLACE');
      return null;
    } catch (e) {
      return null;
    }
  }
}

// =============================================================================
// Riverpod Providers
// =============================================================================

/// مزود معرف المستخدم
final marketUserIdProvider = StateProvider.autoDispose<String>((ref) => '');

/// مزود السوق الرئيسي
/// يستخدم Dio مع ApiConfig للاتصال بـ marketplace-service
final marketplaceProvider =
    StateNotifierProvider.autoDispose<MarketplaceNotifier, MarketplaceState>((ref) {
  final userId = ref.watch(marketUserIdProvider);

  final notifier = MarketplaceNotifier(userId: userId);

  // Initialize asynchronously after construction to avoid constructor side effects
  notifier.init();

  return notifier;
});

/// عدد عناصر السلة
final cartItemCountProvider = Provider.autoDispose<int>((ref) {
  return ref.watch(marketplaceProvider).cartItemCount;
});

/// إجمالي السلة
final cartTotalProvider = Provider.autoDispose<double>((ref) {
  return ref.watch(marketplaceProvider).cartTotal;
});

/// المنتجات المميزة
final featuredProductsProvider = Provider.autoDispose<List<Product>>((ref) {
  return ref.watch(marketplaceProvider).featuredProducts;
});

/// منتجات المحاصيل
final harvestProductsProvider = Provider.autoDispose<List<Product>>((ref) {
  return ref.watch(marketplaceProvider).products
      .where((p) => p.category == ProductCategory.harvest)
      .toList();
});
