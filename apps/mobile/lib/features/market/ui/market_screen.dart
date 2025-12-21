import 'package:flutter/material.dart';
import '../../../core/theme/sahool_theme.dart';

/// شاشة السوق الزراعي - تصميم احترافي
/// Professional Agricultural Marketplace Screen
class MarketScreen extends StatefulWidget {
  const MarketScreen({super.key});

  @override
  State<MarketScreen> createState() => _MarketScreenState();
}

class _MarketScreenState extends State<MarketScreen> {
  String _selectedCategory = 'all';
  final _searchController = TextEditingController();
  int _cartItemsCount = 3;

  final List<Map<String, dynamic>> _categories = [
    {'id': 'all', 'label': 'الكل', 'icon': Icons.apps},
    {'id': 'seeds', 'label': 'بذور ومحاصيل', 'icon': Icons.grass},
    {'id': 'fertilizers', 'label': 'أسمدة', 'icon': Icons.science},
    {'id': 'equipment', 'label': 'معدات ري', 'icon': Icons.water_drop},
    {'id': 'tools', 'label': 'أدوات زراعية', 'icon': Icons.construction},
  ];

  final List<Map<String, dynamic>> _products = [
    {
      'id': '1',
      'name': 'بذور قمح يمني',
      'seller': 'مؤسسة الحبوب',
      'price': 250,
      'unit': 'كيلو',
      'rating': 4.8,
      'image': null,
      'category': 'seeds',
    },
    {
      'id': '2',
      'name': 'سماد يوريا 46%',
      'seller': 'شركة الأسمدة',
      'price': 180,
      'unit': 'كيس 50كغ',
      'rating': 4.5,
      'image': null,
      'category': 'fertilizers',
    },
    {
      'id': '3',
      'name': 'نظام ري بالتنقيط',
      'seller': 'تقنيات الري',
      'price': 1500,
      'unit': 'مجموعة',
      'rating': 4.9,
      'image': null,
      'category': 'equipment',
    },
    {
      'id': '4',
      'name': 'بذور طماطم هجين',
      'seller': 'البذور الذهبية',
      'price': 85,
      'unit': 'علبة',
      'rating': 4.7,
      'image': null,
      'category': 'seeds',
    },
    {
      'id': '5',
      'name': 'مبيد حشري طبيعي',
      'seller': 'الحماية الزراعية',
      'price': 120,
      'unit': 'لتر',
      'rating': 4.3,
      'image': null,
      'category': 'fertilizers',
    },
    {
      'id': '6',
      'name': 'مضخة مياه شمسية',
      'seller': 'الطاقة الخضراء',
      'price': 3500,
      'unit': 'وحدة',
      'rating': 4.6,
      'image': null,
      'category': 'equipment',
    },
  ];

