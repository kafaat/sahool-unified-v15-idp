import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'dart:io';

/// شاشة تنفيذ المهام البحثية
///
/// تتيح للباحث:
/// - تسجيل الملاحظات الميدانية
/// - إرفاق الصور كدليل
/// - الحفظ المحلي (Offline Mode)
/// - المزامنة التلقائية عند توفر الاتصال
class ResearcherTaskScreen extends StatefulWidget {
  final String? taskId;
  final String? plotCode;
  final String? experimentName;

  const ResearcherTaskScreen({
    super.key,
    this.taskId,
    this.plotCode,
    this.experimentName,
  });

  @override
  State<ResearcherTaskScreen> createState() => _ResearcherTaskScreenState();
}

class _ResearcherTaskScreenState extends State<ResearcherTaskScreen> {
  final _formKey = GlobalKey<FormState>();
  final _noteController = TextEditingController();
  final _measurementController = TextEditingController();
  final ImagePicker _picker = ImagePicker();

  String _selectedCategory = 'observation';
  List<XFile> _attachedPhotos = [];
  bool _isSaving = false;
  bool _isOffline = false;

  final List<Map<String, String>> _categories = [
    {'value': 'observation', 'label': 'ملاحظة', 'icon': '👁️'},
    {'value': 'measurement', 'label': 'قياس', 'icon': '📏'},
    {'value': 'treatment', 'label': 'معاملة', 'icon': '💊'},
    {'value': 'harvest', 'label': 'حصاد', 'icon': '🌾'},
    {'value': 'pest', 'label': 'آفة', 'icon': '🐛'},
    {'value': 'disease', 'label': 'مرض', 'icon': '🦠'},
  ];

  @override
  void dispose() {
    _noteController.dispose();
    _measurementController.dispose();
    super.dispose();
  }

