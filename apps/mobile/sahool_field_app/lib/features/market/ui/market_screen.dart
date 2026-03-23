import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/theme/sahool_theme.dart';
import '../../../core/network/api_result.dart';
import '../data/market_models.dart';
import '../data/market_repository.dart';

/// شاشة السوق الزراعي - مربوطة بـ marketplace-service API
/// Agricultural Marketplace Screen - Connected to marketplace-service
class MarketScreen extends ConsumerStatefulWidget {
  const MarketScreen({super.key});

  @override
  ConsumerState<MarketScreen> createState() => _MarketScreenState();
}

class _MarketScreenState extends ConsumerState<MarketScreen> {
  String? _selectedCategory;
  final _searchController = TextEditingController();

  final List<Map<String, dynamic>> _categories = [
    {'id': null, 'label': 'الكل', 'icon': Icons.apps},
    {'id': 'GRAINS', 'label': 'حبوب', 'icon': Icons.grain},
    {'id': 'VEGETABLES', 'label': 'خضروات', 'icon': Icons.eco},
    {'id': 'FRUITS', 'label': 'فواكه', 'icon': Icons.apple},
    {'id': 'SUPPLIES', 'label': 'مستلزمات', 'icon': Icons.science},
    {'id': 'EQUIPMENT', 'label': 'معدات', 'icon': Icons.construction},
  ];

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final productsAsync = ref.watch(productsFutureProvider(_selectedCategory));

