/// Unit Tests for Marketplace Feature - Models, State, and Cart Logic
/// اختبارات وحدات ميزة السوق
import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/features/marketplace/marketplace_provider.dart';

void main() {
  // ═══════════════════════════════════════════════════════════════════════════
  // ProductCategory Enum Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('ProductCategory', () {
    test('has all expected values', () {
      expect(ProductCategory.values, hasLength(7));
      expect(ProductCategory.values, contains(ProductCategory.harvest));
      expect(ProductCategory.values, contains(ProductCategory.seeds));
      expect(ProductCategory.values, contains(ProductCategory.fertilizer));
      expect(ProductCategory.values, contains(ProductCategory.pesticide));
      expect(ProductCategory.values, contains(ProductCategory.equipment));
      expect(ProductCategory.values, contains(ProductCategory.irrigation));
      expect(ProductCategory.values, contains(ProductCategory.other));
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // SellerType Enum Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('SellerType', () {
    test('has all expected values', () {
      expect(SellerType.values, hasLength(3));
      expect(SellerType.values, contains(SellerType.farmer));
      expect(SellerType.values, contains(SellerType.company));
      expect(SellerType.values, contains(SellerType.cooperative));
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Product Model Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('Product', () {
    test('fromJson parses all fields', () {
      // Arrange
      final json = {
        'id': 'PROD-001',
        'name': 'Premium Wheat Seeds',
        'nameAr': 'بذور قمح ممتازة',
        'category': 'SEEDS',
        'price': 150.0,
        'stock': 500.0,
        'unit': 'kg',
        'description': 'High-yield wheat seeds',
        'descriptionAr': 'بذور قمح عالية الإنتاجية',
        'imageUrl': 'https://example.com/wheat.jpg',
        'sellerId': 'seller-001',
        'sellerType': 'FARMER',
        'sellerName': 'Ahmed Farm',
        'governorate': 'Qassim',
        'cropType': 'wheat',
        'qualityGrade': 'A',
        'featured': true,
        'createdAt': '2025-06-15T10:00:00Z',
      };

      // Act
      final product = Product.fromJson(json);

      // Assert
      expect(product.id, 'PROD-001');
      expect(product.name, 'Premium Wheat Seeds');
      expect(product.nameAr, 'بذور قمح ممتازة');
      expect(product.category, ProductCategory.seeds);
      expect(product.price, 150.0);
      expect(product.stock, 500.0);
      expect(product.unit, 'kg');
      expect(product.description, 'High-yield wheat seeds');
      expect(product.descriptionAr, 'بذور قمح عالية الإنتاجية');
      expect(product.imageUrl, 'https://example.com/wheat.jpg');
      expect(product.sellerId, 'seller-001');
      expect(product.sellerType, SellerType.farmer);
      expect(product.sellerName, 'Ahmed Farm');
      expect(product.governorate, 'Qassim');
      expect(product.cropType, 'wheat');
      expect(product.qualityGrade, 'A');
      expect(product.featured, true);
    });

    test('fromJson parses category case-insensitively', () {
      // Arrange & Act
      final harvest = Product.fromJson(_minimalProductJson(category: 'HARVEST'));
      final fertilizer = Product.fromJson(_minimalProductJson(category: 'fertilizer'));
      final pesticide = Product.fromJson(_minimalProductJson(category: 'Pesticide'));
      final equipment = Product.fromJson(_minimalProductJson(category: 'EQUIPMENT'));
      final irrigation = Product.fromJson(_minimalProductJson(category: 'IRRIGATION'));

      // Assert
      expect(harvest.category, ProductCategory.harvest);
      expect(fertilizer.category, ProductCategory.fertilizer);
      expect(pesticide.category, ProductCategory.pesticide);
      expect(equipment.category, ProductCategory.equipment);
      expect(irrigation.category, ProductCategory.irrigation);
    });

    test('fromJson defaults to other for unknown category', () {
      final product = Product.fromJson(_minimalProductJson(category: 'UNKNOWN'));
      expect(product.category, ProductCategory.other);
    });

    test('fromJson defaults to other for null category', () {
      final product = Product.fromJson(_minimalProductJson(category: null));
      expect(product.category, ProductCategory.other);
    });

    test('fromJson parses sellerType case-insensitively', () {
      final company = Product.fromJson(
        _minimalProductJson(sellerType: 'COMPANY'),
      );
      final cooperative = Product.fromJson(
        _minimalProductJson(sellerType: 'COOPERATIVE'),
      );

      expect(company.sellerType, SellerType.company);
      expect(cooperative.sellerType, SellerType.cooperative);
    });

    test('fromJson defaults sellerType to farmer', () {
      final product = Product.fromJson(
        _minimalProductJson(sellerType: 'UNKNOWN'),
      );
      expect(product.sellerType, SellerType.farmer);
    });

    test('fromJson uses name for nameAr when nameAr missing', () {
      // Arrange
      final json = _minimalProductJson();
      json.remove('nameAr');

      // Act
      final product = Product.fromJson(json);

      // Assert
      expect(product.nameAr, product.name);
    });

    test('fromJson defaults featured to false', () {
      final product = Product.fromJson(_minimalProductJson());
      expect(product.featured, false);
    });

    test('categoryIcon returns correct emoji for each category', () {
      expect(_createProduct(ProductCategory.harvest).categoryIcon, '🌾');
      expect(_createProduct(ProductCategory.seeds).categoryIcon, '🌱');
      expect(_createProduct(ProductCategory.fertilizer).categoryIcon, '🧪');
      expect(_createProduct(ProductCategory.pesticide).categoryIcon, '🛡️');
      expect(_createProduct(ProductCategory.equipment).categoryIcon, '🚜');
      expect(_createProduct(ProductCategory.irrigation).categoryIcon, '💧');
      expect(_createProduct(ProductCategory.other).categoryIcon, '📦');
    });

    test('categoryNameAr returns correct Arabic name', () {
      expect(_createProduct(ProductCategory.harvest).categoryNameAr, 'محاصيل');
      expect(_createProduct(ProductCategory.seeds).categoryNameAr, 'بذور');
      expect(_createProduct(ProductCategory.fertilizer).categoryNameAr, 'أسمدة');
      expect(_createProduct(ProductCategory.pesticide).categoryNameAr, 'مبيدات');
      expect(_createProduct(ProductCategory.equipment).categoryNameAr, 'معدات');
      expect(_createProduct(ProductCategory.irrigation).categoryNameAr, 'ري');
      expect(_createProduct(ProductCategory.other).categoryNameAr, 'أخرى');
    });

    test('unitAr returns correct Arabic unit', () {
      expect(_createProduct(ProductCategory.harvest, unit: 'ton').unitAr, 'طن');
      expect(_createProduct(ProductCategory.seeds, unit: 'kg').unitAr, 'كجم');
      expect(_createProduct(ProductCategory.equipment, unit: 'unit').unitAr, 'قطعة');
      expect(_createProduct(ProductCategory.pesticide, unit: 'liter').unitAr, 'لتر');
      expect(_createProduct(ProductCategory.fertilizer, unit: 'bag').unitAr, 'كيس');
    });

    test('unitAr returns original unit for unknown units', () {
      expect(_createProduct(ProductCategory.other, unit: 'piece').unitAr, 'piece');
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // CartItem Model Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('CartItem', () {
    test('totalPrice calculates correctly', () {
      // Arrange
      final product = _createProduct(ProductCategory.seeds, price: 25.0);
      final item = CartItem(product: product, quantity: 10);

      // Act & Assert
      expect(item.totalPrice, 250.0);
    });

    test('totalPrice with fractional quantity', () {
      final product = _createProduct(ProductCategory.harvest, price: 1500.0);
      final item = CartItem(product: product, quantity: 2.5);

      expect(item.totalPrice, 3750.0);
    });

    test('copyWith updates quantity', () {
      final product = _createProduct(ProductCategory.seeds, price: 25.0);
      final item = CartItem(product: product, quantity: 5);

      final updated = item.copyWith(quantity: 10);

      expect(updated.quantity, 10);
      expect(updated.product.id, product.id);
      expect(updated.totalPrice, 250.0);
    });

    test('copyWith preserves quantity when not specified', () {
      final product = _createProduct(ProductCategory.seeds);
      final item = CartItem(product: product, quantity: 5);

      final unchanged = item.copyWith();

      expect(unchanged.quantity, 5);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Order Model Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('Order', () {
    test('fromJson parses all fields', () {
      // Arrange
      final json = {
        'id': 'ORD-001',
        'orderNumber': 'SH-2025-0001',
        'buyerId': 'user-001',
        'subtotal': 1500.0,
        'deliveryFee': 50.0,
        'serviceFee': 30.0,
        'totalAmount': 1580.0,
        'status': 'CONFIRMED',
        'createdAt': '2025-06-15T10:00:00Z',
      };

      // Act
      final order = Order.fromJson(json);

      // Assert
      expect(order.id, 'ORD-001');
      expect(order.orderNumber, 'SH-2025-0001');
      expect(order.buyerId, 'user-001');
      expect(order.subtotal, 1500.0);
      expect(order.deliveryFee, 50.0);
      expect(order.serviceFee, 30.0);
      expect(order.totalAmount, 1580.0);
      expect(order.status, 'CONFIRMED');
    });

    test('fromJson defaults fees to 0', () {
      final json = {
        'id': 'ORD-002',
        'orderNumber': 'SH-2025-0002',
        'buyerId': 'user-001',
        'subtotal': 500.0,
        'totalAmount': 500.0,
        'status': 'PENDING',
        'createdAt': '2025-06-15T10:00:00Z',
      };

      final order = Order.fromJson(json);

      expect(order.deliveryFee, 0);
      expect(order.serviceFee, 0);
    });

    test('statusAr returns correct Arabic status', () {
      expect(_createOrder('PENDING').statusAr, 'قيد الانتظار');
      expect(_createOrder('CONFIRMED').statusAr, 'مؤكد');
      expect(_createOrder('PROCESSING').statusAr, 'جاري التجهيز');
      expect(_createOrder('SHIPPED').statusAr, 'تم الشحن');
      expect(_createOrder('DELIVERED').statusAr, 'تم التسليم');
      expect(_createOrder('CANCELLED').statusAr, 'ملغي');
    });

    test('statusAr returns raw status for unknown statuses', () {
      expect(_createOrder('REFUNDED').statusAr, 'REFUNDED');
    });

    test('statusAr is case-insensitive', () {
      expect(_createOrder('pending').statusAr, 'قيد الانتظار');
      expect(_createOrder('Confirmed').statusAr, 'مؤكد');
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // MarketplaceState Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('MarketplaceState', () {
    test('default state has correct initial values', () {
      const state = MarketplaceState();

      expect(state.products, isEmpty);
      expect(state.featuredProducts, isEmpty);
      expect(state.cart, isEmpty);
      expect(state.orders, isEmpty);
      expect(state.selectedCategory, isNull);
      expect(state.isLoading, false);
      expect(state.error, isNull);
    });

    test('cartTotal calculates sum of cart items', () {
      // Arrange
      final p1 = _createProduct(ProductCategory.seeds, price: 25.0);
      final p2 = _createProduct(ProductCategory.fertilizer, price: 100.0);
      final state = MarketplaceState(
        cart: [
          CartItem(product: p1, quantity: 10),
          CartItem(product: p2, quantity: 5),
        ],
      );

      // Act & Assert
      expect(state.cartTotal, 750.0); // 250 + 500
    });

    test('cartTotal returns 0 for empty cart', () {
      const state = MarketplaceState();
      expect(state.cartTotal, 0);
    });

    test('cartItemCount returns cart length', () {
      final p1 = _createProduct(ProductCategory.seeds);
      final state = MarketplaceState(
        cart: [CartItem(product: p1, quantity: 5)],
      );

      expect(state.cartItemCount, 1);
    });

    test('isCartEmpty returns true when empty', () {
      const state = MarketplaceState();
      expect(state.isCartEmpty, true);
    });

    test('isCartEmpty returns false when has items', () {
      final p = _createProduct(ProductCategory.seeds);
      final state = MarketplaceState(
        cart: [CartItem(product: p, quantity: 1)],
      );

      expect(state.isCartEmpty, false);
    });

    test('copyWith preserves unchanged fields', () {
      final state = MarketplaceState(
        products: [_createProduct(ProductCategory.seeds)],
        isLoading: false,
      );

      final updated = state.copyWith(isLoading: true);

      expect(updated.isLoading, true);
      expect(updated.products, hasLength(1));
      expect(updated.error, isNull);
    });

    test('copyWith clearCategory clears selectedCategory', () {
      final state = MarketplaceState(
        selectedCategory: ProductCategory.seeds,
      );

      final cleared = state.copyWith(clearCategory: true);

      expect(cleared.selectedCategory, isNull);
    });

    test('copyWith sets error', () {
      const state = MarketplaceState();
      final withError = state.copyWith(error: 'Network timeout');

      expect(withError.error, 'Network timeout');
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // MarketplaceNotifier Cart Logic Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('MarketplaceNotifier - Cart Operations', () {
    late MarketplaceNotifier notifier;

    setUp(() {
      // Create notifier - loadProducts will fail (no real server)
      // but we can still test cart operations
      notifier = MarketplaceNotifier(
        baseUrl: 'http://localhost:9999', // Non-existent
        userId: 'test-user',
      );
    });

    test('addToCart adds new item', () {
      // Arrange
      final product = _createProduct(ProductCategory.seeds, price: 25.0);

      // Act
      notifier.addToCart(product, quantity: 5);

      // Assert
      expect(notifier.state.cart, hasLength(1));
      expect(notifier.state.cart.first.quantity, 5);
      expect(notifier.state.cart.first.totalPrice, 125.0);
    });

    test('addToCart increases quantity for existing product', () {
      // Arrange
      final product = _createProduct(ProductCategory.seeds, price: 25.0);

      // Act
      notifier.addToCart(product, quantity: 5);
      notifier.addToCart(product, quantity: 3);

      // Assert
      expect(notifier.state.cart, hasLength(1));
      expect(notifier.state.cart.first.quantity, 8);
    });

    test('addToCart uses default quantity of 1', () {
      // Arrange
      final product = _createProduct(ProductCategory.seeds);

      // Act
      notifier.addToCart(product);

      // Assert
      expect(notifier.state.cart.first.quantity, 1);
    });

    test('addToCart handles multiple different products', () {
      // Arrange
      final p1 = _createProduct(ProductCategory.seeds, id: 'P1');
      final p2 = _createProduct(ProductCategory.fertilizer, id: 'P2');

      // Act
      notifier.addToCart(p1, quantity: 2);
      notifier.addToCart(p2, quantity: 3);

      // Assert
      expect(notifier.state.cart, hasLength(2));
    });

    test('updateCartQuantity updates existing item', () {
      // Arrange
      final product = _createProduct(ProductCategory.seeds, id: 'P1', price: 25.0);
      notifier.addToCart(product, quantity: 5);

      // Act
      notifier.updateCartQuantity('P1', 10);

      // Assert
      expect(notifier.state.cart.first.quantity, 10);
    });

    test('updateCartQuantity removes item when quantity <= 0', () {
      // Arrange
      final product = _createProduct(ProductCategory.seeds, id: 'P1');
      notifier.addToCart(product, quantity: 5);

      // Act
      notifier.updateCartQuantity('P1', 0);

      // Assert
      expect(notifier.state.cart, isEmpty);
    });

    test('updateCartQuantity with negative quantity removes item', () {
      // Arrange
      final product = _createProduct(ProductCategory.seeds, id: 'P1');
      notifier.addToCart(product, quantity: 3);

      // Act
      notifier.updateCartQuantity('P1', -1);

      // Assert
      expect(notifier.state.cart, isEmpty);
    });

    test('removeFromCart removes specific product', () {
      // Arrange
      final p1 = _createProduct(ProductCategory.seeds, id: 'P1');
      final p2 = _createProduct(ProductCategory.fertilizer, id: 'P2');
      notifier.addToCart(p1, quantity: 2);
      notifier.addToCart(p2, quantity: 3);

      // Act
      notifier.removeFromCart('P1');

      // Assert
      expect(notifier.state.cart, hasLength(1));
      expect(notifier.state.cart.first.product.id, 'P2');
    });

    test('removeFromCart handles non-existent product gracefully', () {
      // Arrange
      final product = _createProduct(ProductCategory.seeds, id: 'P1');
      notifier.addToCart(product, quantity: 2);

      // Act - remove non-existent ID
      notifier.removeFromCart('P-NONEXISTENT');

      // Assert - cart unchanged
      expect(notifier.state.cart, hasLength(1));
    });

    test('clearCart removes all items', () {
      // Arrange
      final p1 = _createProduct(ProductCategory.seeds, id: 'P1');
      final p2 = _createProduct(ProductCategory.fertilizer, id: 'P2');
      notifier.addToCart(p1, quantity: 2);
      notifier.addToCart(p2, quantity: 3);

      // Act
      notifier.clearCart();

      // Assert
      expect(notifier.state.cart, isEmpty);
      expect(notifier.state.isCartEmpty, true);
    });

    test('cartTotal updates correctly after operations', () {
      // Arrange
      final p1 = _createProduct(ProductCategory.seeds, id: 'P1', price: 25.0);
      final p2 = _createProduct(ProductCategory.fertilizer, id: 'P2', price: 100.0);

      // Act
      notifier.addToCart(p1, quantity: 10); // 250
      notifier.addToCart(p2, quantity: 5); // 500

      // Assert
      expect(notifier.state.cartTotal, 750.0);

      // Update quantity
      notifier.updateCartQuantity('P1', 20); // 500

      expect(notifier.state.cartTotal, 1000.0);

      // Remove
      notifier.removeFromCart('P2');

      expect(notifier.state.cartTotal, 500.0);
    });

    test('createOrder returns null when cart is empty', () async {
      // Act
      final order = await notifier.createOrder();

      // Assert
      expect(order, isNull);
    });
  });
}

// ═══════════════════════════════════════════════════════════════════════════
// Test Helpers
// ═══════════════════════════════════════════════════════════════════════════

/// Helper: create a minimal Product JSON map
Map<String, dynamic> _minimalProductJson({
  String? category,
  String? sellerType,
}) {
  return {
    'id': 'PROD-TEST',
    'name': 'Test Product',
    'nameAr': 'منتج اختباري',
    'category': category ?? 'OTHER',
    'price': 100.0,
    'stock': 50.0,
    'unit': 'unit',
    'sellerId': 'seller-test',
    'sellerType': sellerType ?? 'FARMER',
    'createdAt': '2025-06-15T10:00:00Z',
  };
}

/// Helper: create a Product with specified category and optional overrides
Product _createProduct(
  ProductCategory category, {
  String id = 'PROD-TEST',
  double price = 100.0,
  String unit = 'unit',
}) {
  return Product(
    id: id,
    name: 'Test Product',
    nameAr: 'منتج اختباري',
    category: category,
    price: price,
    stock: 50.0,
    unit: unit,
    sellerId: 'seller-test',
    sellerType: SellerType.farmer,
    createdAt: DateTime(2025, 6, 15),
  );
}

/// Helper: create an Order with a given status
Order _createOrder(String status) {
  return Order(
    id: 'ORD-TEST',
    orderNumber: 'SH-TEST-001',
    buyerId: 'user-test',
    subtotal: 100.0,
    deliveryFee: 0,
    serviceFee: 0,
    totalAmount: 100.0,
    status: status,
    createdAt: DateTime(2025, 6, 15),
  );
}
