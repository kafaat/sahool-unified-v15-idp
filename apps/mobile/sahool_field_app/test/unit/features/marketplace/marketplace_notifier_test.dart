import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/features/marketplace/marketplace_provider.dart';

/// Comprehensive MarketplaceNotifier tests
/// اختبارات شاملة لمزود السوق
void main() {
  // Shared test product
  Product _createProduct({
    String id = 'p1',
    String name = 'Wheat',
    String nameAr = 'قمح',
    ProductCategory category = ProductCategory.harvest,
    double price = 100.0,
    double stock = 50.0,
    String unit = 'ton',
    String sellerId = 's1',
    SellerType sellerType = SellerType.farmer,
    bool featured = false,
  }) {
    return Product(
      id: id,
      name: name,
      nameAr: nameAr,
      category: category,
      price: price,
      stock: stock,
      unit: unit,
      sellerId: sellerId,
      sellerType: sellerType,
      featured: featured,
      createdAt: DateTime(2025, 1, 1),
    );
  }

  group('MarketplaceNotifier - Cart Operations', () {
    late MarketplaceNotifier notifier;

    setUp(() {
      // Use a notifier - constructor calls loadProducts() which will fail silently
      notifier = MarketplaceNotifier(baseUrl: 'http://localhost:9999', userId: 'test-user');
    });

    tearDown(() {
      notifier.dispose();
    });

    test('initial state has empty cart', () {
      expect(notifier.state.cart, isEmpty);
      expect(notifier.state.isCartEmpty, isTrue);
      expect(notifier.state.cartTotal, 0.0);
      expect(notifier.state.cartItemCount, 0);
    });

    test('addToCart adds new product', () {
      final product = _createProduct();
      notifier.addToCart(product);

      expect(notifier.state.cart.length, 1);
      expect(notifier.state.cart.first.product.id, 'p1');
      expect(notifier.state.cart.first.quantity, 1.0);
      expect(notifier.state.isCartEmpty, isFalse);
    });

    test('addToCart with custom quantity', () {
      final product = _createProduct();
      notifier.addToCart(product, quantity: 5.0);

      expect(notifier.state.cart.first.quantity, 5.0);
    });

    test('addToCart increments quantity for existing product', () {
      final product = _createProduct();
      notifier.addToCart(product, quantity: 2.0);
      notifier.addToCart(product, quantity: 3.0);

      expect(notifier.state.cart.length, 1);
      expect(notifier.state.cart.first.quantity, 5.0);
    });

    test('addToCart keeps separate entries for different products', () {
      final product1 = _createProduct(id: 'p1', name: 'Wheat');
      final product2 = _createProduct(id: 'p2', name: 'Barley');

      notifier.addToCart(product1);
      notifier.addToCart(product2);

      expect(notifier.state.cart.length, 2);
    });

    test('cartTotal sums all items', () {
      final product1 = _createProduct(id: 'p1', price: 100.0);
      final product2 = _createProduct(id: 'p2', price: 200.0);

      notifier.addToCart(product1, quantity: 2.0); // 200
      notifier.addToCart(product2, quantity: 3.0); // 600

      expect(notifier.state.cartTotal, 800.0);
    });

    test('cartItemCount returns number of distinct items', () {
      notifier.addToCart(_createProduct(id: 'p1'));
      notifier.addToCart(_createProduct(id: 'p2'));
      notifier.addToCart(_createProduct(id: 'p1')); // duplicate

      expect(notifier.state.cartItemCount, 2);
    });

    test('updateCartQuantity changes quantity', () {
      notifier.addToCart(_createProduct(id: 'p1'), quantity: 3.0);
      notifier.updateCartQuantity('p1', 10.0);

      expect(notifier.state.cart.first.quantity, 10.0);
    });

    test('updateCartQuantity with 0 removes item', () {
      notifier.addToCart(_createProduct(id: 'p1'));
      notifier.updateCartQuantity('p1', 0);

      expect(notifier.state.cart, isEmpty);
    });

    test('updateCartQuantity with negative removes item', () {
      notifier.addToCart(_createProduct(id: 'p1'));
      notifier.updateCartQuantity('p1', -1);

      expect(notifier.state.cart, isEmpty);
    });

    test('removeFromCart removes specific product', () {
      notifier.addToCart(_createProduct(id: 'p1'));
      notifier.addToCart(_createProduct(id: 'p2'));

      notifier.removeFromCart('p1');

      expect(notifier.state.cart.length, 1);
      expect(notifier.state.cart.first.product.id, 'p2');
    });

    test('removeFromCart does nothing for non-existent product', () {
      notifier.addToCart(_createProduct(id: 'p1'));
      notifier.removeFromCart('non-existent');

      expect(notifier.state.cart.length, 1);
    });

    test('clearCart empties all items', () {
      notifier.addToCart(_createProduct(id: 'p1'));
      notifier.addToCart(_createProduct(id: 'p2'));
      notifier.addToCart(_createProduct(id: 'p3'));

      notifier.clearCart();

      expect(notifier.state.cart, isEmpty);
      expect(notifier.state.isCartEmpty, isTrue);
    });

    test('createOrder returns null when cart is empty', () async {
      final result = await notifier.createOrder();
      expect(result, isNull);
    });
  });

  group('Product model tests', () {
    test('fromJson with complete data', () {
      final json = {
        'id': 'p1',
        'name': 'Wheat',
        'nameAr': 'قمح',
        'category': 'HARVEST',
        'price': 100,
        'stock': 50,
        'unit': 'ton',
        'sellerId': 's1',
        'sellerType': 'FARMER',
        'featured': true,
        'createdAt': '2025-01-01T00:00:00.000',
      };

      final product = Product.fromJson(json);

      expect(product.id, 'p1');
      expect(product.name, 'Wheat');
      expect(product.nameAr, 'قمح');
      expect(product.category, ProductCategory.harvest);
      expect(product.price, 100.0);
      expect(product.stock, 50.0);
      expect(product.unit, 'ton');
      expect(product.sellerId, 's1');
      expect(product.sellerType, SellerType.farmer);
      expect(product.featured, isTrue);
    });

    test('fromJson with minimal data uses defaults', () {
      final json = {
        'id': 'p1',
        'name': 'Test',
        'price': 50,
        'stock': 10,
        'sellerId': 's1',
      };

      final product = Product.fromJson(json);

      expect(product.nameAr, 'Test'); // defaults to name
      expect(product.category, ProductCategory.other); // null → other
      expect(product.unit, 'unit'); // default
      expect(product.sellerType, SellerType.farmer); // default
      expect(product.featured, isFalse); // default
    });

    test('categoryIcon returns correct emoji for each category', () {
      final tests = {
        ProductCategory.harvest: '🌾',
        ProductCategory.seeds: '🌱',
        ProductCategory.fertilizer: '🧪',
        ProductCategory.pesticide: '🛡️',
        ProductCategory.equipment: '🚜',
        ProductCategory.irrigation: '💧',
        ProductCategory.other: '📦',
      };

      for (final entry in tests.entries) {
        final product = Product(
          id: '1', name: 'test', nameAr: 'test',
          category: entry.key, price: 1, stock: 1, unit: 'u',
          sellerId: 's1', sellerType: SellerType.farmer,
          createdAt: DateTime.now(),
        );
        expect(product.categoryIcon, entry.value,
            reason: 'Category ${entry.key} should have icon ${entry.value}');
      }
    });

    test('categoryNameAr returns Arabic names', () {
      final tests = {
        ProductCategory.harvest: 'محاصيل',
        ProductCategory.seeds: 'بذور',
        ProductCategory.fertilizer: 'أسمدة',
        ProductCategory.pesticide: 'مبيدات',
        ProductCategory.equipment: 'معدات',
        ProductCategory.irrigation: 'ري',
        ProductCategory.other: 'أخرى',
      };

      for (final entry in tests.entries) {
        final product = Product(
          id: '1', name: 'test', nameAr: 'test',
          category: entry.key, price: 1, stock: 1, unit: 'u',
          sellerId: 's1', sellerType: SellerType.farmer,
          createdAt: DateTime.now(),
        );
        expect(product.categoryNameAr, entry.value);
      }
    });

    test('unitAr translates unit names to Arabic', () {
      final tests = {
        'ton': 'طن',
        'kg': 'كجم',
        'unit': 'قطعة',
        'liter': 'لتر',
        'bag': 'كيس',
        'box': 'box', // unknown passes through
      };

      for (final entry in tests.entries) {
        final product = Product(
          id: '1', name: 'test', nameAr: 'test',
          category: ProductCategory.other, price: 1, stock: 1,
          unit: entry.key,
          sellerId: 's1', sellerType: SellerType.farmer,
          createdAt: DateTime.now(),
        );
        expect(product.unitAr, entry.value);
      }
    });
  });

  group('CartItem', () {
    test('totalPrice is price * quantity', () {
      final product = Product(
        id: 'p1', name: 'Wheat', nameAr: 'قمح',
        category: ProductCategory.harvest, price: 150.0, stock: 50,
        unit: 'ton', sellerId: 's1', sellerType: SellerType.farmer,
        createdAt: DateTime.now(),
      );

      final cartItem = CartItem(product: product, quantity: 3.0);
      expect(cartItem.totalPrice, 450.0);
    });

    test('copyWith changes quantity', () {
      final product = Product(
        id: 'p1', name: 'Wheat', nameAr: 'قمح',
        category: ProductCategory.harvest, price: 100.0, stock: 50,
        unit: 'ton', sellerId: 's1', sellerType: SellerType.farmer,
        createdAt: DateTime.now(),
      );

      final item = CartItem(product: product, quantity: 2.0);
      final updated = item.copyWith(quantity: 5.0);

      expect(updated.quantity, 5.0);
      expect(updated.product.id, 'p1'); // product preserved
    });
  });

  group('Order', () {
    test('fromJson parses all fields', () {
      final json = {
        'id': 'o1',
        'orderNumber': 'ORD-001',
        'buyerId': 'b1',
        'subtotal': 500,
        'deliveryFee': 50,
        'serviceFee': 25,
        'totalAmount': 575,
        'status': 'PENDING',
        'createdAt': '2025-01-01T00:00:00.000',
      };

      final order = Order.fromJson(json);

      expect(order.id, 'o1');
      expect(order.orderNumber, 'ORD-001');
      expect(order.subtotal, 500.0);
      expect(order.deliveryFee, 50.0);
      expect(order.serviceFee, 25.0);
      expect(order.totalAmount, 575.0);
    });

    test('fromJson with null delivery/service fees defaults to 0', () {
      final json = {
        'id': 'o1',
        'orderNumber': 'ORD-001',
        'buyerId': 'b1',
        'subtotal': 500,
        'totalAmount': 500,
        'status': 'PENDING',
        'createdAt': '2025-01-01T00:00:00.000',
      };

      final order = Order.fromJson(json);
      expect(order.deliveryFee, 0.0);
      expect(order.serviceFee, 0.0);
    });

    test('statusAr returns Arabic status for all values', () {
      final tests = {
        'PENDING': 'قيد الانتظار',
        'CONFIRMED': 'مؤكد',
        'PROCESSING': 'جاري التجهيز',
        'SHIPPED': 'تم الشحن',
        'DELIVERED': 'تم التسليم',
        'CANCELLED': 'ملغي',
      };

      for (final entry in tests.entries) {
        final order = Order(
          id: 'o1', orderNumber: 'ORD', buyerId: 'b1',
          subtotal: 0, deliveryFee: 0, serviceFee: 0,
          totalAmount: 0, status: entry.key,
          createdAt: DateTime.now(),
        );
        expect(order.statusAr, entry.value,
            reason: 'Status ${entry.key} should translate to ${entry.value}');
      }
    });

    test('statusAr returns raw status for unknown values', () {
      final order = Order(
        id: 'o1', orderNumber: 'ORD', buyerId: 'b1',
        subtotal: 0, deliveryFee: 0, serviceFee: 0,
        totalAmount: 0, status: 'CUSTOM',
        createdAt: DateTime.now(),
      );
      expect(order.statusAr, 'CUSTOM');
    });
  });

  group('MarketplaceState', () {
    test('default state', () {
      const state = MarketplaceState();
      expect(state.products, isEmpty);
      expect(state.featuredProducts, isEmpty);
      expect(state.cart, isEmpty);
      expect(state.orders, isEmpty);
      expect(state.selectedCategory, isNull);
      expect(state.isLoading, isFalse);
      expect(state.error, isNull);
    });

    test('copyWith preserves unchanged fields', () {
      const state = MarketplaceState(isLoading: true);
      final updated = state.copyWith(error: 'test');

      expect(updated.isLoading, isTrue); // preserved
      expect(updated.error, 'test'); // changed
    });

    test('copyWith clearCategory sets selectedCategory to null', () {
      const state = MarketplaceState(
        selectedCategory: ProductCategory.harvest,
      );
      final updated = state.copyWith(clearCategory: true);

      expect(updated.selectedCategory, isNull);
    });

    test('cartTotal with multiple items', () {
      final product1 = Product(
        id: 'p1', name: 'a', nameAr: 'a',
        category: ProductCategory.harvest, price: 100, stock: 10,
        unit: 'ton', sellerId: 's1', sellerType: SellerType.farmer,
        createdAt: DateTime.now(),
      );
      final product2 = Product(
        id: 'p2', name: 'b', nameAr: 'b',
        category: ProductCategory.seeds, price: 50, stock: 20,
        unit: 'kg', sellerId: 's1', sellerType: SellerType.farmer,
        createdAt: DateTime.now(),
      );

      final state = MarketplaceState(cart: [
        CartItem(product: product1, quantity: 2), // 200
        CartItem(product: product2, quantity: 10), // 500
      ]);

      expect(state.cartTotal, 700.0);
      expect(state.cartItemCount, 2);
      expect(state.isCartEmpty, isFalse);
    });
  });

  group('ProductCategory enum', () {
    test('has 7 values', () {
      expect(ProductCategory.values.length, 7);
    });

    test('contains all expected values', () {
      expect(ProductCategory.values, contains(ProductCategory.harvest));
      expect(ProductCategory.values, contains(ProductCategory.seeds));
      expect(ProductCategory.values, contains(ProductCategory.fertilizer));
      expect(ProductCategory.values, contains(ProductCategory.pesticide));
      expect(ProductCategory.values, contains(ProductCategory.equipment));
      expect(ProductCategory.values, contains(ProductCategory.irrigation));
      expect(ProductCategory.values, contains(ProductCategory.other));
    });
  });

  group('SellerType enum', () {
    test('has 3 values', () {
      expect(SellerType.values.length, 3);
    });

    test('contains all expected values', () {
      expect(SellerType.values, contains(SellerType.farmer));
      expect(SellerType.values, contains(SellerType.company));
      expect(SellerType.values, contains(SellerType.cooperative));
    });
  });
}
