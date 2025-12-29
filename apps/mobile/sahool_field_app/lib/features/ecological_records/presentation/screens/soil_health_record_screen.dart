import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/theme/sahool_theme.dart';
import '../../../../core/theme/organic_widgets.dart';
import '../providers/ecological_providers.dart';
import '../../domain/entities/ecological_entities.dart';

/// شاشة تسجيل صحة التربة - Soil Health Record Screen
/// نموذج شامل لتسجيل بيانات صحة التربة مع مؤشر الصحة البصري
class SoilHealthRecordScreen extends ConsumerStatefulWidget {
  final String? recordId; // null = سجل جديد
  final String? fieldId; // معرف الحقل

  const SoilHealthRecordScreen({
    super.key,
    this.recordId,
    this.fieldId,
  });

  @override
  ConsumerState<SoilHealthRecordScreen> createState() => _SoilHealthRecordScreenState();
}

class _SoilHealthRecordScreenState extends ConsumerState<SoilHealthRecordScreen> {
  final _formKey = GlobalKey<FormState>();

  // Form Controllers
  final _sampleDepthController = TextEditingController();
  final _organicMatterController = TextEditingController();
  final _phLevelController = TextEditingController();
  final _ecLevelController = TextEditingController();
  final _earthwormCountController = TextEditingController();
  final _notesController = TextEditingController();

  // Form Values
  DateTime? _sampleDate;
  String? _soilTexture;
  double _organicMatterSliderValue = 2.0;

  // Health Score
  double _healthScore = 0.0;

  bool get isEditing => widget.recordId != null;

  @override
  void initState() {
    super.initState();
    _sampleDate = DateTime.now();
    _calculateHealthScore();

    // Add listeners to recalculate health score
    _organicMatterController.addListener(_calculateHealthScore);
    _phLevelController.addListener(_calculateHealthScore);
    _ecLevelController.addListener(_calculateHealthScore);
    _earthwormCountController.addListener(_calculateHealthScore);
  }

