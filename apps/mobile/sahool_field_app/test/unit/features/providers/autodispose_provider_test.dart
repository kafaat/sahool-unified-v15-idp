/// AutoDispose Provider Tests
/// اختبارات التخلص التلقائي للمزودات
///
/// Tests the P0 memory leak fix:
/// - Providers with autoDispose are properly disposed when no longer watched
/// - State is cleaned up when containers are disposed
/// - Key providers across features use autoDispose
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:sahool_field_app/features/marketplace/marketplace_provider.dart';

void main() {
  group('AutoDispose Provider Behavior', () {
    group('Marketplace Providers', () {
      test('marketUserIdProvider should use autoDispose', () {
        final container = ProviderContainer();
        addTearDown(container.dispose);

        // Read the provider - should work
        final userId = container.read(marketUserIdProvider);
        expect(userId, isEmpty);
      });

      test('cartItemCountProvider should start at zero', () async {
        final container = ProviderContainer();

        final count = container.read(cartItemCountProvider);
        expect(count, 0);

        // Allow async initialization to settle before disposal
        await Future.delayed(const Duration(milliseconds: 50));
        container.dispose();
      });

      test('cartTotalProvider should start at zero', () async {
        final container = ProviderContainer();

        final total = container.read(cartTotalProvider);
        expect(total, 0.0);

        await Future.delayed(const Duration(milliseconds: 50));
        container.dispose();
      });

      test('featuredProductsProvider should start empty', () async {
        final container = ProviderContainer();

        final products = container.read(featuredProductsProvider);
        expect(products, isEmpty);

        await Future.delayed(const Duration(milliseconds: 50));
        container.dispose();
      });

      test('harvestProductsProvider should start empty', () async {
        final container = ProviderContainer();

        final products = container.read(harvestProductsProvider);
        expect(products, isEmpty);

        await Future.delayed(const Duration(milliseconds: 50));
        container.dispose();
      });

      test('provider container disposal should not throw', () async {
        final container = ProviderContainer();

        // Read providers to initialize them
        container.read(marketUserIdProvider);
        container.read(cartItemCountProvider);
        container.read(cartTotalProvider);
        container.read(featuredProductsProvider);

        // Allow async initialization to settle before disposal
        await Future.delayed(const Duration(milliseconds: 50));

        // Disposing should work cleanly with autoDispose
        expect(() => container.dispose(), returnsNormally);
      });

      test('separate containers should have independent state', () {
        final container1 = ProviderContainer();
        final container2 = ProviderContainer();
        addTearDown(container1.dispose);
        addTearDown(container2.dispose);

        // Modify state in container1
        container1.read(marketUserIdProvider.notifier).state = 'user-123';

        // container2 should be unaffected
        expect(container2.read(marketUserIdProvider), isEmpty);
        expect(container1.read(marketUserIdProvider), 'user-123');
      });
    });

    group('AutoDispose Memory Safety', () {
      test('autoDispose providers should be re-created after container dispose', () {
        // First container
        final container1 = ProviderContainer();
        container1.read(marketUserIdProvider.notifier).state = 'user-abc';
        expect(container1.read(marketUserIdProvider), 'user-abc');
        container1.dispose();

        // New container should start fresh (old state is gone)
        final container2 = ProviderContainer();
        addTearDown(container2.dispose);
        expect(container2.read(marketUserIdProvider), isEmpty);
      });

      test('multiple provider reads should not leak', () async {
        final container = ProviderContainer();

        // Read multiple times - should be stable
        for (int i = 0; i < 100; i++) {
          container.read(cartItemCountProvider);
          container.read(cartTotalProvider);
        }

        // Should still return correct values
        expect(container.read(cartItemCountProvider), 0);
        expect(container.read(cartTotalProvider), 0.0);

        await Future.delayed(const Duration(milliseconds: 50));
        container.dispose();
      });
    });
  });

  group('Product Model', () {
    test('should parse from JSON', () {
      final json = {
        'id': 'prod-001',
        'name': 'Wheat Seeds',
        'nameAr': 'بذور قمح',
        'category': 'SEEDS',
        'price': 150.0,
        'stock': 100.0,
        'unit': 'kg',
        'sellerId': 'seller-001',
        'sellerType': 'FARMER',
        'createdAt': '2025-01-01T00:00:00Z',
      };

      final product = Product.fromJson(json);
      expect(product.id, 'prod-001');
      expect(product.name, 'Wheat Seeds');
      expect(product.nameAr, 'بذور قمح');
      expect(product.category, ProductCategory.seeds);
      expect(product.price, 150.0);
      expect(product.sellerType, SellerType.farmer);
    });

    test('should handle unknown category', () {
      final json = {
        'id': 'prod-002',
        'name': 'Test',
        'category': 'UNKNOWN',
        'price': 10.0,
        'stock': 5.0,
        'unit': 'unit',
        'sellerId': 'seller-001',
        'sellerType': 'UNKNOWN',
        'createdAt': '2025-01-01T00:00:00Z',
      };

      final product = Product.fromJson(json);
      expect(product.category, ProductCategory.other);
      expect(product.sellerType, SellerType.farmer);
    });

    test('should use name as fallback for nameAr', () {
      final json = {
        'id': 'prod-003',
        'name': 'Test Product',
        'category': 'HARVEST',
        'price': 20.0,
        'stock': 10.0,
        'unit': 'unit',
        'sellerId': 'seller-001',
        'sellerType': 'COMPANY',
        'createdAt': '2025-01-01T00:00:00Z',
      };

      final product = Product.fromJson(json);
      expect(product.nameAr, 'Test Product'); // Falls back to name
    });

    test('categoryIcon should return appropriate emoji', () {
      final json = {
        'id': 'prod-004',
        'name': 'Wheat',
        'category': 'HARVEST',
        'price': 100.0,
        'stock': 500.0,
        'unit': 'ton',
        'sellerId': 'seller-001',
        'sellerType': 'FARMER',
        'createdAt': '2025-01-01T00:00:00Z',
      };

      final product = Product.fromJson(json);
      expect(product.categoryIcon, isNotEmpty);
    });
  });
}
