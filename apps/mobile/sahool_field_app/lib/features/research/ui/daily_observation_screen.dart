import 'package:flutter/material.dart';
import 'dart:io';
import 'package:image_picker/image_picker.dart';

/// شاشة الرصد اليومي للباحث
/// Daily Observation Screen - تسجيل الملاحظات والقياسات اليومية
class DailyObservationScreen extends StatefulWidget {
  final String? experimentId;
  final String? plotCode;

  const DailyObservationScreen({
    super.key,
    this.experimentId,
    this.plotCode,
  });

  @override
  State<DailyObservationScreen> createState() => _DailyObservationScreenState();
}

class _DailyObservationScreenState extends State<DailyObservationScreen> {
  final _formKey = GlobalKey<FormState>();
  final _notesController = TextEditingController();
  final ImagePicker _picker = ImagePicker();

  String _selectedPlot = 'B-01';
  String _selectedCategory = 'observation';
  List<XFile> _photos = [];
  List<MeasurementEntry> _measurements = [];
  bool _isSaving = false;
  bool _isOffline = false; // Check connectivity

  final List<String> _plots = ['B-01', 'B-02', 'B-03', 'B-04', 'B-05'];
  final List<Map<String, dynamic>> _categories = [
    {'id': 'observation', 'label': 'ملاحظة عامة', 'icon': '👁️'},
    {'id': 'growth', 'label': 'نمو النبات', 'icon': '🌱'},
    {'id': 'pest', 'label': 'آفات', 'icon': '🐛'},
    {'id': 'disease', 'label': 'أمراض', 'icon': '🦠'},
    {'id': 'irrigation', 'label': 'ري', 'icon': '💧'},
    {'id': 'weather', 'label': 'طقس', 'icon': '☀️'},
  ];

  final List<Map<String, String>> _measurementTypes = [
    {'id': 'plant_height', 'label': 'ارتفاع النبات', 'unit': 'سم'},
    {'id': 'leaf_count', 'label': 'عدد الأوراق', 'unit': 'ورقة'},
    {'id': 'stem_diameter', 'label': 'قطر الساق', 'unit': 'مم'},
    {'id': 'chlorophyll', 'label': 'الكلوروفيل', 'unit': 'SPAD'},
    {'id': 'soil_moisture', 'label': 'رطوبة التربة', 'unit': '%'},
    {'id': 'soil_temp', 'label': 'حرارة التربة', 'unit': '°C'},
  ];

  @override
  void initState() {
    super.initState();
    if (widget.plotCode != null) {
      _selectedPlot = widget.plotCode!;
    }
    // Add initial measurement row
    _measurements.add(MeasurementEntry());
  }

  @override
  void dispose() {
    _notesController.dispose();
    super.dispose();
  }

  Future<void> _pickImage(ImageSource source) async {
    try {
      final photo = await _picker.pickImage(
        source: source,
        maxWidth: 1920,
        maxHeight: 1080,
        imageQuality: 85,
      );
      if (photo != null) {
        setState(() => _photos.add(photo));
      }
    } catch (e) {
      _showError('خطأ في اختيار الصورة');
    }
  }

  void _addMeasurement() {
    setState(() {
      _measurements.add(MeasurementEntry());
    });
  }

  void _removeMeasurement(int index) {
    if (_measurements.length > 1) {
      setState(() {
        _measurements.removeAt(index);
      });
    }
  }

