/// SAHOOL Marketplace Provider
/// مزود السوق - إدارة المنتجات والطلبات
///
/// Features:
/// - Product listing with filters
/// - Shopping cart management
/// - Order creation
/// - Smart harvest listing

import 'dart:async';
import 'dart:convert';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:http/http.dart' as http;
import '../../core/config/api_config.dart';

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
          ? DateTime.parse(json['createdAt'] as String)
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
      createdAt: DateTime.parse(json['createdAt'] as String),
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
class MarketplaceNotifier extends StateNotifier<MarketplaceState> {
  final String _baseUrl;
  final String _userId;

  MarketplaceNotifier({
    required String baseUrl,
    required String userId,
  })  : _baseUrl = baseUrl,
        _userId = userId,
        super(const MarketplaceState()) {
    loadProducts();
  }

  /// تحميل المنتجات
  Future<void> loadProducts({ProductCategory? category}) async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      String url = '$_baseUrl/api/v1/market/products';
      if (category != null) {
        url += '?category=${category.name.toUpperCase()}';
      }

      final response = await http.get(Uri.parse(url));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body) as List<dynamic>;
        final products = data
            .map((json) => Product.fromJson(json as Map<String, dynamic>))
            .toList();

        final featured = products.where((p) => p.featured).toList();

        state = state.copyWith(
          products: products,
          featuredProducts: featured,
          selectedCategory: category,
          clearCategory: category == null,
          isLoading: false,
        );
      } else {
        state = state.copyWith(
          isLoading: false,
          error: 'فشل في تحميل المنتجات',
        );
      }
    } catch (e) {
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

  /// إنشاء طلب
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

      final response = await http.post(
        Uri.parse('$_baseUrl/api/v1/market/orders'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'buyerId': _userId,
          'items': items,
          'deliveryAddress': deliveryAddress,
          'paymentMethod': paymentMethod,
        }),
      );

      if (response.statusCode == 200 || response.statusCode == 201) {
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        final order = Order.fromJson(data);

        // تفريغ السلة بعد الطلب الناجح
        clearCart();

        // تحديث قائمة الطلبات
        state = state.copyWith(orders: [order, ...state.orders]);

        return order;
      }
      return null;
    } catch (_) {
      return null;
    }
  }

  /// تحميل طلبات المستخدم
  Future<void> loadOrders() async {
    try {
      final response = await http.get(
        Uri.parse('$_baseUrl/api/v1/market/orders/$_userId'),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body) as List<dynamic>;
        final orders = data
            .map((json) => Order.fromJson(json as Map<String, dynamic>))
            .toList();

        state = state.copyWith(orders: orders);
      }
    } catch (_) {
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
      final response = await http.post(
        Uri.parse('$_baseUrl/api/v1/market/list-harvest'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
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
        }),
      );

      if (response.statusCode == 200 || response.statusCode == 201) {
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        final product = Product.fromJson(data);

        // إعادة تحميل المنتجات
        await loadProducts();

        return product;
      }
      return null;
    } catch (_) {
      return null;
    }
  }
}

// =============================================================================
// Riverpod Providers
// =============================================================================

/// مزود معرف المستخدم
final marketUserIdProvider = StateProvider<String>((ref) => '');

/// مزود رابط API
final marketApiUrlProvider = Provider<String>((ref) {
  // Use ApiConfig which handles production/development/emulator detection
  return ApiConfig.marketplaceServiceUrl;
});

/// مزود السوق الرئيسي
final marketplaceProvider =
    StateNotifierProvider<MarketplaceNotifier, MarketplaceState>((ref) {
  final baseUrl = ref.watch(marketApiUrlProvider);
  final userId = ref.watch(marketUserIdProvider);

  return MarketplaceNotifier(
    baseUrl: baseUrl,
    userId: userId,
  );
});

/// عدد عناصر السلة
final cartItemCountProvider = Provider<int>((ref) {
  return ref.watch(marketplaceProvider).cartItemCount;
});

/// إجمالي السلة
final cartTotalProvider = Provider<double>((ref) {
  return ref.watch(marketplaceProvider).cartTotal;
});

/// المنتجات المميزة
final featuredProductsProvider = Provider<List<Product>>((ref) {
  return ref.watch(marketplaceProvider).featuredProducts;
});

/// منتجات المحاصيل
final harvestProductsProvider = Provider<List<Product>>((ref) {
  return ref.watch(marketplaceProvider).products
      .where((p) => p.category == ProductCategory.harvest)
      .toList();
});
