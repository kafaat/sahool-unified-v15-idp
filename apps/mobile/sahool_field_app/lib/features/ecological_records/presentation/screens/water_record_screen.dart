import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/theme/sahool_theme.dart';
import '../../../../core/theme/organic_widgets.dart';
import '../providers/ecological_providers.dart';
import '../../domain/entities/ecological_entities.dart';

/// شاشة تسجيل بيانات الحفاظ على المياه
/// Water Conservation Data Recording Screen
class WaterRecordScreen extends ConsumerStatefulWidget {
  final String? recordId; // null = سجل جديد

  const WaterRecordScreen({super.key, this.recordId});

  @override
  ConsumerState<WaterRecordScreen> createState() => _WaterRecordScreenState();
}

class _WaterRecordScreenState extends ConsumerState<WaterRecordScreen> {
  final _formKey = GlobalKey<FormState>();

  // Form Controllers
  final _waterUsedController = TextEditingController();
  final _rainwaterHarvestedController = TextEditingController();
  final _notesController = TextEditingController();

  // Form Fields
  DateTime? _recordDate;
  String? _periodType;
  String? _waterSource;
  String? _irrigationMethod;
  double _efficiencyPercentage = 50.0;
  bool _mulchingApplied = false;
  bool _dripIrrigationUsed = false;

  bool get isEditing => widget.recordId != null;