    return Scaffold(
      backgroundColor: Colors.grey[50],
      appBar: AppBar(
        title: const Text('سوق سهول'),
        backgroundColor: SahoolColors.forestGreen,
        foregroundColor: Colors.white,
        elevation: 0,
        actions: [
          IconButton(
            onPressed: () {
              // Navigate to cart
            },
            icon: const Icon(Icons.shopping_cart_outlined),
          ),
        ],
      ),
      body: Column(
        children: [
          _buildSearchAndCategories(),
          Expanded(
            child: productsAsync.when(
              data: (result) => _buildProductsResult(result),
              loading: () => const Center(
                child: CircularProgressIndicator(
                  color: SahoolColors.forestGreen,
                ),
              ),
              error: (error, _) => _buildErrorState(error.toString()),
            ),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () {
          // Navigate to sell harvest
        },
        backgroundColor: SahoolColors.harvestGold,
        foregroundColor: Colors.white,
        icon: const Icon(Icons.add),
        label: const Text(
          'بيع محصولي',
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
      ),
    );
  }

  Widget _buildProductsResult(ApiResult<List<ProductModel>> result) {
    return result.when(
      success: (products) {
        if (products.isEmpty) {
          return _buildEmptyState();
        }
        return RefreshIndicator(
          onRefresh: () async {
            ref.invalidate(productsFutureProvider(_selectedCategory));
          },
          child: GridView.builder(
            padding: const EdgeInsets.all(16),
            gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
              crossAxisCount: 2,
              childAspectRatio: 0.72,
              crossAxisSpacing: 16,
              mainAxisSpacing: 16,
            ),
            itemCount: products.length,
            itemBuilder: (context, index) {
              return _ProductCard(
                product: products[index],
                onAddToCart: () {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text(
                        'تمت إضافة ${products[index].nameAr} للسلة',
                      ),
                      backgroundColor: SahoolColors.forestGreen,
                      duration: const Duration(seconds: 2),
                    ),
                  );
                },
              );
            },
          ),
        );
      },
      failure: (message, statusCode) => _buildErrorState(message),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.storefront_outlined, size: 64, color: Colors.grey[400]),
          const SizedBox(height: 16),
          Text(
            'لا توجد منتجات حالياً',
            style: TextStyle(fontSize: 18, color: Colors.grey[600]),
          ),
          const SizedBox(height: 8),
          Text(
            'جرّب تغيير التصنيف أو البحث',
            style: TextStyle(fontSize: 14, color: Colors.grey[500]),
          ),
        ],
      ),
    );
  }

  Widget _buildErrorState(String message) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.cloud_off, size: 64, color: Colors.grey[400]),
          const SizedBox(height: 16),
          Text(
            message,
            style: TextStyle(fontSize: 16, color: Colors.grey[600]),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 16),
          ElevatedButton.icon(
            onPressed: () {
              ref.invalidate(productsFutureProvider(_selectedCategory));
            },
            icon: const Icon(Icons.refresh),
            label: const Text('إعادة المحاولة'),
            style: ElevatedButton.styleFrom(
              backgroundColor: SahoolColors.forestGreen,
              foregroundColor: Colors.white,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSearchAndCategories() {
    final l10n = AppLocalizations.of(context)!;
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withValues(alpha: 0.1),
            blurRadius: 10,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        children: [
          TextField(
            controller: _searchController,
            decoration: InputDecoration(
              hintText: 'ابحث عن بذور، أسمدة، معدات...',
              prefixIcon: const Icon(Icons.search, color: Colors.grey),
              suffixIcon: IconButton(
                icon: const Icon(Icons.tune, color: Colors.grey),
                onPressed: () {
                  // Open filter options
                },
              ),
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: BorderSide.none,
              ),
              filled: true,
              fillColor: Colors.grey[100],
              contentPadding: const EdgeInsets.symmetric(vertical: 0),
            ),
          ),
          const SizedBox(height: 16),
          SizedBox(
            height: 40,
            child: ListView.builder(
              scrollDirection: Axis.horizontal,
              itemCount: _categories.length,
              itemBuilder: (context, index) {
                final cat = _categories[index];
                final isSelected = _selectedCategory == cat['id'];
                return Padding(
                  padding: const EdgeInsets.only(left: 8),
                  child: FilterChip(
                    label: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(
                          cat['icon'] as IconData,
                          size: 16,
                          color: isSelected ? Colors.white : Colors.grey[700],
                        ),
                        const SizedBox(width: 4),
                        Text(cat['label'] as String),
                      ],
                    ),
                    selected: isSelected,
                    onSelected: (selected) {
                      setState(
                        () => _selectedCategory = cat['id'] as String?,
                      );
                    },
                    selectedColor: SahoolColors.forestGreen,
                    checkmarkColor: Colors.white,
                    labelStyle: TextStyle(
                      color: isSelected ? Colors.white : Colors.grey[700],
                      fontWeight:
                          isSelected ? FontWeight.bold : FontWeight.normal,
                    ),
                    backgroundColor: Colors.grey[100],
                    padding: const EdgeInsets.symmetric(horizontal: 8),
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}

/// بطاقة المنتج
class _ProductCard extends StatelessWidget {
  final ProductModel product;
  final VoidCallback onAddToCart;

  const _ProductCard({
    required this.product,
    required this.onAddToCart,
  });

  @override
  Widget build(BuildContext context) {
    return DecoratedBox(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withValues(alpha: 0.1),
            blurRadius: 10,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // صورة المنتج
          Expanded(
            flex: 3,
            child: DecoratedBox(
              decoration: BoxDecoration(
                color: Colors.grey[200],
                borderRadius: const BorderRadius.vertical(
                  top: Radius.circular(16),
                ),
                image: product.imageUrl != null
                    ? DecorationImage(
                        image: NetworkImage(product.imageUrl!),
                        fit: BoxFit.cover,
                      )
                    : null,
              ),
              child: Stack(
                children: [
                  if (product.imageUrl == null)
                    Center(
                      child: Icon(
                        product.category.icon,
                        size: 50,
                        color: Colors.grey[400],
                      ),
                    ),
                  if (product.organic)
                    Positioned(
                      top: 8,
                      left: 8,
                      child: Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 6,
                          vertical: 2,
                        ),
                        decoration: BoxDecoration(
                          color: Colors.green,
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: const Text(
                          'عضوي',
                          style: TextStyle(
                            fontSize: 10,
                            color: Colors.white,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                    ),
                  Positioned(
                    top: 8,
                    right: 8,
                    child: Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 8,
                        vertical: 4,
                      ),
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(
                            product.category.icon,
                            size: 14,
                            color: SahoolColors.forestGreen,
                          ),
                          const SizedBox(width: 2),
                          Text(
                            product.category.arabicName,
                            style: const TextStyle(
                              fontSize: 10,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),

          // تفاصيل المنتج
          Expanded(
            flex: 2,
            child: Padding(
              padding: const EdgeInsets.all(12),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    product.nameAr,
                    style: const TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 14,
                    ),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                  if (product.sellerName != null)
                    Text(
                      product.sellerName!,
                      style: TextStyle(
                        fontSize: 11,
                        color: Colors.grey[600],
                      ),
                      maxLines: 1,
                    ),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            product.formattedPrice,
                            style: const TextStyle(
                              fontWeight: FontWeight.bold,
                              fontSize: 14,
                              color: SahoolColors.forestGreen,
                            ),
                          ),
                        ],
                      ),
                      InkWell(
                        onTap: product.isAvailable ? onAddToCart : null,
                        borderRadius: BorderRadius.circular(8),
                        child: Container(
                          padding: const EdgeInsets.all(8),
                          decoration: BoxDecoration(
                            color: product.isAvailable
                                ? SahoolColors.harvestGold
                                : Colors.grey[300],
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Icon(
                            product.isAvailable
                                ? Icons.add
                                : Icons.block,
                            size: 18,
                            color: Colors.white,
                          ),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
