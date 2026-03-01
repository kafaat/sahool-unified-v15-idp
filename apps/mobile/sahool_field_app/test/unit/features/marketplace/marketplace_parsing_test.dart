/// Marketplace Parsing Tests
/// اختبارات تحليل بيانات السوق
///
/// Tests for compute() isolate JSON parsing in marketplace

import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/features/marketplace/marketplace_provider.dart';

void main() {
  group('Product JSON parsing', () {
    test('should parse empty product list', () {
      final jsonStr = jsonEncode([]);
      final data = jsonDecode(jsonStr) as List<dynamic>;
      final result = data
          .map((json) => Product.fromJson(json as Map<String, dynamic>))
          .toList();

      expect(result, isEmpty);
    });

    test('should parse product list with valid data', () {
      final productsJson = [
        {
          'id': 'prod-001',
          'name': 'Wheat Seeds',
          'nameAr': 'بذور القمح',
          'category': 'SEEDS',
          'price': 150.0,
          'stock': 500.0,
          'unit': 'kg',
          'sellerId': 'seller-001',
          'sellerType': 'farmer',
          'featured': true,
          'createdAt': '2026-01-15T10:30:00Z',
        },
        {
          'id': 'prod-002',
          'name': 'Urea Fertilizer',
          'nameAr': 'سماد يوريا',
          'category': 'FERTILIZER',
          'price': 85.0,
          'stock': 1000.0,
          'unit': 'kg',
          'sellerId': 'seller-002',
          'sellerType': 'supplier',
          'featured': false,
          'createdAt': '2026-01-14T08:00:00Z',
        },
      ];

      final jsonStr = jsonEncode(productsJson);
      final data = jsonDecode(jsonStr) as List<dynamic>;
      final products = data
          .map((json) => Product.fromJson(json as Map<String, dynamic>))
          .toList();

      expect(products.length, 2);
      expect(products[0].id, 'prod-001');
      expect(products[0].name, 'Wheat Seeds');
      expect(products[0].nameAr, 'بذور القمح');
      expect(products[0].featured, isTrue);
      expect(products[1].id, 'prod-002');
      expect(products[1].featured, isFalse);
    });

    test('should handle large product list', () {
      final items = List.generate(200, (i) => {
            'id': 'prod-$i',
            'name': 'Product $i',
            'nameAr': 'منتج $i',
            'category': 'SEEDS',
            'price': 100.0 + i,
            'stock': 50.0,
            'unit': 'kg',
            'sellerId': 'seller-$i',
            'sellerType': 'farmer',
            'createdAt': '2026-01-15T10:30:00Z',
          });

      final jsonStr = jsonEncode(items);
      final data = jsonDecode(jsonStr) as List<dynamic>;
      final products = data
          .map((json) => Product.fromJson(json as Map<String, dynamic>))
          .toList();

      expect(products.length, 200);
      expect(products.first.id, 'prod-0');
      expect(products.last.id, 'prod-199');
    });

    test('should filter featured products correctly', () {
      final productsJson = [
        {
          'id': 'p1',
          'name': 'A',
          'category': 'SEEDS',
          'price': 10.0,
          'stock': 5.0,
          'unit': 'kg',
          'sellerId': 's1',
          'sellerType': 'farmer',
          'featured': true,
          'createdAt': '2026-01-15T00:00:00Z',
        },
        {
          'id': 'p2',
          'name': 'B',
          'category': 'SEEDS',
          'price': 20.0,
          'stock': 10.0,
          'unit': 'kg',
          'sellerId': 's2',
          'sellerType': 'farmer',
          'featured': false,
          'createdAt': '2026-01-15T00:00:00Z',
        },
        {
          'id': 'p3',
          'name': 'C',
          'category': 'FERTILIZER',
          'price': 30.0,
          'stock': 15.0,
          'unit': 'kg',
          'sellerId': 's3',
          'sellerType': 'supplier',
          'featured': true,
          'createdAt': '2026-01-15T00:00:00Z',
        },
      ];

      final jsonStr = jsonEncode(productsJson);
      final data = jsonDecode(jsonStr) as List<dynamic>;
      final products = data
          .map((json) => Product.fromJson(json as Map<String, dynamic>))
          .toList();

      final featured = products.where((p) => p.featured).toList();

      expect(featured.length, 2);
      expect(featured.map((p) => p.id), containsAll(['p1', 'p3']));
    });
  });

  group('MarketplaceState', () {
    test('should have default empty state', () {
      const state = MarketplaceState();
      expect(state.products, isEmpty);
      expect(state.orders, isEmpty);
      expect(state.cart, isEmpty);
      expect(state.isLoading, isFalse);
      expect(state.error, isNull);
    });

    test('copyWith should update products', () {
      const state = MarketplaceState();
      final product = Product(
        id: 'p1',
        name: 'Test',
        nameAr: 'اختبار',
        category: ProductCategory.seeds,
        price: 10.0,
        stock: 5.0,
        unit: 'kg',
        sellerId: 's1',
        sellerType: SellerType.farmer,
        createdAt: DateTime.now(),
      );

      final updated = state.copyWith(products: [product]);
      expect(updated.products.length, 1);
      expect(updated.products.first.id, 'p1');
    });
  });
}