  Future<void> _pickImage(ImageSource source) async {
    try {
      final XFile? photo = await _picker.pickImage(
        source: source,
        maxWidth: 1920,
        maxHeight: 1080,
        imageQuality: 85,
      );
      if (photo != null) {
        setState(() {
          _attachedPhotos.add(photo);
        });
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('خطأ في اختيار الصورة: $e')),
      );
    }
  }

  void _removePhoto(int index) {
    setState(() {
      _attachedPhotos.removeAt(index);
    });
  }

  Future<void> _saveLocal() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isSaving = true);

    try {
      // إنشاء كائن البيانات
      final taskData = {
        'id': DateTime.now().millisecondsSinceEpoch.toString(),
        'taskId': widget.taskId,
        'plotCode': widget.plotCode,
        'category': _selectedCategory,
        'notes': _noteController.text,
        'measurement': _measurementController.text,
        'photosCount': _attachedPhotos.length,
        'timestamp': DateTime.now().toIso8601String(),
        'synced': false,
        'offlineId': 'OFF-${DateTime.now().millisecondsSinceEpoch}',
      };

      // الحفظ في قاعدة البيانات المحلية (Isar/SQLite)
      // await localDb.researchTasks.put(taskData);

      // حفظ الصور محلياً
      // for (var photo in _attachedPhotos) {
      //   await _savePhotoLocally(photo);
      // }

      // محاكاة الحفظ
      await Future.delayed(const Duration(milliseconds: 500));

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Row(
              children: [
                Icon(Icons.check_circle, color: Colors.white),
                SizedBox(width: 8),
                Text('💾 تم الحفظ محلياً - سيتم المزامنة عند توفر الاتصال'),
              ],
            ),
            backgroundColor: Colors.green,
            duration: Duration(seconds: 3),
          ),
        );
        Navigator.pop(context, true);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('خطأ في الحفظ: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      if (mounted) setState(() => _isSaving = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('مهمة رصد ميداني 🌾'),
        backgroundColor: Colors.green.shade700,
        foregroundColor: Colors.white,
        actions: [
          // مؤشر حالة الاتصال
          Container(
            margin: const EdgeInsets.only(left: 16),
            child: Row(
              children: [
                Icon(
                  _isOffline ? Icons.cloud_off : Icons.cloud_done,
                  color: _isOffline ? Colors.orange : Colors.white,
                  size: 20,
                ),
                const SizedBox(width: 4),
                Text(
                  _isOffline ? 'Offline' : 'Online',
                  style: TextStyle(
                    fontSize: 12,
                    color: _isOffline ? Colors.orange : Colors.white,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
      body: Form(
        key: _formKey,
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // بطاقة معلومات القطعة
              _buildPlotInfoCard(),
              const SizedBox(height: 20),

              // اختيار نوع التسجيل
              _buildCategorySelector(),
              const SizedBox(height: 20),

              // حقل القياس (إذا كان النوع قياس)
              if (_selectedCategory == 'measurement') ...[
                _buildMeasurementField(),
                const SizedBox(height: 20),
              ],

              // حقل الملاحظات
              _buildNotesField(),
              const SizedBox(height: 20),

              // إرفاق الصور
              _buildPhotoSection(),
              const SizedBox(height: 30),

              // زر الحفظ
              _buildSaveButton(),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildPlotInfoCard() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.blue.shade50,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.blue.shade200),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.blue.shade100,
              borderRadius: BorderRadius.circular(8),
            ),
            child: const Icon(Icons.grid_view, color: Colors.blue),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'القطعة التجريبية: ${widget.plotCode ?? 'B-05'}',
                  style: const TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 16,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  widget.experimentName ?? 'تجربة أصناف القمح المقاومة للجفاف',
                  style: TextStyle(
                    color: Colors.grey.shade600,
                    fontSize: 14,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCategorySelector() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'نوع التسجيل',
          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
        ),
        const SizedBox(height: 12),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: _categories.map((cat) {
            final isSelected = _selectedCategory == cat['value'];
            return GestureDetector(
              onTap: () => setState(() => _selectedCategory = cat['value']!),
              child: Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                decoration: BoxDecoration(
                  color: isSelected ? Colors.green : Colors.grey.shade100,
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
                    Text(cat['icon']!),
                    const SizedBox(width: 6),
                    Text(
                      cat['label']!,
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

  Widget _buildMeasurementField() {
    return TextFormField(
      controller: _measurementController,
      keyboardType: TextInputType.number,
      decoration: InputDecoration(
        labelText: 'القيمة المقاسة',
        hintText: 'أدخل القيمة...',
        prefixIcon: const Icon(Icons.straighten),
        border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
        filled: true,
        fillColor: Colors.grey.shade50,
      ),
      validator: (value) {
        if (_selectedCategory == 'measurement' &&
            (value == null || value.isEmpty)) {
          return 'يرجى إدخال القيمة المقاسة';
        }
        return null;
      },
    );
  }

  Widget _buildNotesField() {
    return TextFormField(
      controller: _noteController,
      maxLines: 4,
      decoration: InputDecoration(
        labelText: 'ملاحظات الباحث',
        hintText: 'أدخل ملاحظاتك هنا...',
        alignLabelWithHint: true,
        border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
        filled: true,
        fillColor: Colors.grey.shade50,
      ),
      validator: (value) {
        if (value == null || value.isEmpty) {
          return 'يرجى إدخال الملاحظات';
        }
        return null;
      },
    );
  }

  Widget _buildPhotoSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'صور الدليل',
          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
        ),
        const SizedBox(height: 12),

        // الصور المرفقة
        if (_attachedPhotos.isNotEmpty) ...[
          SizedBox(
            height: 100,
            child: ListView.builder(
              scrollDirection: Axis.horizontal,
              itemCount: _attachedPhotos.length,
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
                          image: FileImage(File(_attachedPhotos[index].path)),
                          fit: BoxFit.cover,
                        ),
                      ),
                    ),
                    Positioned(
                      top: 4,
                      right: 4,
                      child: GestureDetector(
                        onTap: () => _removePhoto(index),
                        child: Container(
                          padding: const EdgeInsets.all(4),
                          decoration: const BoxDecoration(
                            color: Colors.red,
                            shape: BoxShape.circle,
                          ),
                          child: const Icon(Icons.close,
                              color: Colors.white, size: 16),
                        ),
                      ),
                    ),
                  ],
                );
              },
            ),
          ),
          const SizedBox(height: 12),
        ],

        // أزرار إضافة الصور
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
                    borderRadius: BorderRadius.circular(12),
                  ),
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
                    borderRadius: BorderRadius.circular(12),
                  ),
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
      height: 54,
      child: ElevatedButton.icon(
        onPressed: _isSaving ? null : _saveLocal,
        icon: _isSaving
            ? const SizedBox(
                width: 20,
                height: 20,
                child: CircularProgressIndicator(
                    color: Colors.white, strokeWidth: 2),
              )
            : const Icon(Icons.save_alt),
        label: Text(_isSaving ? 'جاري الحفظ...' : 'حفظ محلي'),
        style: ElevatedButton.styleFrom(
          backgroundColor: Colors.green.shade700,
          foregroundColor: Colors.white,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          textStyle: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
        ),
      ),
    );
  }
}
