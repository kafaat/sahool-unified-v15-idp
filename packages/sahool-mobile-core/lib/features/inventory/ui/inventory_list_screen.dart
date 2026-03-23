/// Inventory List Screen - شاشة قائمة المخزون
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/inventory_models.dart';
import '../providers/inventory_providers.dart';
import '../widgets/category_filter.dart';
import '../widgets/inventory_card.dart';
import '../widgets/low_stock_alert.dart';

/// شاشة قائمة المخزون
class InventoryListScreen extends ConsumerStatefulWidget {
  const InventoryListScreen({super.key});

  @override
  ConsumerState<InventoryListScreen> createState() => _InventoryListScreenState();
}

class _InventoryListScreenState extends ConsumerState<InventoryListScreen> {
  final _searchController = TextEditingController();
  ItemCategory? _selectedCategory;
  bool _showLowStockOnly = false;
  bool _showExpiringOnly = false;

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  InventoryFilter get _currentFilter {
    return InventoryFilter(
      category: _selectedCategory,
      search: _searchController.text.isEmpty ? null : _searchController.text,
      lowStockOnly: _showLowStockOnly ? true : null,
      expiringOnly: _showExpiringOnly ? true : null,
    );
  }

  @override
  Widget build(BuildContext context) {
    final viewMode = ref.watch(inventoryViewModeProvider);
    final itemsAsync = ref.watch(inventoryItemsProvider(_currentFilter));
    final lowStockItemsAsync = ref.watch(lowStockItemsProvider);
    final statsAsync = ref.watch(inventoryStatsProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('المخزون'),
        actions: [
          // تبديل وضع العرض
          IconButton(
            icon: Icon(viewMode == InventoryViewMode.grid ? Icons.list : Icons.grid_view),
            onPressed: () {
              ref.read(inventoryViewModeProvider.notifier).state =
                  viewMode == InventoryViewMode.grid
                      ? InventoryViewMode.list
                      : InventoryViewMode.grid;
            },
          ),
          // الماسح الضوئي
          IconButton(
            icon: const Icon(Icons.qr_code_scanner),
            onPressed: () {
              // Navigate to scanner screen
              // Navigator.push(context, MaterialPageRoute(builder: (_) => const ScannerScreen()));
            },
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () async {
          ref.invalidate(inventoryItemsProvider);
          ref.invalidate(lowStockItemsProvider);
          ref.invalidate(inventoryStatsProvider);
        },
        child: Column(
          children: [
            // شريط البحث
            Padding(
              padding: const EdgeInsets.all(16),
              child: TextField(
                controller: _searchController,
                decoration: InputDecoration(
                  hintText: 'البحث عن عنصر...',
                  prefixIcon: const Icon(Icons.search),
                  suffixIcon: _searchController.text.isNotEmpty
                      ? IconButton(
                          icon: const Icon(Icons.clear),
                          onPressed: () {
                            _searchController.clear();
                            setState(() {});
                          },
                        )
                      : null,
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                  filled: true,
                  fillColor: Colors.grey.shade50,
                ),
                onChanged: (_) => setState(() {}),
              ),
            ),

            // الإحصائيات
            statsAsync.when(
              data: (stats) => _buildStatsBar(context, stats),
              loading: () => const SizedBox.shrink(),
              error: (_, __) => const SizedBox.shrink(),
            ),

            // تنبيه المخزون المنخفض
            lowStockItemsAsync.when(
              data: (items) => LowStockAlert(
                count: items.length,
                onTap: () {
                  setState(() {
                    _showLowStockOnly = true;
                    _showExpiringOnly = false;
                  });
                },
              ),
              loading: () => const SizedBox.shrink(),
              error: (_, __) => const SizedBox.shrink(),
            ),

            // فلاتر الفئات
            CategoryFilter(
              selectedCategory: _selectedCategory,
              onCategoryChanged: (category) {
                setState(() {
                  _selectedCategory = category;
                });
              },
            ),

            // فلاتر إضافية
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              child: Row(
                children: [
                  FilterChip(
                    label: const Text('مخزون منخفض'),
                    selected: _showLowStockOnly,
                    onSelected: (value) {
                      setState(() {
                        _showLowStockOnly = value;
                        if (value) _showExpiringOnly = false;
                      });
                    },
                  ),
                  const SizedBox(width: 8),
                  FilterChip(
                    label: const Text('قرب الانتهاء'),
                    selected: _showExpiringOnly,
                    onSelected: (value) {
                      setState(() {
                        _showExpiringOnly = value;
                        if (value) _showLowStockOnly = false;
                      });
                    },
                  ),
                ],
              ),
            ),

            // قائمة العناصر
            Expanded(
              child: itemsAsync.when(
                data: (items) {
                  if (items.isEmpty) {
                    return _buildEmptyState(context);
                  }

                  if (viewMode == InventoryViewMode.grid) {
                    return GridView.builder(
                      padding: const EdgeInsets.all(16),
                      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                        crossAxisCount: 2,
                        childAspectRatio: 0.75,
                        crossAxisSpacing: 12,
                        mainAxisSpacing: 12,
                      ),
                      itemCount: items.length,
                      itemBuilder: (context, index) {
                        final item = items[index];
                        return InventoryCard(
                          item: item,
                          isGridView: true,
                          onTap: () => _navigateToDetails(context, item),
                        );
                      },
                    );
                  } else {
                    return ListView.builder(
                      itemCount: items.length,
                      itemBuilder: (context, index) {
                        final item = items[index];
                        return InventoryCard(
                          item: item,
                          isGridView: false,
                          onTap: () => _navigateToDetails(context, item),
                        );
                      },
                    );
                  }
                },
                loading: () => const Center(child: CircularProgressIndicator()),
                error: (error, stack) => Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.error_outline, size: 64, color: Colors.red.shade300),
                      const SizedBox(height: 16),
                      Text(
                        'فشل في تحميل المخزون',
                        style: Theme.of(context).textTheme.titleMedium,
                      ),
                      const SizedBox(height: 8),
                      Text(
                        error.toString(),
                        style: Theme.of(context).textTheme.bodySmall,
                        textAlign: TextAlign.center,
                      ),
                      const SizedBox(height: 16),
                      ElevatedButton.icon(
                        onPressed: () {
                          ref.invalidate(inventoryItemsProvider);
                        },
                        icon: const Icon(Icons.refresh),
                        label: const Text('إعادة المحاولة'),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
      floatingActionButton: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          // إدخال سريع
          FloatingActionButton(
            heroTag: 'quick_stock_in',
            onPressed: () => _showQuickStockInDialog(context),
            tooltip: 'إدخال سريع',
            child: const Icon(Icons.add),
          ),
          const SizedBox(height: 12),
          // إضافة عنصر جديد
          FloatingActionButton(
            heroTag: 'add_item',
            onPressed: () {
              // Navigate to add item screen
              // Navigator.push(context, MaterialPageRoute(builder: (_) => const AddItemScreen()));
            },
            tooltip: 'إضافة عنصر',
            child: const Icon(Icons.inventory_2),
          ),
        ],
      ),
    );
  }

  Widget _buildStatsBar(BuildContext context, InventoryStats stats) {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            Theme.of(context).primaryColor.withOpacity(0.1),
            Theme.of(context).primaryColor.withOpacity(0.05),
          ],
        ),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: Theme.of(context).primaryColor.withOpacity(0.2),
        ),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceAround,
        children: [
          _buildStatItem(
            context,
            'إجمالي',
            stats.totalItems.toString(),
            Icons.inventory_2,
            Colors.blue,
          ),
          _buildStatItem(
            context,
            'منخفض',
            stats.lowStockItems.toString(),
            Icons.warning,
            Colors.orange,
          ),
          _buildStatItem(
            context,
            'نفد',
            stats.outOfStockItems.toString(),
            Icons.error,
            Colors.red,
          ),
        ],
      ),
    );
  }

  Widget _buildStatItem(
    BuildContext context,
    String label,
    String value,
    IconData icon,
    Color color,
  ) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(icon, color: color, size: 24),
        const SizedBox(height: 4),
        Text(
          value,
          style: Theme.of(context).textTheme.titleLarge?.copyWith(
                fontWeight: FontWeight.bold,
                color: color,
              ),
        ),
        Text(
          label,
          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: Colors.grey.shade600,
              ),
        ),
      ],
    );
  }

  Widget _buildEmptyState(BuildContext context) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.inventory_2_outlined,
            size: 96,
            color: Colors.grey.shade300,
          ),
          const SizedBox(height: 16),
          Text(
            'لا توجد عناصر في المخزون',
            style: Theme.of(context).textTheme.titleLarge?.copyWith(
                  color: Colors.grey.shade600,
                ),
          ),
          const SizedBox(height: 8),
          Text(
            'ابدأ بإضافة عناصر إلى المخزون',
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: Colors.grey.shade500,
                ),
          ),
          const SizedBox(height: 24),
          ElevatedButton.icon(
            onPressed: () {
              // Navigate to add item screen
            },
            icon: const Icon(Icons.add),
            label: const Text('إضافة عنصر'),
          ),
        ],
      ),
    );
  }

  void _navigateToDetails(BuildContext context, InventoryItem item) {
    // Navigate to item detail screen
    // Navigator.push(
    //   context,
    //   MaterialPageRoute(builder: (_) => ItemDetailScreen(itemId: item.itemId)),
    // );
  }

  void _showQuickStockInDialog(BuildContext context) {
    // Show quick stock-in dialog
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('إدخال سريع'),
        content: const Text('هذه الميزة قيد التطوير'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('حسناً'),
          ),
        ],
      ),
    );
  }
}