  @override
  void dispose() {
    _sampleDepthController.dispose();
    _organicMatterController.dispose();
    _phLevelController.dispose();
    _ecLevelController.dispose();
    _earthwormCountController.dispose();
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
          title: Text(isEditing ? "تعديل سجل التربة" : "سجل صحة تربة جديد"),
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
                // مؤشر صحة التربة في الأعلى
                _buildHealthScoreIndicator(),
                const SizedBox(height: 24),

                // القسم 1: معلومات العينة
                _buildSectionHeader("معلومات العينة", Icons.science_outlined),
                const SizedBox(height: 16),
                _buildSampleInfoSection(),
                const SizedBox(height: 32),

                // القسم 2: الخصائص الفيزيائية
                _buildSectionHeader("الخصائص الفيزيائية", Icons.terrain),
                const SizedBox(height: 16),
                _buildPhysicalPropertiesSection(),
                const SizedBox(height: 32),

                // القسم 3: الخصائص الكيميائية
                _buildSectionHeader("الخصائص الكيميائية", Icons.biotech),
                const SizedBox(height: 16),
                _buildChemicalPropertiesSection(),
                const SizedBox(height: 32),

                // القسم 4: المؤشرات البيولوجية
                _buildSectionHeader("المؤشرات البيولوجية", Icons.bug_report),
                const SizedBox(height: 16),
                _buildBiologicalIndicatorsSection(),
                const SizedBox(height: 32),

                // القسم 5: ملاحظات
                _buildSectionHeader("ملاحظات", Icons.notes),
                const SizedBox(height: 16),
                _buildNotesSection(),
                const SizedBox(height: 32),

                // زر الحفظ
                ElevatedButton(
                  onPressed: _saveSoilHealthRecord,
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

  // ═══════════════════════════════════════════════════════════════════════
  // Health Score Indicator
  // ═══════════════════════════════════════════════════════════════════════

  Widget _buildHealthScoreIndicator() {
    final healthColor = _getHealthColor(_healthScore);
    final healthLabel = _getHealthLabel(_healthScore);

    return OrganicCard(
      color: healthColor.withOpacity(0.1),
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    "مؤشر صحة التربة",
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                      color: SahoolColors.forestGreen,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    healthLabel,
                    style: TextStyle(
                      fontSize: 14,
                      color: healthColor,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ],
              ),
              Container(
                width: 80,
                height: 80,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: healthColor.withOpacity(0.2),
                  border: Border.all(
                    color: healthColor,
                    width: 4,
                  ),
                ),
                child: Center(
                  child: Text(
                    _healthScore.toStringAsFixed(0),
                    style: TextStyle(
                      fontSize: 32,
                      fontWeight: FontWeight.bold,
                      color: healthColor,
                    ),
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          ClipRRect(
            borderRadius: BorderRadius.circular(8),
            child: LinearProgressIndicator(
              value: _healthScore / 100,
              minHeight: 12,
              backgroundColor: Colors.grey[300],
              valueColor: AlwaysStoppedAnimation<Color>(healthColor),
            ),
          ),
          const SizedBox(height: 8),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                "0",
                style: TextStyle(fontSize: 12, color: Colors.grey[600]),
              ),
              Text(
                "50",
                style: TextStyle(fontSize: 12, color: Colors.grey[600]),
              ),
              Text(
                "100",
                style: TextStyle(fontSize: 12, color: Colors.grey[600]),
              ),
            ],
          ),
        ],
      ),
    );
  }

  // ═══════════════════════════════════════════════════════════════════════
  // Form Sections
  // ═══════════════════════════════════════════════════════════════════════

  Widget _buildSampleInfoSection() {
    return Column(
      children: [
        // تاريخ العينة
        InkWell(
          onTap: _selectSampleDate,
          child: InputDecorator(
            decoration: const InputDecoration(
              labelText: "تاريخ العينة (Sample Date)",
              prefixIcon: Icon(Icons.calendar_today),
              suffixIcon: Icon(Icons.arrow_drop_down),
            ),
            child: Text(
              _sampleDate != null
                  ? "${_sampleDate!.year}-${_sampleDate!.month.toString().padLeft(2, '0')}-${_sampleDate!.day.toString().padLeft(2, '0')}"
                  : "اختر التاريخ",
              style: TextStyle(
                color: _sampleDate != null ? Colors.black : Colors.grey,
              ),
            ),
          ),
        ),
        const SizedBox(height: 16),

        // عمق العينة
        TextFormField(
          controller: _sampleDepthController,
          keyboardType: TextInputType.number,
          decoration: const InputDecoration(
            labelText: "عمق العينة سم (Sample Depth)",
            hintText: "مثال: 30",
            prefixIcon: Icon(Icons.height),
            suffixText: "سم",
          ),
          validator: (value) {
            if (value == null || value.isEmpty) {
              return 'الرجاء إدخال عمق العينة';
            }
            final depth = double.tryParse(value);
            if (depth == null || depth <= 0) {
              return 'الرجاء إدخال قيمة صحيحة';
            }
            return null;
          },
        ),
      ],
    );
  }

  Widget _buildPhysicalPropertiesSection() {
    return Column(
      children: [
        // قوام التربة
        DropdownButtonFormField<String>(
          value: _soilTexture,
          decoration: const InputDecoration(
            labelText: "قوام التربة (Soil Texture)",
            prefixIcon: Icon(Icons.grain),
          ),
          items: const [
            DropdownMenuItem(value: "sandy", child: Text("رملية (Sandy)")),
            DropdownMenuItem(value: "clay", child: Text("طينية (Clay)")),
            DropdownMenuItem(value: "loam", child: Text("طميية (Loam)")),
            DropdownMenuItem(value: "mixed", child: Text("مختلطة (Mixed)")),
          ],
          onChanged: (v) => setState(() => _soilTexture = v),
          validator: (value) {
            if (value == null) {
              return 'الرجاء اختيار قوام التربة';
            }
            return null;
          },
        ),
      ],
    );
  }

  Widget _buildChemicalPropertiesSection() {
    return Column(
      children: [
        // نسبة المادة العضوية
        TextFormField(
          controller: _organicMatterController,
          keyboardType: TextInputType.number,
          decoration: const InputDecoration(
            labelText: "نسبة المادة العضوية % (Organic Matter)",
            hintText: "مثال: 3.5",
            prefixIcon: Icon(Icons.eco),
            suffixText: "%",
          ),
          onChanged: (value) {
            final val = double.tryParse(value);
            if (val != null && val >= 0 && val <= 10) {
              setState(() => _organicMatterSliderValue = val);
            }
          },
          validator: (value) {
            if (value == null || value.isEmpty) {
              return 'الرجاء إدخال نسبة المادة العضوية';
            }
            final om = double.tryParse(value);
            if (om == null || om < 0 || om > 100) {
              return 'الرجاء إدخال قيمة بين 0 و 100';
            }
            return null;
          },
        ),
        const SizedBox(height: 16),

        // Slider للمادة العضوية
        OrganicCard(
          color: SahoolColors.paleOlive.withOpacity(0.5),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text(
                    "المادة العضوية",
                    style: TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.w600,
                      color: SahoolColors.forestGreen,
                    ),
                  ),
                  Text(
                    "${_organicMatterSliderValue.toStringAsFixed(1)}%",
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                      color: SahoolColors.sageGreen,
                    ),
                  ),
                ],
              ),
              Slider(
                value: _organicMatterSliderValue,
                min: 0,
                max: 10,
                divisions: 100,
                activeColor: SahoolColors.sageGreen,
                inactiveColor: Colors.grey[300],
                onChanged: (value) {
                  setState(() {
                    _organicMatterSliderValue = value;
                    _organicMatterController.text = value.toStringAsFixed(1);
                  });
                },
              ),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    "0%",
                    style: TextStyle(fontSize: 12, color: Colors.grey[600]),
                  ),
                  Text(
                    "5%",
                    style: TextStyle(fontSize: 12, color: Colors.grey[600]),
                  ),
                  Text(
                    "10%",
                    style: TextStyle(fontSize: 12, color: Colors.grey[600]),
                  ),
                ],
              ),
            ],
          ),
        ),
        const SizedBox(height: 16),

        // درجة الحموضة pH
        TextFormField(
          controller: _phLevelController,
          keyboardType: TextInputType.number,
          decoration: const InputDecoration(
            labelText: "درجة الحموضة pH (pH Level)",
            hintText: "مثال: 7.0",
            prefixIcon: Icon(Icons.water_drop),
            helperText: "المدى الطبيعي: 0-14، المثالي: 6.0-7.5",
          ),
          validator: (value) {
            if (value == null || value.isEmpty) {
              return 'الرجاء إدخال درجة الحموضة';
            }
            final ph = double.tryParse(value);
            if (ph == null || ph < 0 || ph > 14) {
              return 'الرجاء إدخال قيمة بين 0 و 14';
            }
            return null;
          },
        ),
        const SizedBox(height: 16),

        // الملوحة EC
        TextFormField(
          controller: _ecLevelController,
          keyboardType: TextInputType.number,
          decoration: const InputDecoration(
            labelText: "الملوحة EC (Electrical Conductivity)",
            hintText: "مثال: 1.2",
            prefixIcon: Icon(Icons.water),
            suffixText: "dS/m",
            helperText: "المثالي: أقل من 2.0",
          ),
          validator: (value) {
            if (value == null || value.isEmpty) {
              return 'الرجاء إدخال مستوى الملوحة';
            }
            final ec = double.tryParse(value);
            if (ec == null || ec < 0) {
              return 'الرجاء إدخال قيمة صحيحة';
            }
            return null;
          },
        ),
      ],
    );
  }

  Widget _buildBiologicalIndicatorsSection() {
    return Column(
      children: [
        // عدد الديدان
        TextFormField(
          controller: _earthwormCountController,
          keyboardType: TextInputType.number,
          decoration: const InputDecoration(
            labelText: "عدد الديدان (Earthworm Count)",
            hintText: "مثال: 15",
            prefixIcon: Icon(Icons.pets),
            helperText: "عدد الديدان في عينة التربة",
          ),
          validator: (value) {
            if (value == null || value.isEmpty) {
              return 'الرجاء إدخال عدد الديدان';
            }
            final count = int.tryParse(value);
            if (count == null || count < 0) {
              return 'الرجاء إدخال عدد صحيح';
            }
            return null;
          },
        ),
      ],
    );
  }

  Widget _buildNotesSection() {
    return TextFormField(
      controller: _notesController,
      maxLines: 4,
      decoration: const InputDecoration(
        labelText: "ملاحظات (Notes)",
        hintText: "أي ملاحظات إضافية حول حالة التربة، الرائحة، اللون، الرطوبة...",
        alignLabelWithHint: true,
        prefixIcon: Padding(
          padding: EdgeInsets.only(bottom: 70),
          child: Icon(Icons.notes),
        ),
      ),
    );
  }

  // ═══════════════════════════════════════════════════════════════════════
  // Helper Methods
  // ═══════════════════════════════════════════════════════════════════════

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

  Future<void> _selectSampleDate() async {
    final date = await showDatePicker(
      context: context,
      initialDate: _sampleDate ?? DateTime.now(),
      firstDate: DateTime(2020),
      lastDate: DateTime.now(),
      builder: (context, child) {
        return Theme(
          data: Theme.of(context).copyWith(
            colorScheme: const ColorScheme.light(
              primary: SahoolColors.forestGreen,
            ),
          ),
          child: Directionality(
            textDirection: TextDirection.rtl,
            child: child!,
          ),
        );
      },
    );

    if (date != null) {
      setState(() => _sampleDate = date);
    }
  }

  void _calculateHealthScore() {
    setState(() {
      double score = 0.0;
      int factors = 0;

      // عامل 1: درجة الحموضة pH (الوزن: 25%)
      final ph = double.tryParse(_phLevelController.text);
      if (ph != null) {
        factors++;
        if (ph >= 6.0 && ph <= 7.5) {
          score += 25; // مثالي
        } else if (ph >= 5.5 && ph <= 8.0) {
          score += 18; // جيد
        } else if (ph >= 5.0 && ph <= 8.5) {
          score += 12; // مقبول
        } else {
          score += 5; // ضعيف
        }
      }

      // عامل 2: المادة العضوية (الوزن: 30%)
      final om = double.tryParse(_organicMatterController.text);
      if (om != null) {
        factors++;
        if (om >= 5.0) {
          score += 30; // ممتاز
        } else if (om >= 3.0) {
          score += 25; // جيد جداً
        } else if (om >= 2.0) {
          score += 18; // جيد
        } else if (om >= 1.0) {
          score += 10; // مقبول
        } else {
          score += 5; // ضعيف
        }
      }

      // عامل 3: الملوحة EC (الوزن: 25%)
      final ec = double.tryParse(_ecLevelController.text);
      if (ec != null) {
        factors++;
        if (ec < 2.0) {
          score += 25; // ممتاز
        } else if (ec < 4.0) {
          score += 18; // جيد
        } else if (ec < 8.0) {
          score += 10; // مقبول
        } else {
          score += 5; // ضعيف
        }
      }

      // عامل 4: عدد الديدان (الوزن: 20%)
      final worms = int.tryParse(_earthwormCountController.text);
      if (worms != null) {
        factors++;
        if (worms >= 20) {
          score += 20; // ممتاز
        } else if (worms >= 10) {
          score += 15; // جيد جداً
        } else if (worms >= 5) {
          score += 10; // جيد
        } else if (worms >= 1) {
          score += 5; // مقبول
        } else {
          score += 0; // ضعيف
        }
      }

      // حساب النتيجة النهائية
      _healthScore = factors > 0 ? score : 0.0;
      _healthScore = _healthScore.clamp(0.0, 100.0);
    });
  }

  Color _getHealthColor(double score) {
    if (score >= 80) return SahoolColors.healthExcellent;
    if (score >= 60) return SahoolColors.healthGood;
    if (score >= 40) return SahoolColors.healthModerate;
    if (score >= 20) return SahoolColors.healthPoor;
    return SahoolColors.healthCritical;
  }

  String _getHealthLabel(double score) {
    if (score >= 80) return "ممتازة (Excellent)";
    if (score >= 60) return "جيدة (Good)";
    if (score >= 40) return "متوسطة (Moderate)";
    if (score >= 20) return "ضعيفة (Poor)";
    return "حرجة (Critical)";
  }

  void _saveSoilHealthRecord() async {
    if (_formKey.currentState!.validate()) {
      // حفظ البيانات
      final SoilTexture texture = _parseSoilTexture(_soilTexture);

      final record = SoilHealthRecord(
        id: widget.recordId ?? DateTime.now().millisecondsSinceEpoch.toString(),
        fieldId: widget.fieldId ?? 'default_field',
        sampleDate: _sampleDate ?? DateTime.now(),
        sampleDepthCm: double.tryParse(_sampleDepthController.text) ?? 0.0,
        soilTexture: texture,
        organicMatterPercent: double.tryParse(_organicMatterController.text) ?? 0.0,
        phLevel: double.tryParse(_phLevelController.text) ?? 7.0,
        ecLevel: double.tryParse(_ecLevelController.text) ?? 0.0,
        earthwormCount: int.tryParse(_earthwormCountController.text) ?? 0,
        notes: _notesController.text.isNotEmpty ? _notesController.text : null,
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
      );

      // حفظ السجل باستخدام المزود
      await ref.read(soilHealthProvider.notifier).addRecord(record);

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('تم حفظ السجل بنجاح'),
            backgroundColor: SahoolColors.forestGreen,
          ),
        );

        Navigator.pop(context);
      }
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text("الرجاء تعبئة جميع الحقول المطلوبة"),
          backgroundColor: SahoolColors.danger,
        ),
      );
    }
  }

  SoilTexture _parseSoilTexture(String? texture) {
    switch (texture) {
      case 'sandy':
        return SoilTexture.sandy;
      case 'clay':
        return SoilTexture.clay;
      case 'loam':
        return SoilTexture.loam;
      case 'mixed':
        return SoilTexture.mixed;
      default:
        return SoilTexture.loam;
    }
  }

  void _showDeleteConfirmation() {
    showDialog(
      context: context,
      builder: (context) => Directionality(
        textDirection: TextDirection.rtl,
        child: AlertDialog(
          title: const Text("حذف السجل"),
          content: const Text(
            "هل أنت متأكد من حذف سجل صحة التربة هذا؟ لا يمكن التراجع عن هذا الإجراء.",
          ),
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