  Future<void> _saveObservation() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isSaving = true);

    try {
      // Prepare data
      final observation = {
        'id': DateTime.now().millisecondsSinceEpoch.toString(),
        'experimentId': widget.experimentId,
        'plotCode': _selectedPlot,
        'category': _selectedCategory,
        'notes': _notesController.text,
        'measurements': _measurements
            .where((m) => m.type != null && m.value != null)
            .map((m) => {
                  'type': m.type,
                  'value': m.value,
                })
            .toList(),
        'photosCount': _photos.length,
        'timestamp': DateTime.now().toIso8601String(),
        'synced': false,
        'offlineId': 'OBS-${DateTime.now().millisecondsSinceEpoch}',
      };

      // Save locally (Isar/SQLite simulation)
      await Future.delayed(const Duration(milliseconds: 500));

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Row(
              children: [
                const Icon(Icons.check_circle, color: Colors.white),
                const SizedBox(width: 8),
                Text(_isOffline
                    ? '💾 تم الحفظ محلياً - سيتم الرفع عند توفر الاتصال'
                    : '✅ تم حفظ الرصد بنجاح'),
              ],
            ),
            backgroundColor: Colors.green,
          ),
        );
        Navigator.pop(context, true);
      }
    } catch (e) {
      _showError('خطأ في الحفظ: $e');
    } finally {
      if (mounted) setState(() => _isSaving = false);
    }
  }

  void _showError(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message), backgroundColor: Colors.red),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('رصد يومي 📝'),
        backgroundColor: Colors.green.shade700,
        foregroundColor: Colors.white,
        actions: [
          // Offline indicator
          Container(
            margin: const EdgeInsets.only(left: 16),
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
            decoration: BoxDecoration(
              color: _isOffline ? Colors.orange : Colors.green.shade800,
              borderRadius: BorderRadius.circular(12),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(
                  _isOffline ? Icons.cloud_off : Icons.cloud_done,
                  size: 16,
                  color: Colors.white,
                ),
                const SizedBox(width: 4),
                Text(
                  _isOffline ? 'Offline' : 'Online',
                  style: const TextStyle(fontSize: 12, color: Colors.white),
                ),
              ],
            ),
          ),
        ],
      ),
      body: Form(
        key: _formKey,
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Date & Time Card
              _buildDateTimeCard(),
              const SizedBox(height: 16),

              // Plot Selection
              _buildPlotSelector(),
              const SizedBox(height: 16),

              // Category Selection
              _buildCategorySelector(),
              const SizedBox(height: 20),

              // Measurements Section
              _buildMeasurementsSection(),
              const SizedBox(height: 20),

              // Notes
              _buildNotesField(),
              const SizedBox(height: 20),

              // Photos
              _buildPhotosSection(),
              const SizedBox(height: 24),

              // Save Button
              _buildSaveButton(),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildDateTimeCard() {
    final now = DateTime.now();
    return Card(
      color: Colors.blue.shade50,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            const Icon(Icons.calendar_today, color: Colors.blue),
            const SizedBox(width: 12),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  '${now.year}/${now.month}/${now.day}',
                  style: const TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Text(
                  '${now.hour.toString().padLeft(2, '0')}:${now.minute.toString().padLeft(2, '0')}',
                  style: TextStyle(color: Colors.grey.shade600),
                ),
              ],
            ),
            const Spacer(),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
              decoration: BoxDecoration(
                color: Colors.blue,
                borderRadius: BorderRadius.circular(20),
              ),
              child: const Text(
                'الآن',
                style:
                    TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPlotSelector() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'القطعة التجريبية',
          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
        ),
        const SizedBox(height: 8),
        SizedBox(
          height: 50,
          child: ListView.builder(
            scrollDirection: Axis.horizontal,
            itemCount: _plots.length,
            itemBuilder: (context, index) {
              final plot = _plots[index];
              final isSelected = plot == _selectedPlot;
              return GestureDetector(
                onTap: () => setState(() => _selectedPlot = plot),
                child: Container(
                  margin: const EdgeInsets.only(left: 8),
                  padding: const EdgeInsets.symmetric(horizontal: 20),
                  decoration: BoxDecoration(
                    color: isSelected ? Colors.green : Colors.grey.shade100,
                    borderRadius: BorderRadius.circular(25),
                    border: Border.all(
                      color: isSelected
                          ? Colors.green.shade700
                          : Colors.grey.shade300,
                    ),
                  ),
                  child: Center(
                    child: Text(
                      plot,
                      style: TextStyle(
                        color: isSelected ? Colors.white : Colors.black87,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                ),
              );
            },
          ),
        ),
      ],
    );
  }

  Widget _buildCategorySelector() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'نوع الرصد',
          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
        ),
        const SizedBox(height: 12),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: _categories.map((cat) {
            final isSelected = cat['id'] == _selectedCategory;
            return GestureDetector(
              onTap: () => setState(() => _selectedCategory = cat['id']),
              child: Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                decoration: BoxDecoration(
                  color: isSelected ? Colors.green : Colors.white,
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(
                    color: isSelected
                        ? Colors.green.shade700
                        : Colors.grey.shade300,
                  ),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(cat['icon']),
                    const SizedBox(width: 6),
                    Text(
                      cat['label'],
                      style: TextStyle(
                        color: isSelected ? Colors.white : Colors.black87,
                        fontWeight:
                            isSelected ? FontWeight.bold : FontWeight.normal,
                      ),
                    ),
                  ],
                ),
              ),
            );
          }).toList(),
        ),
      ],
    );
  }

  Widget _buildMeasurementsSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            const Text(
              'القياسات',
              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
            ),
            TextButton.icon(
              onPressed: _addMeasurement,
              icon: const Icon(Icons.add, size: 18),
              label: const Text('إضافة قياس'),
            ),
          ],
        ),
        const SizedBox(height: 8),
        ...List.generate(_measurements.length, (index) {
          return _buildMeasurementRow(index);
        }),
      ],
    );
  }

  Widget _buildMeasurementRow(int index) {
    final entry = _measurements[index];
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Row(
          children: [
            // Type dropdown
            Expanded(
              flex: 2,
              child: DropdownButtonFormField<String>(
                value: entry.type,
                decoration: const InputDecoration(
                  labelText: 'النوع',
                  contentPadding:
                      EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                  border: OutlineInputBorder(),
                ),
                items: _measurementTypes
                    .map((t) => DropdownMenuItem(
                          value: t['id'],
                          child: Text(t['label']!,
                              style: const TextStyle(fontSize: 13)),
                        ))
                    .toList(),
                onChanged: (value) {
                  setState(() => _measurements[index].type = value);
                },
              ),
            ),
            const SizedBox(width: 8),
            // Value input
            Expanded(
              child: TextFormField(
                keyboardType: TextInputType.number,
                decoration: InputDecoration(
                  labelText: 'القيمة',
                  suffix: Text(
                    _measurementTypes.firstWhere(
                          (t) => t['id'] == entry.type,
                          orElse: () => {'unit': ''},
                        )['unit'] ??
                        '',
                    style: const TextStyle(fontSize: 12),
                  ),
                  contentPadding:
                      const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                  border: const OutlineInputBorder(),
                ),
                onChanged: (value) {
                  _measurements[index].value = double.tryParse(value);
                },
              ),
            ),
            // Remove button
            if (_measurements.length > 1)
              IconButton(
                icon: const Icon(Icons.close, color: Colors.red),
                onPressed: () => _removeMeasurement(index),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildNotesField() {
    return TextFormField(
      controller: _notesController,
      maxLines: 4,
      decoration: InputDecoration(
        labelText: 'الملاحظات',
        hintText: 'أدخل ملاحظاتك هنا...',
        alignLabelWithHint: true,
        border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
        filled: true,
        fillColor: Colors.grey.shade50,
      ),
      validator: (value) {
        if ((value == null || value.isEmpty) &&
            _measurements.every((m) => m.value == null)) {
          return 'يرجى إدخال ملاحظات أو قياس واحد على الأقل';
        }
        return null;
      },
    );
  }

  Widget _buildPhotosSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'الصور',
          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
        ),
        const SizedBox(height: 12),

        // Photo thumbnails
        if (_photos.isNotEmpty)
          SizedBox(
            height: 100,
            child: ListView.builder(
              scrollDirection: Axis.horizontal,
              itemCount: _photos.length,
              itemBuilder: (context, index) {
                return Stack(
                  children: [
                    Container(
                      width: 100,
                      height: 100,
                      margin: const EdgeInsets.only(left: 8),
                      decoration: BoxDecoration(
                        borderRadius: BorderRadius.circular(12),
                        image: DecorationImage(
                          image: FileImage(File(_photos[index].path)),
                          fit: BoxFit.cover,
                        ),
                      ),
                    ),
                    Positioned(
                      top: 4,
                      right: 4,
                      child: GestureDetector(
                        onTap: () => setState(() => _photos.removeAt(index)),
                        child: Container(
                          padding: const EdgeInsets.all(4),
                          decoration: const BoxDecoration(
                            color: Colors.red,
                            shape: BoxShape.circle,
                          ),
                          child: const Icon(Icons.close,
                              color: Colors.white, size: 14),
                        ),
                      ),
                    ),
                  ],
                );
              },
            ),
          ),

        const SizedBox(height: 12),

        // Add photo buttons
        Row(
          children: [
            Expanded(
              child: OutlinedButton.icon(
                onPressed: () => _pickImage(ImageSource.camera),
                icon: const Icon(Icons.camera_alt),
                label: const Text('الكاميرا'),
                style: OutlinedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 14),
                  shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12)),
                ),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: OutlinedButton.icon(
                onPressed: () => _pickImage(ImageSource.gallery),
                icon: const Icon(Icons.photo_library),
                label: const Text('المعرض'),
                style: OutlinedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 14),
                  shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12)),
                ),
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildSaveButton() {
    return SizedBox(
      width: double.infinity,
      height: 56,
      child: ElevatedButton.icon(
        onPressed: _isSaving ? null : _saveObservation,
        icon: _isSaving
            ? const SizedBox(
                width: 20,
                height: 20,
                child: CircularProgressIndicator(
                    color: Colors.white, strokeWidth: 2),
              )
            : Icon(_isOffline ? Icons.save : Icons.cloud_upload),
        label: Text(
          _isSaving
              ? 'جاري الحفظ...'
              : (_isOffline ? 'حفظ محلي 💾' : 'حفظ ورفع ☁️'),
          style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
        ),
        style: ElevatedButton.styleFrom(
          backgroundColor: Colors.green.shade700,
          foregroundColor: Colors.white,
          shape:
              RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        ),
      ),
    );
  }
}

class MeasurementEntry {
  String? type;
  double? value;

  MeasurementEntry({this.type, this.value});
}
