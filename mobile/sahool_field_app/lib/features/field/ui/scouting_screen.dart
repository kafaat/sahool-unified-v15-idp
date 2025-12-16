import 'package:flutter/material.dart';
import '../../../core/theme/sahool_theme.dart';
import '../../../core/theme/organic_widgets.dart';

/// شاشة الكشف الميداني - Plant Doctor
/// تركز على التصوير والتشخيص الذكي للآفات والأمراض
class ScoutingScreen extends StatefulWidget {
  final String? fieldId;

  const ScoutingScreen({super.key, this.fieldId});

  @override
  State<ScoutingScreen> createState() => _ScoutingScreenState();
}

class _ScoutingScreenState extends State<ScoutingScreen> {
  String? _imagePath;
  bool _isAnalyzing = false;
  DiagnosisResult? _diagnosis;
  final _notesController = TextEditingController();
  bool _isRecording = false;
  String _recordingTime = "00:00";
  String _selectedSeverity = "medium";

  @override
  void dispose() {
    _notesController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: SahoolColors.warmCream,
      appBar: AppBar(
        title: const Text("كشف ميداني"),
        backgroundColor: Colors.white,
        foregroundColor: SahoolColors.forestGreen,
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.history),
            onPressed: _showHistory,
            tooltip: "السجل",
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 1. منطقة التصوير
            _buildImageCapture(),

            const SizedBox(height: 24),

            // 2. نتيجة التشخيص (إذا تم التحليل)
            if (_diagnosis != null) _buildDiagnosisCard(),

            if (_diagnosis != null) const SizedBox(height: 24),

            // 3. تحديد الشدة يدوياً
            _buildSeveritySelector(),

            const SizedBox(height: 24),

            // 4. الملاحظات النصية
            _buildNotesField(),

            const SizedBox(height: 16),

            // 5. التسجيل الصوتي
            _buildVoiceRecorder(),

            const SizedBox(height: 16),

            // 6. تحديد الموقع
            _buildLocationCard(),

            const SizedBox(height: 32),

            // 7. زر الحفظ
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: _saveReport,
                style: ElevatedButton.styleFrom(
                  backgroundColor: SahoolColors.forestGreen,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                child: const Text(
                  "حفظ التقرير",
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildImageCapture() {
    return OrganicCard(
      padding: EdgeInsets.zero,
      child: _imagePath == null
          ? _buildEmptyImageState()
          : _buildImagePreview(),
    );
  }

  Widget _buildEmptyImageState() {
    return Container(
      height: 220,
      padding: const EdgeInsets.all(24),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: SahoolColors.paleOlive,
              shape: BoxShape.circle,
            ),
            child: const Icon(
              Icons.camera_alt,
              size: 40,
              color: SahoolColors.forestGreen,
            ),
          ),
          const SizedBox(height: 16),
          const Text(
            "التقط صورة للإصابة أو النبات",
            style: TextStyle(
              fontWeight: FontWeight.bold,
              color: SahoolColors.forestGreen,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            "سيتم تحليلها بالذكاء الاصطناعي",
            style: TextStyle(
              fontSize: 12,
              color: Colors.grey[600],
            ),
          ),
          const SizedBox(height: 16),
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              ElevatedButton.icon(
                onPressed: _captureImage,
                icon: const Icon(Icons.camera_alt, size: 18),
                label: const Text("التقاط"),
                style: ElevatedButton.styleFrom(
                  backgroundColor: SahoolColors.forestGreen,
                  foregroundColor: Colors.white,
                ),
              ),
              const SizedBox(width: 12),
              OutlinedButton.icon(
                onPressed: _pickFromGallery,
                icon: const Icon(Icons.photo_library, size: 18),
                label: const Text("المعرض"),
                style: OutlinedButton.styleFrom(
                  foregroundColor: SahoolColors.forestGreen,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildImagePreview() {
    return Stack(
      children: [
        Container(
          height: 250,
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(28),
            color: Colors.grey[300],
          ),
          child: const Center(
            child: Icon(Icons.image, size: 60, color: Colors.grey),
          ),
        ),
        Positioned(
          top: 12,
          right: 12,
          child: Row(
            children: [
              _ActionChip(
                icon: Icons.refresh,
                onPressed: () => setState(() => _imagePath = null),
              ),
              const SizedBox(width: 8),
              _ActionChip(
                icon: Icons.zoom_in,
                onPressed: () {},
              ),
            ],
          ),
        ),
        if (_isAnalyzing)
          Positioned.fill(
            child: Container(
              decoration: BoxDecoration(
                color: Colors.black54,
                borderRadius: BorderRadius.circular(28),
              ),
              child: const Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  CircularProgressIndicator(color: Colors.white),
                  SizedBox(height: 16),
                  Text(
                    "جاري التحليل...",
                    style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
                  ),
                ],
              ),
            ),
          ),
      ],
    );
  }

  Widget _buildDiagnosisCard() {
    final diagnosis = _diagnosis!;
    final isPositive = diagnosis.confidence > 0.7;

    return OrganicCard(
      color: isPositive ? Colors.red.shade50 : Colors.green.shade50,
      child: Column(
        children: [
          Row(
            children: [
              Icon(
                isPositive ? Icons.warning_amber : Icons.check_circle,
                color: isPositive ? SahoolColors.danger : SahoolColors.sageGreen,
              ),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  isPositive ? "تم اكتشاف إصابة محتملة!" : "النبات يبدو سليماً",
                  style: TextStyle(
                    color: isPositive ? SahoolColors.danger : SahoolColors.sageGreen,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
              StatusBadge(
                label: "دقة ${(diagnosis.confidence * 100).toInt()}%",
                color: isPositive ? SahoolColors.danger : SahoolColors.sageGreen,
              ),
            ],
          ),
          if (isPositive) ...[
            const Divider(height: 24),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text("التشخيص:", style: TextStyle(color: Colors.grey)),
                Text(
                  diagnosis.name,
                  style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text("النوع:", style: TextStyle(color: Colors.grey)),
                Text(diagnosis.type),
              ],
            ),
            const SizedBox(height: 16),
            // التوصيات
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(12),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Row(
                    children: [
                      Icon(Icons.lightbulb, size: 16, color: SahoolColors.harvestGold),
                      SizedBox(width: 4),
                      Text(
                        "التوصية:",
                        style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12),
                      ),
                    ],
                  ),
                  const SizedBox(height: 4),
                  Text(
                    diagnosis.recommendation,
                    style: const TextStyle(fontSize: 12),
                  ),
                ],
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildSeveritySelector() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          "شدة الإصابة",
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 12),
        Row(
          children: [
            _SeverityOption(
              label: "خفيفة",
              icon: Icons.sentiment_satisfied,
              color: SahoolColors.sageGreen,
              isSelected: _selectedSeverity == "low",
              onTap: () => setState(() => _selectedSeverity = "low"),
            ),
            const SizedBox(width: 12),
            _SeverityOption(
              label: "متوسطة",
              icon: Icons.sentiment_neutral,
              color: SahoolColors.harvestGold,
              isSelected: _selectedSeverity == "medium",
              onTap: () => setState(() => _selectedSeverity = "medium"),
            ),
            const SizedBox(width: 12),
            _SeverityOption(
              label: "شديدة",
              icon: Icons.sentiment_dissatisfied,
              color: SahoolColors.danger,
              isSelected: _selectedSeverity == "high",
              onTap: () => setState(() => _selectedSeverity = "high"),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildNotesField() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          "ملاحظات إضافية",
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 12),
        TextFormField(
          controller: _notesController,
          maxLines: 3,
          decoration: const InputDecoration(
            hintText: "صف حالة النبات وانتشار الإصابة...",
            alignLabelWithHint: true,
          ),
        ),
      ],
    );
  }

  Widget _buildVoiceRecorder() {
    return OrganicCard(
      child: Row(
        children: [
          GestureDetector(
            onTap: _toggleRecording,
            child: Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: _isRecording
                    ? SahoolColors.danger.withOpacity(0.1)
                    : SahoolColors.harvestGold.withOpacity(0.2),
                shape: BoxShape.circle,
              ),
              child: Icon(
                _isRecording ? Icons.stop : Icons.mic,
                color: _isRecording ? SahoolColors.danger : SahoolColors.harvestGold,
              ),
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  _isRecording ? "جاري التسجيل..." : "إضافة ملاحظة صوتية",
                  style: const TextStyle(fontWeight: FontWeight.w500),
                ),
                Text(
                  _recordingTime,
                  style: const TextStyle(color: Colors.grey, fontSize: 12),
                ),
              ],
            ),
          ),
          if (_isRecording)
            Container(
              width: 12,
              height: 12,
              decoration: const BoxDecoration(
                color: SahoolColors.danger,
                shape: BoxShape.circle,
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildLocationCard() {
    return OrganicCard(
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: Colors.blue.withOpacity(0.1),
              borderRadius: BorderRadius.circular(8),
            ),
            child: const Icon(Icons.location_on, color: Colors.blue),
          ),
          const SizedBox(width: 12),
          const Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  "الموقع الحالي",
                  style: TextStyle(fontWeight: FontWeight.w500),
                ),
                Text(
                  "15.3694° N, 44.1910° E",
                  style: TextStyle(color: Colors.grey, fontSize: 12),
                ),
              ],
            ),
          ),
          const StatusBadge(
            label: "تم التحديد",
            color: SahoolColors.sageGreen,
            icon: Icons.check,
            isSmall: true,
          ),
        ],
      ),
    );
  }

  void _captureImage() {
    // محاكاة التقاط صورة
    setState(() {
      _imagePath = "captured_image.jpg";
      _isAnalyzing = true;
    });

    // محاكاة تحليل الذكاء الاصطناعي
    Future.delayed(const Duration(seconds: 2), () {
      setState(() {
        _isAnalyzing = false;
        _diagnosis = DiagnosisResult(
          name: "تبقع الأوراق (Leaf Spot)",
          type: "فطري",
          confidence: 0.92,
          recommendation: "رش مبيد فطري مناسب مثل Mancozeb بتركيز 2.5 جم/لتر. يُفضل الرش في الصباح الباكر.",
        );
      });
    });
  }

  void _pickFromGallery() {
    _captureImage(); // نفس السلوك للمحاكاة
  }

  void _toggleRecording() {
    setState(() {
      _isRecording = !_isRecording;
      if (!_isRecording) {
        _recordingTime = "00:15"; // محاكاة مدة التسجيل
      }
    });
  }

  void _showHistory() {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) => DraggableScrollableSheet(
        initialChildSize: 0.6,
        maxChildSize: 0.9,
        minChildSize: 0.4,
        expand: false,
        builder: (context, scrollController) => ListView(
          controller: scrollController,
          padding: const EdgeInsets.all(20),
          children: [
            const Center(
              child: Text(
                "سجل الكشوفات",
                style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18),
              ),
            ),
            const SizedBox(height: 20),
            _HistoryCard(
              date: "اليوم 10:30 ص",
              diagnosis: "تبقع الأوراق",
              severity: "متوسطة",
            ),
            _HistoryCard(
              date: "أمس 3:45 م",
              diagnosis: "نقص النيتروجين",
              severity: "خفيفة",
            ),
            _HistoryCard(
              date: "منذ 3 أيام",
              diagnosis: "سليم",
              severity: "-",
            ),
          ],
        ),
      ),
    );
  }

  void _saveReport() {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text("تم حفظ التقرير بنجاح"),
        backgroundColor: SahoolColors.forestGreen,
      ),
    );
    Navigator.pop(context, true);
  }
}

