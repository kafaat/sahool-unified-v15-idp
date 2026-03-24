/// Marketplace Models Comprehensive Tests
/// اختبارات شاملة لنماذج السوق
///
/// Tests all marketplace models: Product, CartItem, Order, MarketplaceState
/// including enum parsing, Arabic localization, and computed properties.

import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/features/marketplace/marketplace_provider.dart';

void main() {
  // =========================================================================
  // ProductCategory Enum
  // =========================================================================

  group('ProductCategory', () {
    test('has exactly 7 values', () {
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

  // =========================================================================
  // SellerType Enum
  // =========================================================================

  group('SellerType', () {
    test('has exactly 3 values', () {
      expect(SellerType.values.length, 3);
    });

    test('contains all expected values', () {
      expect(SellerType.values, contains(SellerType.farmer));
      expect(SellerType.values, contains(SellerType.company));
      expect(SellerType.values, contains(SellerType.cooperative));
    });
  });

  // =========================================================================
  // Product
  // =========================================================================

  group('Product', () {
    /// Helper to create a full JSON map for Product.fromJson
    Map<String, dynamic> fullProductJson({
      String id = 'prod-001',
      String name = 'Premium Wheat',
      String nameAr = 'قمح ممتاز',
      String category = 'HARVEST',
      double price = 1850.0,
      num stock = 100,
      String unit = 'ton',
      String? description = 'High-quality wheat harvest',
      String? descriptionAr = 'محصول قمح عالي الجودة',
      String? imageUrl = 'https://example.com/wheat.jpg',
      String sellerId = 'seller-001',
      String? sellerType = 'FARMER',
      String? sellerName = 'Al-Rashid Farm',
      String? governorate = 'Sana\'a',
      String? cropType = 'wheat',
      String? qualityGrade = 'A',
      bool featured = true,
      String createdAt = '2026-03-15T08:30:00.000Z',
    }) {
      return {
        'id': id,
        'name': name,
        'nameAr': nameAr,
        'category': category,
        'price': price,
        'stock': stock,
        'unit': unit,
        'description': description,
        'descriptionAr': descriptionAr,
        'imageUrl': imageUrl,
        'sellerId': sellerId,
        'sellerType': sellerType,
        'sellerName': sellerName,
        'governorate': governorate,
        'cropType': cropType,
        'qualityGrade': qualityGrade,
        'featured': featured,
        'createdAt': createdAt,
      };
    }

    group('fromJson', () {
      test('parses all fields correctly', () {
        final json = fullProductJson();
        final product = Product.fromJson(json);

        expect(product.id, 'prod-001');
        expect(product.name, 'Premium Wheat');
        expect(product.nameAr, 'قمح ممتاز');
        expect(product.category, ProductCategory.harvest);
        expect(product.price, 1850.0);
        expect(product.stock, 100.0);
        expect(product.unit, 'ton');
        expect(product.description, 'High-quality wheat harvest');
        expect(product.descriptionAr, 'محصول قمح عالي الجودة');
        expect(product.imageUrl, 'https://example.com/wheat.jpg');
        expect(product.sellerId, 'seller-001');
        expect(product.sellerType, SellerType.farmer);
        expect(product.sellerName, 'Al-Rashid Farm');
        expect(product.governorate, 'Sana\'a');
        expect(product.cropType, 'wheat');
        expect(product.qualityGrade, 'A');
        expect(product.featured, true);
        expect(product.createdAt, DateTime.utc(2026, 3, 15, 8, 30));
      });

      test('defaults nameAr to name when absent', () {
        final json = {
          'id': 'p1',
          'name': 'Wheat Seeds',
          'category': 'SEEDS',
          'price': 50.0,
          'stock': 200,
          'unit': 'kg',
          'sellerId': 'seller-1',
          'createdAt': '2026-03-10T00:00:00.000Z',
        };

        final product = Product.fromJson(json);
        expect(product.nameAr, 'Wheat Seeds');
      });

      test('defaults unit to "unit" when absent', () {
        final json = {
          'id': 'p1',
          'name': 'Item',
          'category': 'OTHER',
          'price': 10.0,
          'stock': 5,
          'sellerId': 'seller-1',
          'createdAt': '2026-01-01T00:00:00.000Z',
        };

        final product = Product.fromJson(json);
        expect(product.unit, 'unit');
      });

      test('defaults featured to false when absent', () {
        final json = {
          'id': 'p1',
          'name': 'Item',
          'category': 'HARVEST',
          'price': 10.0,
          'stock': 5,
          'unit': 'kg',
          'sellerId': 'seller-1',
          'createdAt': '2026-01-01T00:00:00.000Z',
        };

        final product = Product.fromJson(json);
        expect(product.featured, false);
      });

      test('handles minimal fields (all optional fields null)', () {
        final json = {
          'id': 'p-min',
          'name': 'Minimal Product',
          'category': 'SEEDS',
          'price': 25,
          'stock': 10,
          'sellerId': 'seller-min',
          'createdAt': '2026-02-20T12:00:00.000Z',
        };

        final product = Product.fromJson(json);
        expect(product.id, 'p-min');
        expect(product.nameAr, 'Minimal Product'); // defaults to name
        expect(product.unit, 'unit'); // defaults to 'unit'
        expect(product.description, isNull);
        expect(product.descriptionAr, isNull);
        expect(product.imageUrl, isNull);
        expect(product.sellerType, SellerType.farmer); // null -> farmer
        expect(product.sellerName, isNull);
        expect(product.governorate, isNull);
        expect(product.cropType, isNull);
        expect(product.qualityGrade, isNull);
        expect(product.featured, false); // defaults to false
      });

      test('handles integer stock value via num.toDouble()', () {
        final json = fullProductJson(stock: 42);
        final product = Product.fromJson(json);
        expect(product.stock, 42.0);
        expect(product.stock, isA<double>());
      });

      test('uses DateTime.now() when createdAt is null', () {
        final json = {
          'id': 'p1',
          'name': 'Item',
          'category': 'HARVEST',
          'price': 10.0,
          'stock': 5,
          'unit': 'kg',
          'sellerId': 'seller-1',
          // no createdAt
        };

        final before = DateTime.now();
        final product = Product.fromJson(json);
        final after = DateTime.now();

        expect(product.createdAt.isAfter(before.subtract(const Duration(seconds: 1))), isTrue);
        expect(product.createdAt.isBefore(after.add(const Duration(seconds: 1))), isTrue);
      });
    });

    group('_parseCategory', () {
      test('HARVEST returns harvest', () {
        final p = Product.fromJson(fullProductJson(category: 'HARVEST'));
        expect(p.category, ProductCategory.harvest);
      });

      test('SEEDS returns seeds', () {
        final p = Product.fromJson(fullProductJson(category: 'SEEDS'));
        expect(p.category, ProductCategory.seeds);
      });

      test('FERTILIZER returns fertilizer', () {
        final p = Product.fromJson(fullProductJson(category: 'FERTILIZER'));
        expect(p.category, ProductCategory.fertilizer);
      });

      test('PESTICIDE returns pesticide', () {
        final p = Product.fromJson(fullProductJson(category: 'PESTICIDE'));
        expect(p.category, ProductCategory.pesticide);
      });

      test('EQUIPMENT returns equipment', () {
        final p = Product.fromJson(fullProductJson(category: 'EQUIPMENT'));
        expect(p.category, ProductCategory.equipment);
      });

      test('IRRIGATION returns irrigation', () {
        final p = Product.fromJson(fullProductJson(category: 'IRRIGATION'));
        expect(p.category, ProductCategory.irrigation);
      });

      test('null category returns other', () {
        final json = fullProductJson();
        json['category'] = null;
        final p = Product.fromJson(json);
        expect(p.category, ProductCategory.other);
      });

      test('unknown category returns other', () {
        final p = Product.fromJson(fullProductJson(category: 'UNKNOWN'));
        expect(p.category, ProductCategory.other);
      });

      test('lowercase category is handled via toUpperCase', () {
        final p = Product.fromJson(fullProductJson(category: 'harvest'));
        expect(p.category, ProductCategory.harvest);
      });

      test('mixed case category is handled via toUpperCase', () {
        final p = Product.fromJson(fullProductJson(category: 'Seeds'));
        expect(p.category, ProductCategory.seeds);
      });
    });

    group('_parseSellerType', () {
      test('COMPANY returns company', () {
        final p = Product.fromJson(fullProductJson(sellerType: 'COMPANY'));
        expect(p.sellerType, SellerType.company);
      });

      test('COOPERATIVE returns cooperative', () {
        final p = Product.fromJson(fullProductJson(sellerType: 'COOPERATIVE'));
        expect(p.sellerType, SellerType.cooperative);
      });

      test('FARMER returns farmer (default branch)', () {
        final p = Product.fromJson(fullProductJson(sellerType: 'FARMER'));
        expect(p.sellerType, SellerType.farmer);
      });

      test('null sellerType returns farmer', () {
        final json = fullProductJson();
        json['sellerType'] = null;
        final p = Product.fromJson(json);
        expect(p.sellerType, SellerType.farmer);
      });

      test('unknown sellerType returns farmer', () {
        final p = Product.fromJson(fullProductJson(sellerType: 'SUPPLIER'));
        expect(p.sellerType, SellerType.farmer);
      });

      test('lowercase company is handled via toUpperCase', () {
        final p = Product.fromJson(fullProductJson(sellerType: 'company'));
        expect(p.sellerType, SellerType.company);
      });
    });

    group('categoryIcon', () {
      Product _makeProduct(ProductCategory category) {
        return Product(
          id: 'x',
          name: 'x',
          nameAr: 'x',
          category: category,
          price: 1,
          stock: 1,
          unit: 'unit',
          sellerId: 's',
          sellerType: SellerType.farmer,
          createdAt: DateTime(2026),
        );
      }

      test('harvest returns wheat emoji', () {
        expect(_makeProduct(ProductCategory.harvest).categoryIcon, '\u{1F33E}');
      });

      test('seeds returns seedling emoji', () {
        expect(_makeProduct(ProductCategory.seeds).categoryIcon, '\u{1F331}');
      });

      test('fertilizer returns test tube emoji', () {
        expect(_makeProduct(ProductCategory.fertilizer).categoryIcon, '\u{1F9EA}');
      });

      test('pesticide returns shield emoji', () {
        expect(
          _makeProduct(ProductCategory.pesticide).categoryIcon,
          '\u{1F6E1}\u{FE0F}',
        );
      });

      test('equipment returns tractor emoji', () {
        expect(_makeProduct(ProductCategory.equipment).categoryIcon, '\u{1F69C}');
      });

      test('irrigation returns droplet emoji', () {
        expect(
          _makeProduct(ProductCategory.irrigation).categoryIcon,
          '\u{1F4A7}',
        );
      });

      test('other returns package emoji', () {
        expect(_makeProduct(ProductCategory.other).categoryIcon, '\u{1F4E6}');
      });

      test('every category has a non-empty icon', () {
        for (final category in ProductCategory.values) {
          final icon = _makeProduct(category).categoryIcon;
          expect(icon.isNotEmpty, isTrue,
              reason: 'Category $category should have a non-empty icon');
        }
      });
    });

    group('categoryNameAr', () {
      Product _makeProduct(ProductCategory category) {
        return Product(
          id: 'x',
          name: 'x',
          nameAr: 'x',
          category: category,
          price: 1,
          stock: 1,
          unit: 'unit',
          sellerId: 's',
          sellerType: SellerType.farmer,
          createdAt: DateTime(2026),
        );
      }

      test('harvest returns Arabic name', () {
        expect(_makeProduct(ProductCategory.harvest).categoryNameAr, 'محاصيل');
      });

      test('seeds returns Arabic name', () {
        expect(_makeProduct(ProductCategory.seeds).categoryNameAr, 'بذور');
      });

      test('fertilizer returns Arabic name', () {
        expect(_makeProduct(ProductCategory.fertilizer).categoryNameAr, 'أسمدة');
      });

      test('pesticide returns Arabic name', () {
        expect(_makeProduct(ProductCategory.pesticide).categoryNameAr, 'مبيدات');
      });

      test('equipment returns Arabic name', () {
        expect(_makeProduct(ProductCategory.equipment).categoryNameAr, 'معدات');
      });

      test('irrigation returns Arabic name', () {
        expect(_makeProduct(ProductCategory.irrigation).categoryNameAr, 'ري');
      });

      test('other returns Arabic name', () {
        expect(_makeProduct(ProductCategory.other).categoryNameAr, 'أخرى');
      });

      test('every category has a non-empty Arabic name', () {
        for (final category in ProductCategory.values) {
          final nameAr = _makeProduct(category).categoryNameAr;
          expect(nameAr.isNotEmpty, isTrue,
              reason: 'Category $category should have a non-empty Arabic name');
        }
      });
    });

    group('unitAr', () {
      Product _makeProductWithUnit(String unit) {
        return Product(
          id: 'x',
          name: 'x',
          nameAr: 'x',
          category: ProductCategory.other,
          price: 1,
          stock: 1,
          unit: unit,
          sellerId: 's',
          sellerType: SellerType.farmer,
          createdAt: DateTime(2026),
        );
      }

      test('ton returns Arabic translation', () {
        expect(_makeProductWithUnit('ton').unitAr, 'طن');
      });

      test('kg returns Arabic translation', () {
        expect(_makeProductWithUnit('kg').unitAr, 'كجم');
      });

      test('unit returns Arabic translation', () {
        expect(_makeProductWithUnit('unit').unitAr, 'قطعة');
      });

      test('liter returns Arabic translation', () {
        expect(_makeProductWithUnit('liter').unitAr, 'لتر');
      });

      test('bag returns Arabic translation', () {
        expect(_makeProductWithUnit('bag').unitAr, 'كيس');
      });

      test('unknown unit returns the original unit string', () {
        expect(_makeProductWithUnit('box').unitAr, 'box');
      });

      test('another unknown unit returns the original unit string', () {
        expect(_makeProductWithUnit('gallon').unitAr, 'gallon');
      });

      test('handles uppercase unit via toLowerCase', () {
        expect(_makeProductWithUnit('TON').unitAr, 'طن');
      });

      test('handles mixed case unit via toLowerCase', () {
        expect(_makeProductWithUnit('Kg').unitAr, 'كجم');
      });
    });
  });

  // =========================================================================
  // CartItem
  // =========================================================================

  group('CartItem', () {
    late Product product;

    setUp(() {
      product = Product(
        id: 'cart-prod-1',
        name: 'Urea Fertilizer',
        nameAr: 'سماد يوريا',
        category: ProductCategory.fertilizer,
        price: 120.0,
        stock: 500.0,
        unit: 'bag',
        sellerId: 'seller-100',
        sellerType: SellerType.company,
        createdAt: DateTime(2026, 3, 1),
      );
    });

    test('construction with required fields', () {
      final item = CartItem(product: product, quantity: 3.0);

      expect(item.product.id, 'cart-prod-1');
      expect(item.quantity, 3.0);
    });

    test('totalPrice calculates price * quantity', () {
      final item = CartItem(product: product, quantity: 5.0);
      expect(item.totalPrice, 600.0); // 120.0 * 5.0
    });

    test('totalPrice with fractional quantity', () {
      final item = CartItem(product: product, quantity: 2.5);
      expect(item.totalPrice, 300.0); // 120.0 * 2.5
    });

    test('totalPrice with quantity of 1', () {
      final item = CartItem(product: product, quantity: 1.0);
      expect(item.totalPrice, 120.0);
    });

    test('copyWith changes quantity', () {
      final item = CartItem(product: product, quantity: 2.0);
      final updated = item.copyWith(quantity: 7.0);

      expect(updated.quantity, 7.0);
      expect(updated.product.id, product.id);
    });

    test('copyWith preserves quantity when not specified', () {
      final item = CartItem(product: product, quantity: 4.0);
      final updated = item.copyWith();

      expect(updated.quantity, 4.0);
      expect(updated.product.id, product.id);
    });

    test('copyWith preserves product reference', () {
      final item = CartItem(product: product, quantity: 1.0);
      final updated = item.copyWith(quantity: 10.0);

      expect(identical(updated.product, product), isTrue);
    });
  });

  // =========================================================================
  // Order
  // =========================================================================

  group('Order', () {
    group('fromJson', () {
      test('parses all fields correctly', () {
        final json = {
          'id': 'ord-100',
          'orderNumber': 'ORD-2026-100',
          'buyerId': 'buyer-abc',
          'subtotal': 3700.0,
          'deliveryFee': 150.0,
          'serviceFee': 75.0,
          'totalAmount': 3925.0,
          'status': 'PENDING',
          'createdAt': '2026-03-20T14:30:00.000Z',
        };

        final order = Order.fromJson(json);

        expect(order.id, 'ord-100');
        expect(order.orderNumber, 'ORD-2026-100');
        expect(order.buyerId, 'buyer-abc');
        expect(order.subtotal, 3700.0);
        expect(order.deliveryFee, 150.0);
        expect(order.serviceFee, 75.0);
        expect(order.totalAmount, 3925.0);
        expect(order.status, 'PENDING');
        expect(order.createdAt, DateTime.utc(2026, 3, 20, 14, 30));
      });

      test('defaults deliveryFee to 0 when absent', () {
        final json = {
          'id': 'ord-200',
          'orderNumber': 'ORD-002',
          'buyerId': 'buyer-def',
          'subtotal': 500.0,
          'totalAmount': 500.0,
          'status': 'CONFIRMED',
          'createdAt': '2026-03-15T10:00:00.000Z',
        };

        final order = Order.fromJson(json);
        expect(order.deliveryFee, 0.0);
      });

      test('defaults serviceFee to 0 when absent', () {
        final json = {
          'id': 'ord-201',
          'orderNumber': 'ORD-003',
          'buyerId': 'buyer-ghi',
          'subtotal': 800.0,
          'totalAmount': 800.0,
          'status': 'PROCESSING',
          'createdAt': '2026-03-15T10:00:00.000Z',
        };

        final order = Order.fromJson(json);
        expect(order.serviceFee, 0.0);
      });

      test('defaults both fees to 0 when absent', () {
        final json = {
          'id': 'ord-202',
          'orderNumber': 'ORD-004',
          'buyerId': 'buyer-jkl',
          'subtotal': 250.0,
          'totalAmount': 250.0,
          'status': 'DELIVERED',
          'createdAt': '2026-03-15T10:00:00.000Z',
        };

        final order = Order.fromJson(json);
        expect(order.deliveryFee, 0.0);
        expect(order.serviceFee, 0.0);
      });

      test('handles integer numeric values via num.toDouble()', () {
        final json = {
          'id': 'ord-int',
          'orderNumber': 'ORD-INT',
          'buyerId': 'buyer-int',
          'subtotal': 1000,
          'deliveryFee': 50,
          'serviceFee': 25,
          'totalAmount': 1075,
          'status': 'PENDING',
          'createdAt': '2026-01-01T00:00:00.000Z',
        };

        final order = Order.fromJson(json);
        expect(order.subtotal, 1000.0);
        expect(order.subtotal, isA<double>());
        expect(order.deliveryFee, 50.0);
        expect(order.serviceFee, 25.0);
        expect(order.totalAmount, 1075.0);
      });
    });

    group('statusAr', () {
      Order _makeOrderWithStatus(String status) {
        return Order(
          id: 'x',
          orderNumber: 'x',
          buyerId: 'x',
          subtotal: 0,
          deliveryFee: 0,
          serviceFee: 0,
          totalAmount: 0,
          status: status,
          createdAt: DateTime(2026),
        );
      }

      test('PENDING returns Arabic status', () {
        expect(_makeOrderWithStatus('PENDING').statusAr, 'قيد الانتظار');
      });

      test('CONFIRMED returns Arabic status', () {
        expect(_makeOrderWithStatus('CONFIRMED').statusAr, 'مؤكد');
      });

      test('PROCESSING returns Arabic status', () {
        expect(_makeOrderWithStatus('PROCESSING').statusAr, 'جاري التجهيز');
      });

      test('SHIPPED returns Arabic status', () {
        expect(_makeOrderWithStatus('SHIPPED').statusAr, 'تم الشحن');
      });

      test('DELIVERED returns Arabic status', () {
        expect(_makeOrderWithStatus('DELIVERED').statusAr, 'تم التسليم');
      });

      test('CANCELLED returns Arabic status', () {
        expect(_makeOrderWithStatus('CANCELLED').statusAr, 'ملغي');
      });

      test('unknown status returns raw status string', () {
        expect(_makeOrderWithStatus('REFUNDED').statusAr, 'REFUNDED');
      });

      test('lowercase status is handled via toUpperCase', () {
        expect(_makeOrderWithStatus('pending').statusAr, 'قيد الانتظار');
      });

      test('mixed case status is handled via toUpperCase', () {
        expect(_makeOrderWithStatus('Confirmed').statusAr, 'مؤكد');
      });
    });
  });

  // =========================================================================
  // MarketplaceState
  // =========================================================================

  group('MarketplaceState', () {
    Product _makeProduct({
      required String id,
      double price = 100.0,
    }) {
      return Product(
        id: id,
        name: 'Product $id',
        nameAr: 'منتج $id',
        category: ProductCategory.harvest,
        price: price,
        stock: 50,
        unit: 'kg',
        sellerId: 'seller-$id',
        sellerType: SellerType.farmer,
        createdAt: DateTime(2026, 3, 1),
      );
    }

    test('default values are correct', () {
      const state = MarketplaceState();

      expect(state.products, isEmpty);
      expect(state.featuredProducts, isEmpty);
      expect(state.cart, isEmpty);
      expect(state.orders, isEmpty);
      expect(state.selectedCategory, isNull);
      expect(state.isLoading, false);
      expect(state.error, isNull);
    });

    test('cartTotal with empty cart returns 0', () {
      const state = MarketplaceState();
      expect(state.cartTotal, 0.0);
    });

    test('cartTotal sums all items correctly', () {
      final p1 = _makeProduct(id: 'p1', price: 100.0);
      final p2 = _makeProduct(id: 'p2', price: 250.0);
      final p3 = _makeProduct(id: 'p3', price: 75.0);

      final state = MarketplaceState(
        cart: [
          CartItem(product: p1, quantity: 2.0),  // 200
          CartItem(product: p2, quantity: 1.0),  // 250
          CartItem(product: p3, quantity: 4.0),  // 300
        ],
      );

      expect(state.cartTotal, 750.0);
    });

    test('cartTotal with single item', () {
      final p1 = _makeProduct(id: 'p1', price: 1850.0);

      final state = MarketplaceState(
        cart: [CartItem(product: p1, quantity: 3.0)],
      );

      expect(state.cartTotal, 5550.0);
    });

    test('cartItemCount returns number of cart items', () {
      final p1 = _makeProduct(id: 'p1');
      final p2 = _makeProduct(id: 'p2');

      final state = MarketplaceState(
        cart: [
          CartItem(product: p1, quantity: 5.0),
          CartItem(product: p2, quantity: 3.0),
        ],
      );

      expect(state.cartItemCount, 2);
    });

    test('cartItemCount is 0 for empty cart', () {
      const state = MarketplaceState();
      expect(state.cartItemCount, 0);
    });

    test('isCartEmpty is true when cart is empty', () {
      const state = MarketplaceState();
      expect(state.isCartEmpty, true);
    });

    test('isCartEmpty is false when cart has items', () {
      final p1 = _makeProduct(id: 'p1');

      final state = MarketplaceState(
        cart: [CartItem(product: p1, quantity: 1.0)],
      );

      expect(state.isCartEmpty, false);
    });

    group('copyWith', () {
      test('updates products', () {
        const state = MarketplaceState();
        final p = _makeProduct(id: 'new-p');
        final updated = state.copyWith(products: [p]);

        expect(updated.products.length, 1);
        expect(updated.products.first.id, 'new-p');
      });

      test('updates featuredProducts', () {
        const state = MarketplaceState();
        final p = _makeProduct(id: 'feat');
        final updated = state.copyWith(featuredProducts: [p]);

        expect(updated.featuredProducts.length, 1);
      });

      test('updates cart', () {
        const state = MarketplaceState();
        final p = _makeProduct(id: 'c1');
        final updated = state.copyWith(
          cart: [CartItem(product: p, quantity: 2.0)],
        );

        expect(updated.cart.length, 1);
        expect(updated.cartTotal, 200.0);
      });

      test('updates isLoading', () {
        const state = MarketplaceState();
        final updated = state.copyWith(isLoading: true);
        expect(updated.isLoading, true);
      });

      test('updates error', () {
        const state = MarketplaceState();
        final updated = state.copyWith(error: 'Network error');
        expect(updated.error, 'Network error');
      });

      test('clears error when copyWith sets it to null', () {
        final state = const MarketplaceState().copyWith(error: 'Error');
        final updated = state.copyWith(error: null);
        // Note: copyWith uses `error: error` directly, so passing null clears it
        expect(updated.error, isNull);
      });

      test('updates selectedCategory', () {
        const state = MarketplaceState();
        final updated = state.copyWith(
          selectedCategory: ProductCategory.seeds,
        );
        expect(updated.selectedCategory, ProductCategory.seeds);
      });

      test('clearCategory sets selectedCategory to null', () {
        const state = MarketplaceState(
          selectedCategory: ProductCategory.harvest,
        );
        final updated = state.copyWith(clearCategory: true);
        expect(updated.selectedCategory, isNull);
      });

      test('clearCategory overrides selectedCategory parameter', () {
        const state = MarketplaceState(
          selectedCategory: ProductCategory.harvest,
        );
        // When clearCategory is true, selectedCategory param is ignored
        final updated = state.copyWith(
          selectedCategory: ProductCategory.seeds,
          clearCategory: true,
        );
        expect(updated.selectedCategory, isNull);
      });

      test('preserves existing selectedCategory when clearCategory is false', () {
        const state = MarketplaceState(
          selectedCategory: ProductCategory.equipment,
        );
        final updated = state.copyWith(isLoading: true);
        expect(updated.selectedCategory, ProductCategory.equipment);
      });

      test('preserves fields not specified in copyWith', () {
        final p = _makeProduct(id: 'p1');
        final state = MarketplaceState(
          products: [p],
          cart: [CartItem(product: p, quantity: 1.0)],
          isLoading: false,
          selectedCategory: ProductCategory.harvest,
        );

        final updated = state.copyWith(isLoading: true);

        expect(updated.products.length, 1);
        expect(updated.cart.length, 1);
        expect(updated.selectedCategory, ProductCategory.harvest);
        expect(updated.isLoading, true);
      });
    });
  });
}
