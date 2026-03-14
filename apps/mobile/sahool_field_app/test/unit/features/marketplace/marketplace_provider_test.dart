import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/features/marketplace/marketplace_provider.dart';

void main() {
  group('ProductCategory', () {
    test('all categories defined', () {
      expect(ProductCategory.values.length, 7);
      expect(ProductCategory.values, contains(ProductCategory.harvest));
      expect(ProductCategory.values, contains(ProductCategory.seeds));
      expect(ProductCategory.values, contains(ProductCategory.fertilizer));
      expect(ProductCategory.values, contains(ProductCategory.pesticide));
      expect(ProductCategory.values, contains(ProductCategory.equipment));
      expect(ProductCategory.values, contains(ProductCategory.irrigation));
      expect(ProductCategory.values, contains(ProductCategory.other));
    });
  });

  group('SellerType', () {
    test('all seller types defined', () {
      expect(SellerType.values.length, 3);
      expect(SellerType.values, contains(SellerType.farmer));
      expect(SellerType.values, contains(SellerType.company));
      expect(SellerType.values, contains(SellerType.cooperative));
    });
  });

  group('Product', () {
    late Product product;

    setUp(() {
      product = Product(
        id: 'p1',
        name: 'Wheat',
        nameAr: 'قمح',
        category: ProductCategory.harvest,
        price: 1850.0,
        stock: 100.0,
        unit: 'ton',
        description: 'Fresh wheat',
        descriptionAr: 'قمح طازج',
        sellerId: 'seller-1',
        sellerType: SellerType.farmer,
        sellerName: 'Farm A',
        governorate: 'Riyadh',
        cropType: 'wheat',
        qualityGrade: 'A',
        featured: true,
        createdAt: DateTime(2026, 3, 1),
      );
    });

    test('fromJson parses correctly', () {
      final json = {
        'id': 'p2',
        'name': 'Seeds',
        'nameAr': 'بذور',
        'category': 'SEEDS',
        'price': 50.0,
        'stock': 200,
        'unit': 'kg',
        'sellerId': 'seller-2',
        'sellerType': 'COMPANY',
        'featured': false,
        'createdAt': '2026-03-10T00:00:00.000Z',
      };

      final p = Product.fromJson(json);
      expect(p.id, 'p2');
      expect(p.name, 'Seeds');
      expect(p.category, ProductCategory.seeds);
      expect(p.price, 50.0);
      expect(p.sellerType, SellerType.company);
      expect(p.featured, false);
    });

    test('fromJson defaults nameAr to name when absent', () {
      final json = {
        'id': 'p3',
        'name': 'Seeds',
        'category': 'SEEDS',
        'price': 50.0,
        'stock': 200,
        'unit': 'kg',
        'sellerId': 'seller-2',
        'createdAt': '2026-03-10T00:00:00.000Z',
      };

      final p = Product.fromJson(json);
      expect(p.nameAr, 'Seeds');
    });

    test('fromJson parses unknown category as other', () {
      final json = {
        'id': 'p4',
        'name': 'Something',
        'category': 'UNKNOWN',
        'price': 10.0,
        'stock': 5,
        'unit': 'unit',
        'sellerId': 'seller-3',
        'createdAt': '2026-03-10T00:00:00.000Z',
      };

      final p = Product.fromJson(json);
      expect(p.category, ProductCategory.other);
    });

    test('fromJson parses unknown sellerType as farmer', () {
      final json = {
        'id': 'p5',
        'name': 'Item',
        'category': 'HARVEST',
        'price': 10.0,
        'stock': 5,
        'unit': 'unit',
        'sellerId': 'seller-4',
        'sellerType': 'UNKNOWN',
        'createdAt': '2026-03-10T00:00:00.000Z',
      };

      final p = Product.fromJson(json);
      expect(p.sellerType, SellerType.farmer);
    });

    test('fromJson parses COOPERATIVE sellerType', () {
      final json = {
        'id': 'p6',
        'name': 'Item',
        'category': 'HARVEST',
        'price': 10.0,
        'stock': 5,
        'unit': 'unit',
        'sellerId': 'seller-5',
        'sellerType': 'COOPERATIVE',
        'createdAt': '2026-03-10T00:00:00.000Z',
      };

      final p = Product.fromJson(json);
      expect(p.sellerType, SellerType.cooperative);
    });

    test('categoryIcon returns correct emoji', () {
      expect(product.categoryIcon, '🌾');

      final seedProduct = Product(
        id: 'x', name: 'x', nameAr: 'x',
        category: ProductCategory.seeds,
        price: 1, stock: 1, unit: 'kg',
        sellerId: 's', sellerType: SellerType.farmer,
        createdAt: DateTime.now(),
      );
      expect(seedProduct.categoryIcon, '🌱');
    });

    test('categoryNameAr returns correct Arabic name', () {
      expect(product.categoryNameAr, 'محاصيل');
    });

    test('unitAr returns correct Arabic unit', () {
      expect(product.unitAr, 'طن');

      final kgProduct = Product(
        id: 'x', name: 'x', nameAr: 'x',
        category: ProductCategory.seeds,
        price: 1, stock: 1, unit: 'kg',
        sellerId: 's', sellerType: SellerType.farmer,
        createdAt: DateTime.now(),
      );
      expect(kgProduct.unitAr, 'كجم');
    });

    test('unitAr returns original unit for unknown units', () {
      final customProduct = Product(
        id: 'x', name: 'x', nameAr: 'x',
        category: ProductCategory.other,
        price: 1, stock: 1, unit: 'box',
        sellerId: 's', sellerType: SellerType.farmer,
        createdAt: DateTime.now(),
      );
      expect(customProduct.unitAr, 'box');
    });

    test('all category icons are non-empty', () {
      for (final category in ProductCategory.values) {
        final p = Product(
          id: 'x', name: 'x', nameAr: 'x',
          category: category,
          price: 1, stock: 1, unit: 'unit',
          sellerId: 's', sellerType: SellerType.farmer,
          createdAt: DateTime.now(),
        );
        expect(p.categoryIcon.isNotEmpty, true);
      }
    });

    test('all category Arabic names are non-empty', () {
      for (final category in ProductCategory.values) {
        final p = Product(
          id: 'x', name: 'x', nameAr: 'x',
          category: category,
          price: 1, stock: 1, unit: 'unit',
          sellerId: 's', sellerType: SellerType.farmer,
          createdAt: DateTime.now(),
        );
        expect(p.categoryNameAr.isNotEmpty, true);
      }
    });

    test('all product categories parse correctly', () {
      final categories = {
        'HARVEST': ProductCategory.harvest,
        'SEEDS': ProductCategory.seeds,
        'FERTILIZER': ProductCategory.fertilizer,
        'PESTICIDE': ProductCategory.pesticide,
        'EQUIPMENT': ProductCategory.equipment,
        'IRRIGATION': ProductCategory.irrigation,
      };

      for (final entry in categories.entries) {
        final json = {
          'id': 'x', 'name': 'x', 'category': entry.key,
          'price': 1, 'stock': 1, 'unit': 'unit', 'sellerId': 's',
          'createdAt': '2026-01-01T00:00:00.000Z',
        };
        final p = Product.fromJson(json);
        expect(p.category, entry.value);
      }
    });
  });

  group('CartItem', () {
    late Product product;

    setUp(() {
      product = Product(
        id: 'p1',
        name: 'Wheat',
        nameAr: 'قمح',
        category: ProductCategory.harvest,
        price: 1850.0,
        stock: 100.0,
        unit: 'ton',
        sellerId: 'seller-1',
        sellerType: SellerType.farmer,
        createdAt: DateTime(2026, 3, 1),
      );
    });

    test('totalPrice calculates correctly', () {
      final item = CartItem(product: product, quantity: 2.5);
      expect(item.totalPrice, 4625.0);
    });

    test('copyWith updates quantity', () {
      final item = CartItem(product: product, quantity: 1);
      final updated = item.copyWith(quantity: 3);
      expect(updated.quantity, 3);
      expect(updated.product.id, 'p1');
    });

    test('copyWith preserves quantity when not specified', () {
      final item = CartItem(product: product, quantity: 5);
      final updated = item.copyWith();
      expect(updated.quantity, 5);
    });
  });

  group('Order', () {
    test('fromJson parses correctly', () {
      final json = {
        'id': 'ord-1',
        'orderNumber': 'ORD-2026-001',
        'buyerId': 'buyer-1',
        'subtotal': 1000.0,
        'deliveryFee': 50.0,
        'serviceFee': 25.0,
        'totalAmount': 1075.0,
        'status': 'PENDING',
        'createdAt': '2026-03-14T10:00:00.000Z',
      };

      final order = Order.fromJson(json);
      expect(order.id, 'ord-1');
      expect(order.orderNumber, 'ORD-2026-001');
      expect(order.subtotal, 1000.0);
      expect(order.deliveryFee, 50.0);
      expect(order.serviceFee, 25.0);
      expect(order.totalAmount, 1075.0);
    });

    test('fromJson defaults fees to 0', () {
      final json = {
        'id': 'ord-2',
        'orderNumber': 'ORD-002',
        'buyerId': 'buyer-2',
        'subtotal': 500.0,
        'totalAmount': 500.0,
        'status': 'CONFIRMED',
        'createdAt': '2026-03-14T10:00:00.000Z',
      };

      final order = Order.fromJson(json);
      expect(order.deliveryFee, 0);
      expect(order.serviceFee, 0);
    });

    test('statusAr returns correct Arabic status', () {
      const statuses = {
        'PENDING': 'قيد الانتظار',
        'CONFIRMED': 'مؤكد',
        'PROCESSING': 'جاري التجهيز',
        'SHIPPED': 'تم الشحن',
        'DELIVERED': 'تم التسليم',
        'CANCELLED': 'ملغي',
      };

      for (final entry in statuses.entries) {
        final order = Order(
          id: 'x', orderNumber: 'x', buyerId: 'x',
          subtotal: 0, deliveryFee: 0, serviceFee: 0,
          totalAmount: 0, status: entry.key,
          createdAt: DateTime.now(),
        );
        expect(order.statusAr, entry.value);
      }
    });

    test('statusAr returns raw status for unknown values', () {
      final order = Order(
        id: 'x', orderNumber: 'x', buyerId: 'x',
        subtotal: 0, deliveryFee: 0, serviceFee: 0,
        totalAmount: 0, status: 'CUSTOM_STATUS',
        createdAt: DateTime.now(),
      );
      expect(order.statusAr, 'CUSTOM_STATUS');
    });
  });

  group('MarketplaceState', () {
    test('default state is empty', () {
      const state = MarketplaceState();
      expect(state.products, isEmpty);
      expect(state.featuredProducts, isEmpty);
      expect(state.cart, isEmpty);
      expect(state.orders, isEmpty);
      expect(state.selectedCategory, isNull);
      expect(state.isLoading, false);
      expect(state.error, isNull);
    });

    test('cartTotal calculates sum of all items', () {
      final p1 = Product(
        id: 'p1', name: 'x', nameAr: 'x',
        category: ProductCategory.harvest,
        price: 100, stock: 10, unit: 'kg',
        sellerId: 's', sellerType: SellerType.farmer,
        createdAt: DateTime.now(),
      );
      final p2 = Product(
        id: 'p2', name: 'y', nameAr: 'y',
        category: ProductCategory.seeds,
        price: 50, stock: 10, unit: 'kg',
        sellerId: 's', sellerType: SellerType.farmer,
        createdAt: DateTime.now(),
      );

      final state = MarketplaceState(
        cart: [
          CartItem(product: p1, quantity: 2),
          CartItem(product: p2, quantity: 3),
        ],
      );

      expect(state.cartTotal, 350.0);
    });

    test('cartItemCount returns number of items', () {
      final p1 = Product(
        id: 'p1', name: 'x', nameAr: 'x',
        category: ProductCategory.harvest,
        price: 100, stock: 10, unit: 'kg',
        sellerId: 's', sellerType: SellerType.farmer,
        createdAt: DateTime.now(),
      );

      final state = MarketplaceState(
        cart: [CartItem(product: p1, quantity: 5)],
      );

      expect(state.cartItemCount, 1);
    });

    test('isCartEmpty is true for empty cart', () {
      const state = MarketplaceState();
      expect(state.isCartEmpty, true);
    });

    test('isCartEmpty is false for non-empty cart', () {
      final p1 = Product(
        id: 'p1', name: 'x', nameAr: 'x',
        category: ProductCategory.harvest,
        price: 100, stock: 10, unit: 'kg',
        sellerId: 's', sellerType: SellerType.farmer,
        createdAt: DateTime.now(),
      );

      final state = MarketplaceState(
        cart: [CartItem(product: p1, quantity: 1)],
      );

      expect(state.isCartEmpty, false);
    });

    test('copyWith with clearCategory clears category', () {
      const state = MarketplaceState(
        selectedCategory: ProductCategory.harvest,
      );
      final copied = state.copyWith(clearCategory: true);
      expect(copied.selectedCategory, isNull);
    });

    test('copyWith preserves category when clearCategory is false', () {
      const state = MarketplaceState(
        selectedCategory: ProductCategory.harvest,
      );
      final copied = state.copyWith();
      expect(copied.selectedCategory, ProductCategory.harvest);
    });
  });

  group('MarketplaceNotifier cart operations', () {
    late MarketplaceNotifier notifier;
    late Product product1;
    late Product product2;

    setUp(() {
      // Create notifier - it calls loadProducts in constructor which will fail
      // since there's no server, but cart operations are local
      notifier = MarketplaceNotifier(
        baseUrl: 'http://localhost:9999',
        userId: 'test-user',
      );

      product1 = Product(
        id: 'p1', name: 'Wheat', nameAr: 'قمح',
        category: ProductCategory.harvest,
        price: 1850, stock: 100, unit: 'ton',
        sellerId: 's1', sellerType: SellerType.farmer,
        createdAt: DateTime(2026, 3, 1),
      );

      product2 = Product(
        id: 'p2', name: 'Seeds', nameAr: 'بذور',
        category: ProductCategory.seeds,
        price: 50, stock: 200, unit: 'kg',
        sellerId: 's2', sellerType: SellerType.company,
        createdAt: DateTime(2026, 3, 1),
      );
    });

    test('addToCart adds new item', () {
      notifier.addToCart(product1, quantity: 2);
      expect(notifier.state.cart.length, 1);
      expect(notifier.state.cart.first.quantity, 2);
    });

    test('addToCart updates quantity for existing item', () {
      notifier.addToCart(product1, quantity: 2);
      notifier.addToCart(product1, quantity: 3);
      expect(notifier.state.cart.length, 1);
      expect(notifier.state.cart.first.quantity, 5);
    });

    test('addToCart allows multiple products', () {
      notifier.addToCart(product1);
      notifier.addToCart(product2);
      expect(notifier.state.cart.length, 2);
    });

    test('removeFromCart removes item by productId', () {
      notifier.addToCart(product1);
      notifier.addToCart(product2);
      notifier.removeFromCart('p1');
      expect(notifier.state.cart.length, 1);
      expect(notifier.state.cart.first.product.id, 'p2');
    });

    test('removeFromCart does nothing for non-existent id', () {
      notifier.addToCart(product1);
      notifier.removeFromCart('nonexistent');
      expect(notifier.state.cart.length, 1);
    });

    test('updateCartQuantity updates quantity', () {
      notifier.addToCart(product1, quantity: 1);
      notifier.updateCartQuantity('p1', 5);
      expect(notifier.state.cart.first.quantity, 5);
    });

    test('updateCartQuantity with 0 removes item', () {
      notifier.addToCart(product1, quantity: 1);
      notifier.updateCartQuantity('p1', 0);
      expect(notifier.state.cart, isEmpty);
    });

    test('updateCartQuantity with negative removes item', () {
      notifier.addToCart(product1, quantity: 1);
      notifier.updateCartQuantity('p1', -1);
      expect(notifier.state.cart, isEmpty);
    });

    test('clearCart empties the cart', () {
      notifier.addToCart(product1);
      notifier.addToCart(product2);
      notifier.clearCart();
      expect(notifier.state.isCartEmpty, true);
    });

    test('createOrder returns null for empty cart', () async {
      final order = await notifier.createOrder();
      expect(order, isNull);
    });
  });
}