class DiagnosisResult {
  final String name;
  final String type;
  final double confidence;
  final String recommendation;

  DiagnosisResult({
    required this.name,
    required this.type,
    required this.confidence,
    required this.recommendation,
  });
}

class _ActionChip extends StatelessWidget {
  final IconData icon;
  final VoidCallback onPressed;

  const _ActionChip({required this.icon, required this.onPressed});

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.white,
      borderRadius: BorderRadius.circular(20),
      child: InkWell(
        onTap: onPressed,
        borderRadius: BorderRadius.circular(20),
        child: Padding(
          padding: const EdgeInsets.all(8),
          child: Icon(icon, size: 20, color: SahoolColors.forestGreen),
        ),
      ),
    );
  }
}

class _SeverityOption extends StatelessWidget {
  final String label;
  final IconData icon;
  final Color color;
  final bool isSelected;
  final VoidCallback onTap;

  const _SeverityOption({
    required this.label,
    required this.icon,
    required this.color,
    required this.isSelected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: GestureDetector(
        onTap: onTap,
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 200),
          padding: const EdgeInsets.symmetric(vertical: 16),
          decoration: BoxDecoration(
            color: isSelected ? color.withOpacity(0.1) : Colors.white,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(
              color: isSelected ? color : Colors.grey.withOpacity(0.2),
              width: isSelected ? 2 : 1,
            ),
          ),
          child: Column(
            children: [
              Icon(icon, color: color),
              const SizedBox(height: 4),
              Text(
                label,
                style: TextStyle(
                  fontSize: 12,
                  fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                  color: isSelected ? color : Colors.grey,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _HistoryCard extends StatelessWidget {
  final String date;
  final String diagnosis;
  final String severity;

  const _HistoryCard({
    required this.date,
    required this.diagnosis,
    required this.severity,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.grey.withOpacity(0.1)),
      ),
      child: Row(
        children: [
          Container(
            width: 50,
            height: 50,
            decoration: BoxDecoration(
              color: SahoolColors.paleOlive,
              borderRadius: BorderRadius.circular(8),
            ),
            child: const Icon(Icons.image, color: SahoolColors.sageGreen),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(diagnosis, style: const TextStyle(fontWeight: FontWeight.bold)),
                Text(date, style: const TextStyle(fontSize: 12, color: Colors.grey)),
              ],
            ),
          ),
          StatusBadge(
            label: severity,
            color: severity == "شديدة"
                ? SahoolColors.danger
                : severity == "متوسطة"
                    ? SahoolColors.harvestGold
                    : SahoolColors.sageGreen,
            isSmall: true,
          ),
        ],
      ),
    );
  }
}