  @override
  void dispose() {
    _waterUsedController.dispose();
    _rainwaterHarvestedController.dispose();
    _notesController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Directionality(
      textDirection: TextDirection.rtl,
      child: Scaffold(
        backgroundColor: SahoolColors.warmCream,
        appBar: AppBar(
          title: Text(isEditing ? "تعديل سجل المياه" : "تسجيل بيانات المياه"),
          backgroundColor: Colors.white,
          foregroundColor: SahoolColors.forestGreen,
          elevation: 0,
          actions: [
            if (isEditing)
              IconButton(
                icon: const Icon(Icons.delete_outline, color: SahoolColors.danger),
                onPressed: _showDeleteConfirmation,
              ),
          ],
        ),
        body: Form(
          key: _formKey,
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // القسم 1: معلومات الفترة
                _buildSectionHeader("معلومات الفترة", Icons.date_range),
                const SizedBox(height: 16),

                // تاريخ السجل
                InkWell(
                  onTap: _selectRecordDate,
                  child: InputDecorator(
                    decoration: const InputDecoration(
                      labelText: "تاريخ السجل",
                      hintText: "اختر التاريخ",
                      prefixIcon: Icon(Icons.calendar_today),
                      suffixIcon: Icon(Icons.arrow_drop_down),
                    ),
                    child: Text(
                      _recordDate != null
                          ? "${_recordDate!.year}-${_recordDate!.month.toString().padLeft(2, '0')}-${_recordDate!.day.toString().padLeft(2, '0')}"
                          : "اختر التاريخ",
                      style: TextStyle(
                        color: _recordDate != null ? Colors.black : Colors.grey,
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 16),

                // نوع الفترة
                DropdownButtonFormField<String>(
                  value: _periodType,
                  decoration: const InputDecoration(
                    labelText: "نوع الفترة",
                    hintText: "اختر نوع الفترة",
                    prefixIcon: Icon(Icons.timelapse),
                  ),
                  items: const [
                    DropdownMenuItem(value: "daily", child: Text("يومي")),
                    DropdownMenuItem(value: "weekly", child: Text("أسبوعي")),
                    DropdownMenuItem(value: "monthly", child: Text("شهري")),
                    DropdownMenuItem(value: "seasonal", child: Text("موسمي")),
                  ],
                  onChanged: (v) => setState(() => _periodType = v),
                  validator: (value) {
                    if (value == null) {
                      return 'الرجاء اختيار نوع الفترة';
                    }
                    return null;
                  },
                ),

                const SizedBox(height: 32),

                // القسم 2: استخدام المياه
                _buildSectionHeader("استخدام المياه", Icons.water_drop),
                const SizedBox(height: 16),

                // كمية المياه المستخدمة
                TextFormField(
                  controller: _waterUsedController,
                  keyboardType: TextInputType.number,
                  decoration: const InputDecoration(
                    labelText: "كمية المياه المستخدمة",
                    hintText: "مثال: 5000",
                    prefixIcon: Icon(Icons.water),
                    suffixText: "لتر",
                  ),
                  validator: (value) {
                    if (value == null || value.isEmpty) {
                      return 'الرجاء إدخال كمية المياه المستخدمة';
                    }
                    if (double.tryParse(value) == null) {
                      return 'الرجاء إدخال رقم صحيح';
                    }
                    return null;
                  },
                ),
                const SizedBox(height: 16),

                // مصدر المياه
                DropdownButtonFormField<String>(
                  value: _waterSource,
                  decoration: const InputDecoration(
                    labelText: "مصدر المياه",
                    hintText: "اختر مصدر المياه",
                    prefixIcon: Icon(Icons.source),
                  ),
                  items: const [
                    DropdownMenuItem(value: "well", child: Text("بئر")),
                    DropdownMenuItem(value: "river", child: Text("نهر")),
                    DropdownMenuItem(value: "rainwater", child: Text("مياه أمطار")),
                    DropdownMenuItem(value: "network", child: Text("شبكة")),
                  ],
                  onChanged: (v) => setState(() => _waterSource = v),
                  validator: (value) {
                    if (value == null) {
                      return 'الرجاء اختيار مصدر المياه';
                    }
                    return null;
                  },
                ),
                const SizedBox(height: 16),

                // طريقة الري
                DropdownButtonFormField<String>(
                  value: _irrigationMethod,
                  decoration: const InputDecoration(
                    labelText: "طريقة الري",
                    hintText: "اختر طريقة الري",
                    prefixIcon: Icon(Icons.shower),
                  ),
                  items: const [
                    DropdownMenuItem(value: "drip", child: Text("تنقيط")),
                    DropdownMenuItem(value: "sprinkler", child: Text("رشاشات")),
                    DropdownMenuItem(value: "flood", child: Text("غمر")),
                    DropdownMenuItem(value: "pivot", child: Text("محوري")),
                  ],
                  onChanged: (v) => setState(() => _irrigationMethod = v),
                  validator: (value) {
                    if (value == null) {
                      return 'الرجاء اختيار طريقة الري';
                    }
                    return null;
                  },
                ),

                const SizedBox(height: 32),

                // القسم 3: مقاييس الكفاءة
                _buildSectionHeader("مقاييس الكفاءة", Icons.trending_up),
                const SizedBox(height: 16),

                // نسبة الكفاءة
                OrganicCard(
                  color: _getEfficiencyColor().withOpacity(0.1),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          const Text(
                            "نسبة الكفاءة",
                            style: TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                              color: SahoolColors.forestGreen,
                            ),
                          ),
                          Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 16,
                              vertical: 8,
                            ),
                            decoration: BoxDecoration(
                              color: _getEfficiencyColor(),
                              borderRadius: BorderRadius.circular(20),
                            ),
                            child: Row(
                              children: [
                                Icon(
                                  _getEfficiencyIcon(),
                                  color: Colors.white,
                                  size: 20,
                                ),
                                const SizedBox(width: 8),
                                Text(
                                  "${_efficiencyPercentage.round()}%",
                                  style: const TextStyle(
                                    color: Colors.white,
                                    fontWeight: FontWeight.bold,
                                    fontSize: 18,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 16),
                      Slider(
                        value: _efficiencyPercentage,
                        min: 0,
                        max: 100,
                        divisions: 20,
                        activeColor: _getEfficiencyColor(),
                        inactiveColor: _getEfficiencyColor().withOpacity(0.3),
                        onChanged: (value) {
                          setState(() => _efficiencyPercentage = value);
                        },
                      ),
                      const SizedBox(height: 8),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text(
                            _getEfficiencyLabel(),
                            style: TextStyle(
                              color: _getEfficiencyColor(),
                              fontWeight: FontWeight.bold,
                              fontSize: 14,
                            ),
                          ),
                          Text(
                            _getEfficiencyDescription(),
                            style: TextStyle(
                              color: Colors.grey[600],
                              fontSize: 12,
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: 16),

                // مؤشر الكفاءة البصري
                _buildEfficiencyIndicator(),

                const SizedBox(height: 32),

                // القسم 4: ممارسات الحفاظ على المياه
                _buildSectionHeader("ممارسات الحفاظ على المياه", Icons.eco),
                const SizedBox(height: 16),

                // تغطية التربة
                OrganicCard(
                  color: _mulchingApplied
                      ? SahoolColors.sageGreen.withOpacity(0.1)
                      : Colors.grey[100],
                  child: SwitchListTile(
                    title: const Text(
                      "تغطية التربة (Mulching)",
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        color: SahoolColors.forestGreen,
                      ),
                    ),
                    subtitle: const Text(
                      "يساعد على الاحتفاظ بالرطوبة وتقليل التبخر",
                      style: TextStyle(fontSize: 12),
                    ),
                    value: _mulchingApplied,
                    activeColor: SahoolColors.sageGreen,
                    onChanged: (value) {
                      setState(() => _mulchingApplied = value);
                    },
                    contentPadding: EdgeInsets.zero,
                  ),
                ),

                const SizedBox(height: 16),

                // استخدام التنقيط
                OrganicCard(
                  color: _dripIrrigationUsed
                      ? SahoolColors.sageGreen.withOpacity(0.1)
                      : Colors.grey[100],
                  child: SwitchListTile(
                    title: const Text(
                      "استخدام نظام التنقيط",
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        color: SahoolColors.forestGreen,
                      ),
                    ),
                    subtitle: const Text(
                      "أكثر كفاءة في استخدام المياه من الطرق التقليدية",
                      style: TextStyle(fontSize: 12),
                    ),
                    value: _dripIrrigationUsed,
                    activeColor: SahoolColors.sageGreen,
                    onChanged: (value) {
                      setState(() => _dripIrrigationUsed = value);
                    },
                    contentPadding: EdgeInsets.zero,
                  ),
                ),

                const SizedBox(height: 16),

                // مياه أمطار محصودة
                TextFormField(
                  controller: _rainwaterHarvestedController,
                  keyboardType: TextInputType.number,
                  decoration: const InputDecoration(
                    labelText: "مياه أمطار محصودة",
                    hintText: "مثال: 1000",
                    prefixIcon: Icon(Icons.cloud),
                    suffixText: "لتر",
                  ),
                ),

                const SizedBox(height: 16),

                // ملاحظات
                TextFormField(
                  controller: _notesController,
                  maxLines: 4,
                  decoration: const InputDecoration(
                    labelText: "ملاحظات",
                    hintText: "أي معلومات إضافية عن استخدام المياه...",
                    alignLabelWithHint: true,
                    prefixIcon: Padding(
                      padding: EdgeInsets.only(bottom: 70),
                      child: Icon(Icons.notes),
                    ),
                  ),
                ),

                const SizedBox(height: 32),

                // زر الحفظ
                ElevatedButton(
                  onPressed: _saveRecord,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: SahoolColors.forestGreen,
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                  child: Text(
                    isEditing ? "حفظ التغييرات" : "حفظ السجل",
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                    ),
                  ),
                ),

                const SizedBox(height: 16),

                // زر إلغاء
                OutlinedButton(
                  onPressed: () => Navigator.pop(context),
                  style: OutlinedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                  child: const Text("إلغاء"),
                ),

                const SizedBox(height: 24),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildSectionHeader(String title, IconData icon) {
    return Row(
      children: [
        Icon(icon, size: 20, color: SahoolColors.forestGreen),
        const SizedBox(width: 8),
        Text(
          title,
          style: const TextStyle(
            fontWeight: FontWeight.bold,
            fontSize: 18,
            color: SahoolColors.forestGreen,
          ),
        ),
      ],
    );
  }

  Widget _buildEfficiencyIndicator() {
    return OrganicCard(
      color: Colors.white,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const Text(
            "مؤشر الكفاءة البصري",
            style: TextStyle(
              fontWeight: FontWeight.bold,
              fontSize: 14,
              color: SahoolColors.forestGreen,
            ),
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: _buildEfficiencyBar(
                  color: SahoolColors.danger,
                  label: "هدر",
                  range: "0-40%",
                  isActive: _efficiencyPercentage < 40,
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: _buildEfficiencyBar(
                  color: SahoolColors.warning,
                  label: "متوسط",
                  range: "40-70%",
                  isActive: _efficiencyPercentage >= 40 && _efficiencyPercentage < 70,
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: _buildEfficiencyBar(
                  color: SahoolColors.success,
                  label: "كفؤ",
                  range: "70-100%",
                  isActive: _efficiencyPercentage >= 70,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildEfficiencyBar({
    required Color color,
    required String label,
    required String range,
    required bool isActive,
  }) {
    return AnimatedContainer(
      duration: const Duration(milliseconds: 300),
      padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 8),
      decoration: BoxDecoration(
        color: isActive ? color : color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: color,
          width: isActive ? 2 : 1,
        ),
      ),
      child: Column(
        children: [
          Icon(
            isActive ? Icons.check_circle : Icons.circle_outlined,
            color: isActive ? Colors.white : color,
            size: 20,
          ),
          const SizedBox(height: 4),
          Text(
            label,
            style: TextStyle(
              color: isActive ? Colors.white : color,
              fontWeight: FontWeight.bold,
              fontSize: 12,
            ),
          ),
          Text(
            range,
            style: TextStyle(
              color: isActive ? Colors.white70 : color.withOpacity(0.7),
              fontSize: 10,
            ),
          ),
        ],
      ),
    );
  }

  Color _getEfficiencyColor() {
    if (_efficiencyPercentage >= 70) {
      return SahoolColors.success;
    } else if (_efficiencyPercentage >= 40) {
      return SahoolColors.warning;
    } else {
      return SahoolColors.danger;
    }
  }

  IconData _getEfficiencyIcon() {
    if (_efficiencyPercentage >= 70) {
      return Icons.eco;
    } else if (_efficiencyPercentage >= 40) {
      return Icons.warning_amber;
    } else {
      return Icons.warning;
    }
  }

  String _getEfficiencyLabel() {
    if (_efficiencyPercentage >= 70) {
      return "كفاءة عالية";
    } else if (_efficiencyPercentage >= 40) {
      return "كفاءة متوسطة";
    } else {
      return "هدر في المياه";
    }
  }

  String _getEfficiencyDescription() {
    if (_efficiencyPercentage >= 70) {
      return "ممتاز! استمر بهذه الطريقة";
    } else if (_efficiencyPercentage >= 40) {
      return "يمكن التحسين";
    } else {
      return "يحتاج تحسين عاجل";
    }
  }

  Future<void> _selectRecordDate() async {
    final date = await showDatePicker(
      context: context,
      initialDate: _recordDate ?? DateTime.now(),
      firstDate: DateTime(2020),
      lastDate: DateTime.now().add(const Duration(days: 365)),
      builder: (context, child) {
        return Theme(
          data: Theme.of(context).copyWith(
            colorScheme: const ColorScheme.light(
              primary: SahoolColors.forestGreen,
            ),
          ),
          child: child!,
        );
      },
    );

    if (date != null) {
      setState(() => _recordDate = date);
    }
  }

  void _saveRecord() async {
    if (_formKey.currentState!.validate()) {
      if (_recordDate == null) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text("الرجاء اختيار تاريخ السجل"),
            backgroundColor: SahoolColors.danger,
          ),
        );
        return;
      }

      // حفظ البيانات
      final WaterSource source = _parseWaterSource(_waterSource);
      final IrrigationMethod method = _parseIrrigationMethod(_irrigationMethod);

      final record = WaterConservationRecord(
        id: widget.recordId ?? DateTime.now().millisecondsSinceEpoch.toString(),
        farmId: 'default_farm', // TODO: Get from context or parameter
        fieldId: 'default_field', // TODO: Get from context or parameter
        recordDate: _recordDate!,
        waterUsedLiters: double.parse(_waterUsedController.text),
        waterSource: source,
        irrigationMethod: method,
        efficiencyPercentage: _efficiencyPercentage,
        mulchingApplied: _mulchingApplied,
        dripIrrigationUsed: _dripIrrigationUsed,
        rainwaterHarvestedLiters: _rainwaterHarvestedController.text.isNotEmpty
            ? double.parse(_rainwaterHarvestedController.text)
            : null,
        notes: _notesController.text.isNotEmpty ? _notesController.text : null,
      );

      // حفظ السجل باستخدام المزود
      await ref.read(waterConservationProvider.notifier).addRecord(record);

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('تم حفظ السجل بنجاح'),
            backgroundColor: SahoolColors.forestGreen,
          ),
        );
        Navigator.pop(context);
      }
    }
  }

  WaterSource _parseWaterSource(String? source) {
    switch (source) {
      case 'well':
        return WaterSource.well;
      case 'river':
        return WaterSource.river;
      case 'rainwater':
        return WaterSource.rainwater;
      case 'network':
        return WaterSource.network;
      default:
        return WaterSource.well;
    }
  }

  IrrigationMethod _parseIrrigationMethod(String? method) {
    switch (method) {
      case 'drip':
        return IrrigationMethod.drip;
      case 'sprinkler':
        return IrrigationMethod.sprinkler;
      case 'flood':
        return IrrigationMethod.flood;
      case 'pivot':
        return IrrigationMethod.pivot;
      default:
        return IrrigationMethod.drip;
    }
  }

  void _showDeleteConfirmation() {
    showDialog(
      context: context,
      builder: (context) => Directionality(
        textDirection: TextDirection.rtl,
        child: AlertDialog(
          title: const Text("حذف السجل"),
          content: const Text("هل أنت متأكد من حذف هذا السجل؟ لا يمكن التراجع عن هذا الإجراء."),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text("إلغاء"),
            ),
            ElevatedButton(
              onPressed: () {
                Navigator.pop(context); // Close dialog
                Navigator.pop(context, 'deleted'); // Return to previous screen
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: SahoolColors.danger,
              ),
              child: const Text("حذف", style: TextStyle(color: Colors.white)),
            ),
          ],
        ),
      ),
    );
  }
}
