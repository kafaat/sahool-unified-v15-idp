/// Quick Question Chips Widget
/// شرائح الأسئلة السريعة
///
/// Displays quick question templates for common agricultural queries
library;

import 'package:flutter/material.dart';
import '../../../../core/config/theme.dart';
import '../../domain/models/advisory.dart';
import '../../domain/models/advisory_request.dart';

class QuickQuestionChips extends StatelessWidget {
  final List<QuickQuestion> questions;
  final Function(QuickQuestion) onQuestionSelected;
  final bool wrap;

  const QuickQuestionChips({
    super.key,
    required this.questions,
    required this.onQuestionSelected,
    this.wrap = false,
  });

  @override
  Widget build(BuildContext context) {
    if (wrap) {
      return Padding(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        child: Wrap(
          spacing: 8,
          runSpacing: 8,
          children: questions.map((q) => _buildChip(context, q)).toList(),
        ),
      );
    }

    return Container(
      height: 50,
      margin: const EdgeInsets.only(bottom: 8),
      child: ListView.builder(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 16),
        itemCount: questions.length,
        itemBuilder: (context, index) {
          return Padding(
            padding: EdgeInsets.only(
              left: index == 0 ? 0 : 8,
            ),
            child: _buildChip(context, questions[index]),
          );
        },
      ),
    );
  }

  Widget _buildChip(BuildContext context, QuickQuestion question) {
    final locale = Localizations.localeOf(context).languageCode;
    final text = question.getText(locale);

    return ActionChip(
      avatar: Icon(
        _getIconData(question.icon),
        size: 18,
        color: SahoolTheme.primary,
      ),
      label: Text(text),
      labelStyle: TextStyle(
        fontSize: 13,
        color: Colors.grey[800],
      ),
      backgroundColor: SahoolTheme.primary.withValues(alpha: 0.08),
      side: BorderSide(
        color: SahoolTheme.primary.withValues(alpha: 0.2),
      ),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(20),
      ),
      onPressed: () => onQuestionSelected(question),
    );
  }

  IconData _getIconData(String iconName) {
    switch (iconName) {
      case 'water_drop':
        return Icons.water_drop;
      case 'compost':
        return Icons.eco;
      case 'healing':
        return Icons.healing;
      case 'agriculture':
        return Icons.agriculture;
      case 'pest_control':
        return Icons.pest_control;
      case 'cloud':
        return Icons.cloud;
      default:
        return Icons.help_outline;
    }
  }
}

/// Category-based quick questions widget
class CategoryQuickQuestions extends StatefulWidget {
  final Function(QuickQuestion) onQuestionSelected;

  const CategoryQuickQuestions({
    super.key,
    required this.onQuestionSelected,
  });

  @override
  State<CategoryQuickQuestions> createState() => _CategoryQuickQuestionsState();
}

class _CategoryQuickQuestionsState extends State<CategoryQuickQuestions> {
  String _selectedCategory = 'all';

  final Map<String, List<QuickQuestion>> _questionsByCategory = {
    'all': QuickQuestion.predefined,
    'irrigation': [
      const QuickQuestion(
        id: 'irrigation_when',
        textEn: 'When should I irrigate?',
        textAr: 'متى أسقي؟',
        type: AdvisoryRequestType.recommendation,
        focusArea: AdvisoryType.irrigation,
        icon: 'water_drop',
      ),
      const QuickQuestion(
        id: 'irrigation_amount',
        textEn: 'How much water does my crop need?',
        textAr: 'كم كمية الماء التي يحتاجها محصولي؟',
        type: AdvisoryRequestType.recommendation,
        focusArea: AdvisoryType.irrigation,
        icon: 'water_drop',
      ),
      const QuickQuestion(
        id: 'irrigation_frequency',
        textEn: 'How often should I water?',
        textAr: 'كم مرة يجب أن أروي؟',
        type: AdvisoryRequestType.recommendation,
        focusArea: AdvisoryType.irrigation,
        icon: 'water_drop',
      ),
    ],
    'fertilization': [
      const QuickQuestion(
        id: 'fertilizer_what',
        textEn: 'What fertilizer do I need?',
        textAr: 'ما السماد المناسب؟',
        type: AdvisoryRequestType.recommendation,
        focusArea: AdvisoryType.fertilization,
        icon: 'compost',
      ),
      const QuickQuestion(
        id: 'fertilizer_amount',
        textEn: 'How much fertilizer should I use?',
        textAr: 'كم كمية السماد؟',
        type: AdvisoryRequestType.recommendation,
        focusArea: AdvisoryType.fertilization,
        icon: 'compost',
      ),
      const QuickQuestion(
        id: 'fertilizer_timing',
        textEn: 'When is the best time to fertilize?',
        textAr: 'ما أفضل وقت للتسميد؟',
        type: AdvisoryRequestType.recommendation,
        focusArea: AdvisoryType.fertilization,
        icon: 'compost',
      ),
    ],
    'pest_disease': [
      const QuickQuestion(
        id: 'crop_health',
        textEn: 'Is my crop healthy?',
        textAr: 'هل محصولي سليم؟',
        type: AdvisoryRequestType.analysis,
        focusArea: AdvisoryType.diseaseControl,
        icon: 'healing',
      ),
      const QuickQuestion(
        id: 'pest_problem',
        textEn: 'How to control pests?',
        textAr: 'كيف أكافح الآفات؟',
        type: AdvisoryRequestType.recommendation,
        focusArea: AdvisoryType.pestControl,
        icon: 'pest_control',
      ),
      const QuickQuestion(
        id: 'disease_treatment',
        textEn: 'How to treat this disease?',
        textAr: 'كيف أعالج هذا المرض؟',
        type: AdvisoryRequestType.recommendation,
        focusArea: AdvisoryType.diseaseControl,
        icon: 'healing',
      ),
    ],
    'harvest': [
      const QuickQuestion(
        id: 'harvest_time',
        textEn: 'When should I harvest?',
        textAr: 'متى موعد الحصاد؟',
        type: AdvisoryRequestType.recommendation,
        focusArea: AdvisoryType.harvest,
        icon: 'agriculture',
      ),
      const QuickQuestion(
        id: 'harvest_ready',
        textEn: 'Is my crop ready for harvest?',
        textAr: 'هل محصولي جاهز للحصاد؟',
        type: AdvisoryRequestType.analysis,
        focusArea: AdvisoryType.harvest,
        icon: 'agriculture',
      ),
    ],
  };

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Category tabs
        SingleChildScrollView(
          scrollDirection: Axis.horizontal,
          padding: const EdgeInsets.symmetric(horizontal: 16),
          child: Row(
            children: [
              _buildCategoryTab('all', 'الكل'),
              _buildCategoryTab('irrigation', 'الري'),
              _buildCategoryTab('fertilization', 'التسميد'),
              _buildCategoryTab('pest_disease', 'الآفات'),
              _buildCategoryTab('harvest', 'الحصاد'),
            ],
          ),
        ),
        const SizedBox(height: 12),