  List<Map<String, dynamic>> get _filteredProducts {
    if (_selectedCategory == 'all') return _products;
    return _products.where((p) => p['category'] == _selectedCategory).toList();
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[50],
      appBar: AppBar(
        title: const Text("سوق سهول"),
        backgroundColor: SahoolColors.forestGreen,
        foregroundColor: Colors.white,
        elevation: 0,
        actions: [
          // سلة التسوق
          Stack(
            children: [
              IconButton(
                onPressed: () {
                  // الانتقال لسلة التسوق
                },
                icon: const Icon(Icons.shopping_cart_outlined),
              ),
              if (_cartItemsCount > 0)
                Positioned(
                  right: 8,
                  top: 8,
                  child: Container(
                    padding: const EdgeInsets.all(4),
                    decoration: const BoxDecoration(
                      color: SahoolColors.harvestGold,
                      shape: BoxShape.circle,
                    ),
                    child: Text(
                      '$_cartItemsCount',
                      style: const TextStyle(
                        fontSize: 10,
                        fontWeight: FontWeight.bold,
                        color: Colors.white,
                      ),
                    ),
                  ),
                ),
            ],
          ),
        ],
      ),
      body: Column(
        children: [
          // 1. قسم البحث والتصنيفات
          _buildSearchAndCategories(),

          // 2. شبكة المنتجات
          Expanded(
            child: GridView.builder(
              padding: const EdgeInsets.all(16),
              gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: 2,
                childAspectRatio: 0.72,
                crossAxisSpacing: 16,
                mainAxisSpacing: 16,
              ),
              itemCount: _filteredProducts.length,
              itemBuilder: (context, index) {
                return _ProductCard(
                  product: _filteredProducts[index],
                  onAddToCart: () {
                    setState(() => _cartItemsCount++);
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(
                        content: Text(
                          'تمت إضافة ${_filteredProducts[index]['name']} للسلة',
                        ),
                        backgroundColor: SahoolColors.forestGreen,
                        duration: const Duration(seconds: 2),
                      ),
                    );
                  },
                );
              },
            ),
          ),
        ],
      ),
      // زر بيع المحصول
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () {
          // الانتقال لصفحة إضافة منتج
        },
        backgroundColor: SahoolColors.harvestGold,
        foregroundColor: Colors.white,
        icon: const Icon(Icons.add),
        label: const Text(
          "بيع محصولي",
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
      ),
    );
  }

  Widget _buildSearchAndCategories() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.1),
            blurRadius: 10,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        children: [
          // شريط البحث
          TextField(
            controller: _searchController,
            decoration: InputDecoration(
              hintText: "ابحث عن بذور، أسمدة، معدات...",
              prefixIcon: const Icon(Icons.search, color: Colors.grey),
              suffixIcon: IconButton(
                icon: const Icon(Icons.tune, color: Colors.grey),
                onPressed: () {
                  // فتح خيارات التصفية
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

          // التصنيفات
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
                      setState(() => _selectedCategory = cat['id'] as String);
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
  final Map<String, dynamic> product;
  final VoidCallback onAddToCart;

  const _ProductCard({
    required this.product,
    required this.onAddToCart,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.1),
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
            child: Container(
              decoration: BoxDecoration(
                color: Colors.grey[200],
                borderRadius: const BorderRadius.vertical(
                  top: Radius.circular(16),
                ),
              ),
              child: Stack(
                children: [
                  // صورة المنتج (placeholder)
                  Center(
                    child: Icon(
                      Icons.image_outlined,
                      size: 50,
                      color: Colors.grey[400],
                    ),
                  ),
                  // شارة التقييم
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
                          const Icon(
                            Icons.star,
                            size: 14,
                            color: SahoolColors.harvestGold,
                          ),
                          const SizedBox(width: 2),
                          Text(
                            '${product['rating']}',
                            style: const TextStyle(
                              fontSize: 12,
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
                  // اسم المنتج
                  Text(
                    product['name'] as String,
                    style: const TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 14,
                    ),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                  // البائع
                  Text(
                    product['seller'] as String,
                    style: TextStyle(
                      fontSize: 11,
                      color: Colors.grey[600],
                    ),
                    maxLines: 1,
                  ),
                  // السعر وزر الإضافة
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            "\$${product['price']}",
                            style: const TextStyle(
                              fontWeight: FontWeight.bold,
                              fontSize: 16,
                              color: SahoolColors.forestGreen,
                            ),
                          ),
                          Text(
                            "/${product['unit']}",
                            style: TextStyle(
                              fontSize: 10,
                              color: Colors.grey[500],
                            ),
                          ),
                        ],
                      ),
                      // زر الإضافة للسلة
                      InkWell(
                        onTap: onAddToCart,
                        borderRadius: BorderRadius.circular(8),
                        child: Container(
                          padding: const EdgeInsets.all(8),
                          decoration: BoxDecoration(
                            color: SahoolColors.harvestGold,
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: const Icon(
                            Icons.add,
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
