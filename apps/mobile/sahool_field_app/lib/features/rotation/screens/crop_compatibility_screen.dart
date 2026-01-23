import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/rotation_models.dart';
import '../providers/rotation_provider.dart';

class CropCompatibilityScreen extends ConsumerStatefulWidget {
  const CropCompatibilityScreen({Key? key}) : super(key: key);

  @override
  ConsumerState<CropCompatibilityScreen> createState() =>
      _CropCompatibilityScreenState();
}

class _CropCompatibilityScreenState
    extends ConsumerState<CropCompatibilityScreen> {
  Crop? _selectedCrop1;
  Crop? _selectedCrop2;

  @override
  Widget build(BuildContext context) {
    final matrixAsync = ref.watch(compatibilityMatrixProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Crop Compatibility'),
        actions: [
          IconButton(
            icon: const Icon(Icons.help_outline),
            tooltip: 'Help',
            onPressed: () => _showHelp(context),
          ),
        ],
      ),
      body: Column(
        children: [
          // Info banner
          Container(
            padding: const EdgeInsets.all(16),
            color: Colors.blue.shade50,
            child: Row(
              children: [
                Icon(Icons.info_outline, color: Colors.blue.shade700),
                const SizedBox(width: 12),
                Expanded(
                  child: Text(
                    'Select two crops to check their compatibility in rotation',
                    style: TextStyle(
                      color: Colors.blue.shade900,
                      fontSize: 14,
                    ),
                  ),
                ),
              ],
            ),
          ),

          // Crop selectors
          Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              children: [
                _buildCropSelector(
                  'First Crop (Current/Previous)',
                  _selectedCrop1,
                  (crop) => setState(() => _selectedCrop1 = crop),
                ),
                const SizedBox(height: 16),
                const Icon(Icons.arrow_downward, color: Colors.grey),
                const SizedBox(height: 16),
                _buildCropSelector(
                  'Second Crop (Next)',
                  _selectedCrop2,
                  (crop) => setState(() => _selectedCrop2 = crop),
                ),
              ],
            ),
          ),

          // Compatibility result
          if (_selectedCrop1 != null && _selectedCrop2 != null)
            _buildCompatibilityResult(_selectedCrop1!, _selectedCrop2!),

          const SizedBox(height: 16),

          // Matrix view
          Expanded(
            child: matrixAsync.when(
              data: (matrix) => _buildCompatibilityMatrix(matrix),
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (error, stack) => Center(
                child: Text('Error loading matrix: $error'),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCropSelector(
      String label, Crop? selected, Function(Crop) onSelect) {
    final crops = YemenCrops.crops.where((c) => !c.isPerennial).toList();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: const TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.w600,
          ),
        ),
        const SizedBox(height: 8),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 12),
          decoration: BoxDecoration(
            border: Border.all(color: Colors.grey.shade300),
            borderRadius: BorderRadius.circular(8),
          ),
          child: DropdownButton<Crop>(
            isExpanded: true,
            value: selected,
            hint: const Text('Select a crop'),
            underline: const SizedBox.shrink(),
            items: crops.map((crop) {
              return DropdownMenuItem(
                value: crop,
                child: Row(
                  children: [
                    Icon(Icons.grass, size: 20, color: Colors.green.shade700),
                    const SizedBox(width: 8),
                    Text(crop.nameEn),
                    const SizedBox(width: 8),
                    Text(
                      crop.nameAr,
                      style: TextStyle(color: Colors.grey.shade600),
                    ),
                  ],
                ),
              );
            }).toList(),
            onChanged: (crop) {
              if (crop != null) onSelect(crop);
            },
          ),
        ),
      ],
    );
  }

  Widget _buildCompatibilityResult(Crop crop1, Crop crop2) {
    final compatibilityAsync = ref.watch(
      cropCompatibilityProvider(
        CropCompatibilityParams(crop1: crop1, crop2: crop2),
      ),
    );

    return compatibilityAsync.when(
      data: (compatibility) => Card(
        margin: const EdgeInsets.symmetric(horizontal: 16),
        color: _getCompatibilityBackgroundColor(compatibility.score),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            children: [
              // Score indicator
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(
                    _getCompatibilityIcon(compatibility.score),
                    size: 48,
                    color: _getCompatibilityColor(compatibility.score),
                  ),
                  const SizedBox(width: 16),
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        compatibility.level,
                        style: TextStyle(
                          fontSize: 24,
                          fontWeight: FontWeight.bold,
                          color: _getCompatibilityColor(compatibility.score),
                        ),
                      ),
                      Text(
                        '${(compatibility.score * 100).toStringAsFixed(0)}% Compatible',
                        style: TextStyle(
                          fontSize: 14,
                          color: Colors.grey.shade700,
                        ),
                      ),
                    ],
                  ),
                ],
              ),

              const SizedBox(height: 16),
              const Divider(),
              const SizedBox(height: 8),

              // English reason
              Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Icon(Icons.info_outline, size: 20),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      compatibility.reason,
                      style: const TextStyle(fontSize: 14),
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 8),

              // Arabic reason
              Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Icon(Icons.translate, size: 20),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      compatibility.reasonAr,
                      style: const TextStyle(fontSize: 14),
                      textDirection: TextDirection.rtl,
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 16),

              // Crop families
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.7),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Column(
                  children: [
                    _buildFamilyInfo(crop1),
                    const SizedBox(height: 8),
                    const Icon(Icons.arrow_downward, size: 16),
                    const SizedBox(height: 8),
                    _buildFamilyInfo(crop2),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
      loading: () => const Padding(
        padding: EdgeInsets.all(16),
        child: CircularProgressIndicator(),
      ),
      error: (error, stack) => const SizedBox.shrink(),
    );
  }

  Widget _buildFamilyInfo(Crop crop) {
    final familyInfo = CropFamilyInfo.familyData[crop.family]!;
    return Row(
      children: [
        Icon(Icons.category, size: 16, color: Colors.grey.shade600),
        const SizedBox(width: 8),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                '${crop.nameEn} (${crop.nameAr})',
                style: const TextStyle(fontWeight: FontWeight.w600),
              ),
              Text(
                '${familyInfo.nameEn} (${familyInfo.nameAr})',
                style: TextStyle(fontSize: 12, color: Colors.grey.shade600),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildCompatibilityMatrix(
      Map<String, Map<String, CompatibilityScore>> matrix) {
    final crops = YemenCrops.crops.where((c) => !c.isPerennial).toList();

    return SingleChildScrollView(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Compatibility Matrix',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  'Tap a cell to see detailed compatibility',
                  style: TextStyle(
                    fontSize: 14,
                    color: Colors.grey.shade600,
                  ),
                ),
                const SizedBox(height: 16),
                _buildColorLegend(),
              ],
            ),
          ),

          // Matrix table
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: DataTable(
              headingRowColor: MaterialStateProperty.all(Colors.grey.shade200),
              columnSpacing: 8,
              horizontalMargin: 8,
              dataRowHeight: 48,
              headingRowHeight: 48,
              columns: [
                const DataColumn(
                  label: Text(
                    'Current →\nNext ↓',
                    style: TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                ...crops.map((crop) => DataColumn(
                      label: SizedBox(
                        width: 60,
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Text(
                              crop.nameEn,
                              style: const TextStyle(
                                fontSize: 10,
                                fontWeight: FontWeight.bold,
                              ),
                              textAlign: TextAlign.center,
                              maxLines: 2,
                              overflow: TextOverflow.ellipsis,
                            ),
                          ],
                        ),
                      ),
                    )),
              ],
              rows: crops.map((nextCrop) {
                return DataRow(
                  cells: [
                    DataCell(
                      SizedBox(
                        width: 80,
                        child: Text(
                          nextCrop.nameEn,
                          style: const TextStyle(
                            fontSize: 11,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ),
                    ),
                    ...crops.map((currentCrop) {
                      if (currentCrop.id == nextCrop.id) {
                        return const DataCell(
                          Center(child: Text('-', style: TextStyle(fontSize: 16))),
                        );
                      }

                      final compatibility =
                          matrix[nextCrop.id]?[currentCrop.id];
                      if (compatibility == null) {
                        return const DataCell(SizedBox.shrink());
                      }

                      return DataCell(
                        GestureDetector(
                          onTap: () => _showCompatibilityDetails(
                              context, compatibility),
                          child: Container(
                            width: 60,
                            height: 40,
                            decoration: BoxDecoration(
                              color: _getCompatibilityColor(compatibility.score)
                                  .withOpacity(0.3),
                              borderRadius: BorderRadius.circular(4),
                              border: Border.all(
                                color: _getCompatibilityColor(compatibility.score),
                                width: 1,
                              ),
                            ),
                            child: Center(
                              child: Icon(
                                _getCompatibilityIcon(compatibility.score),
                                color: _getCompatibilityColor(compatibility.score),
                                size: 20,
                              ),
                            ),
                          ),
                        ),
                      );
                    }),
                  ],
                );
              }).toList(),
            ),
          ),

          const SizedBox(height: 32),
        ],
      ),
    );
  }

  Widget _buildColorLegend() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
      children: [
        _buildLegendItem('Excellent', Colors.green, Icons.check_circle),
        _buildLegendItem('Good', Colors.lightGreen, Icons.check),
        _buildLegendItem('Fair', Colors.orange, Icons.warning),
        _buildLegendItem('Avoid', Colors.red, Icons.cancel),
      ],
    );
  }

  Widget _buildLegendItem(String label, Color color, IconData icon) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(icon, color: color, size: 16),
        const SizedBox(width: 4),
        Text(
          label,
          style: TextStyle(
            fontSize: 11,
            color: color,
            fontWeight: FontWeight.w600,
          ),
        ),
      ],
    );
  }

  Color _getCompatibilityColor(double score) {
    if (score >= 0.9) return Colors.green;
    if (score >= 0.7) return Colors.lightGreen;
    if (score >= 0.5) return Colors.orange;
    return Colors.red;
  }

  Color _getCompatibilityBackgroundColor(double score) {
    return _getCompatibilityColor(score).withOpacity(0.1);
  }

  IconData _getCompatibilityIcon(double score) {
    if (score >= 0.9) return Icons.check_circle;
    if (score >= 0.7) return Icons.check;
    if (score >= 0.5) return Icons.warning;
    return Icons.cancel;
  }

  void _showCompatibilityDetails(
      BuildContext context, CompatibilityScore compatibility) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Row(
          children: [
            Icon(
              _getCompatibilityIcon(compatibility.score),
              color: _getCompatibilityColor(compatibility.score),
            ),
            const SizedBox(width: 8),
            Text(compatibility.level),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '${compatibility.crop2.nameEn} → ${compatibility.crop1.nameEn}',
              style: const TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'Score: ${(compatibility.score * 100).toStringAsFixed(0)}%',
              style: TextStyle(
                color: _getCompatibilityColor(compatibility.score),
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: 16),
            const Divider(),
            const SizedBox(height: 8),
            Text(compatibility.reason),
            const SizedBox(height: 12),
            Text(
              compatibility.reasonAr,
              textDirection: TextDirection.rtl,
              style: TextStyle(color: Colors.grey.shade700),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }

  void _showHelp(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Crop Compatibility Guide'),
        content: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              _buildHelpItem(
                'Excellent (90%+)',
                'Perfect rotation sequence. Maximizes soil health and breaks pest cycles.',
                Colors.green,
              ),
              const SizedBox(height: 12),
              _buildHelpItem(
                'Good (70-89%)',
                'Good rotation choice. Different families with complementary nutrient needs.',
                Colors.lightGreen,
              ),
              const SizedBox(height: 12),
              _buildHelpItem(
                'Fair (50-69%)',
                'Acceptable rotation but not optimal. Monitor soil nutrients closely.',
                Colors.orange,
              ),
              const SizedBox(height: 12),
              _buildHelpItem(
                'Avoid (<50%)',
                'Poor rotation choice. Same family increases disease and pest risk.',
                Colors.red,
              ),
              const SizedBox(height: 16),
              const Divider(),
              const SizedBox(height: 12),
              const Text(
                'Best Practices:',
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              const Text('• Rotate between different crop families'),
              const Text('• Include nitrogen-fixing legumes every 2-3 years'),
              const Text('• Avoid planting the same family consecutively'),
              const Text('• Follow heavy feeders with light feeders or legumes'),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Got it'),
          ),
        ],
      ),
    );
  }

  Widget _buildHelpItem(String title, String description, Color color) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Icon(Icons.circle, color: color, size: 12),
        const SizedBox(width: 8),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                title,
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  color: color,
                ),
              ),
              Text(
                description,
                style: TextStyle(
                  fontSize: 13,
                  color: Colors.grey.shade700,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}