        // Questions
        QuickQuestionChips(
          questions: _questionsByCategory[_selectedCategory] ?? [],
          onQuestionSelected: widget.onQuestionSelected,
          wrap: true,
        ),
      ],
    );
  }

  Widget _buildCategoryTab(String category, String label) {
    final isSelected = _selectedCategory == category;

    return Padding(
      padding: const EdgeInsets.only(right: 8),
      child: ChoiceChip(
        label: Text(label),
        selected: isSelected,
        onSelected: (selected) {
          if (selected) {
            setState(() {
              _selectedCategory = category;
            });
          }
        },
        selectedColor: SahoolTheme.primary.withValues(alpha: 0.2),
        labelStyle: TextStyle(
          color: isSelected ? SahoolTheme.primary : Colors.grey[700],
          fontWeight: isSelected ? FontWeight.w600 : FontWeight.normal,
        ),
      ),
    );
  }
}

/// Suggested questions based on context
class SuggestedQuestions extends StatelessWidget {
  final String? fieldId;
  final String? cropType;
  final Function(String) onQuestionSelected;

  const SuggestedQuestions({
    super.key,
    this.fieldId,
    this.cropType,
    required this.onQuestionSelected,
  });

  @override
  Widget build(BuildContext context) {
    final suggestions = _getSuggestions();

    if (suggestions.isEmpty) return const SizedBox.shrink();

    return Container(
      margin: const EdgeInsets.all(16),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: SahoolTheme.primary.withValues(alpha: 0.05),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: SahoolTheme.primary.withValues(alpha: 0.1),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Icon(Icons.lightbulb_outline,
                  size: 18, color: SahoolTheme.primary),
              SizedBox(width: 8),
              Text(
                'أسئلة مقترحة',
                style: TextStyle(
                  fontWeight: FontWeight.w600,
                  color: SahoolTheme.primary,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          ...suggestions.map((suggestion) => _buildSuggestionItem(suggestion)),
        ],
      ),
    );
  }

  Widget _buildSuggestionItem(String suggestion) {
    return InkWell(
      onTap: () => onQuestionSelected(suggestion),
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 8),
        child: Row(
          children: [
            Icon(Icons.arrow_forward_ios, size: 14, color: Colors.grey[400]),
            const SizedBox(width: 8),
            Expanded(
              child: Text(
                suggestion,
                style: TextStyle(
                  fontSize: 14,
                  color: Colors.grey[800],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  List<String> _getSuggestions() {
    final suggestions = <String>[];

    // Add context-based suggestions
    if (cropType != null) {
      suggestions.add('ما أفضل وقت لري ${_getCropNameAr(cropType!)}؟');
      suggestions.add('كم السماد المطلوب لـ${_getCropNameAr(cropType!)}؟');
    }

    if (fieldId != null) {
      suggestions.add('حلل صحة الحقل');
      suggestions.add('ما التوصيات الحالية للحقل؟');
    }

    // Add general suggestions
    if (suggestions.isEmpty) {
      suggestions.addAll([
        'ما أفضل طريقة للري في هذا الموسم؟',
        'كيف أحمي محصولي من الآفات؟',
        'متى أفضل وقت للتسميد؟',
      ]);
    }

    return suggestions.take(3).toList();
  }

  String _getCropNameAr(String cropType) {
    final cropNames = {
      'wheat': 'القمح',
      'barley': 'الشعير',
      'date_palm': 'النخيل',
      'tomato': 'الطماطم',
      'cucumber': 'الخيار',
    };
    return cropNames[cropType.toLowerCase()] ?? cropType;
  }
}
