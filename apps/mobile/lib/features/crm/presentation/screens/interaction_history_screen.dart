/// Interaction History Screen
/// شاشة سجل التفاعلات
///
/// Displays full interaction history for a farmer
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../domain/models/interaction.dart';
import '../../state/crm_providers.dart';
import '../widgets/interaction_timeline.dart';

/// Interaction History Screen
/// شاشة عرض سجل التفاعلات الكامل
class InteractionHistoryScreen extends ConsumerStatefulWidget {
  final String farmerId;
  final String farmerName;

  const InteractionHistoryScreen({
    super.key,
    required this.farmerId,
    required this.farmerName,
  });

  @override
  ConsumerState<InteractionHistoryScreen> createState() =>
      _InteractionHistoryScreenState();
}

class _InteractionHistoryScreenState
    extends ConsumerState<InteractionHistoryScreen> {
  InteractionType? _selectedType;
  InteractionOutcome? _selectedOutcome;

  @override
  Widget build(BuildContext context) {
    final filter = InteractionFilter(
      farmerId: widget.farmerId,
      type: _selectedType,
      outcome: _selectedOutcome,
    );
    final interactionsAsync = ref.watch(interactionsListProvider(filter));

    return Scaffold(
      appBar: AppBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('سجل التفاعلات'),
            Text(
              widget.farmerName,
              style: const TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.normal,
              ),
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: Badge(
              isLabelVisible: filter.hasFilters,
              child: const Icon(Icons.filter_list),
            ),
            onPressed: () => _showFilterSheet(context),
          ),
        ],
      ),
      body: Column(
        children: [
          // Filter chips
          if (_selectedType != null || _selectedOutcome != null)
            _buildFilterChips(),

          // Interactions list
          Expanded(
            child: interactionsAsync.when(
              data: (interactions) => _buildInteractionsList(interactions),
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (error, _) => _buildError(error),
            ),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () => _navigateToAddInteraction(context),
        backgroundColor: const Color(0xFF367C2B),
        child: const Icon(Icons.add, color: Colors.white),
      ),
    );
  }

  Widget _buildFilterChips() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: SingleChildScrollView(
        scrollDirection: Axis.horizontal,
        child: Row(
          children: [
            if (_selectedType != null)
              Padding(
                padding: const EdgeInsets.only(left: 8),
                child: Chip(
                  label: Text(_getTypeLabel(_selectedType!)),
                  deleteIcon: const Icon(Icons.close, size: 16),
                  onDeleted: () {
                    setState(() => _selectedType = null);
                  },
                ),
              ),
            if (_selectedOutcome != null)
              Padding(
                padding: const EdgeInsets.only(left: 8),
                child: Chip(
                  label: Text(_getOutcomeLabel(_selectedOutcome!)),
                  deleteIcon: const Icon(Icons.close, size: 16),
                  onDeleted: () {
                    setState(() => _selectedOutcome = null);
                  },
                ),
              ),
            TextButton(
              onPressed: () {
                setState(() {
                  _selectedType = null;
                  _selectedOutcome = null;
                });
              },
              child: const Text('مسح الكل'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildInteractionsList(List<Interaction> interactions) {
    if (interactions.isEmpty) {
      return Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.history, size: 64, color: Colors.grey[400]),
            const SizedBox(height: 16),
            Text(
              'لا توجد تفاعلات',
              style: TextStyle(
                fontSize: 16,
                color: Colors.grey[600],
              ),
            ),
            const SizedBox(height: 8),
            ElevatedButton.icon(
              onPressed: () => _navigateToAddInteraction(context),
              icon: const Icon(Icons.add),
              label: const Text('إضافة تفاعل'),
            ),
          ],
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: () async {
        ref.invalidate(interactionsListProvider);
      },
      child: SingleChildScrollView(
        physics: const AlwaysScrollableScrollPhysics(),
        child: InteractionTimeline(
          interactions: interactions,
          onInteractionTap: (interaction) {
            _showInteractionDetails(context, interaction);
          },
        ),
      ),
    );
  }

  Widget _buildError(Object error) {
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(Icons.error_outline, size: 64, color: Colors.red[300]),
          const SizedBox(height: 16),
          Text(
            error.toString(),
            style: TextStyle(color: Colors.grey[600]),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 16),
          ElevatedButton(
            onPressed: () => ref.invalidate(interactionsListProvider),
            child: const Text('إعادة المحاولة'),
          ),
        ],
      ),
    );
  }

  void _showFilterSheet(BuildContext context) {
    showModalBottomSheet(
      context: context,
      builder: (context) => SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'تصفية حسب النوع',
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 12),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: [
                  _buildFilterChip(
                    'الكل',
                    _selectedType == null,
                    () => setState(() => _selectedType = null),
                  ),
                  ...InteractionType.values.take(6).map((type) {
                    return _buildFilterChip(
                      _getTypeLabel(type),
                      _selectedType == type,
                      () => setState(() => _selectedType = type),
                    );
                  }),
                ],
              ),
              const SizedBox(height: 24),
              const Text(
                'تصفية حسب النتيجة',
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 12),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: [
                  _buildFilterChip(
                    'الكل',
                    _selectedOutcome == null,
                    () => setState(() => _selectedOutcome = null),
                  ),
                  ...InteractionOutcome.values.map((outcome) {
                    return _buildFilterChip(
                      _getOutcomeLabel(outcome),
                      _selectedOutcome == outcome,
                      () => setState(() => _selectedOutcome = outcome),
                    );
                  }),
                ],
              ),
              const SizedBox(height: 16),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildFilterChip(String label, bool isSelected, VoidCallback onTap) {
    return FilterChip(
      label: Text(label),
      selected: isSelected,
      onSelected: (_) {
        Navigator.pop(context);
        onTap();
      },
      selectedColor: const Color(0xFF367C2B).withOpacity(0.2),
    );
  }

  void _showInteractionDetails(BuildContext context, Interaction interaction) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      builder: (context) => DraggableScrollableSheet(
        initialChildSize: 0.6,
        maxChildSize: 0.9,
        minChildSize: 0.4,
        expand: false,
        builder: (context, scrollController) => _InteractionDetailsSheet(
          interaction: interaction,
          scrollController: scrollController,
        ),
      ),
    );
  }

  void _navigateToAddInteraction(BuildContext context) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => AddInteractionScreen(
          farmerId: widget.farmerId,
          farmerName: widget.farmerName,
        ),
      ),
    );
  }

  String _getTypeLabel(InteractionType type) {
    switch (type) {
      case InteractionType.call:
        return 'مكالمة';
      case InteractionType.visit:
        return 'زيارة';
      case InteractionType.whatsapp:
        return 'واتساب';
      case InteractionType.sms:
        return 'رسالة نصية';
      case InteractionType.email:
        return 'بريد إلكتروني';
      case InteractionType.meeting:
        return 'اجتماع';
      case InteractionType.note:
        return 'ملاحظة';
      case InteractionType.task:
        return 'مهمة';
      case InteractionType.demo:
        return 'عرض';
      case InteractionType.training:
        return 'تدريب';
      case InteractionType.complaint:
        return 'شكوى';
      case InteractionType.feedback:
        return 'ملاحظات';
      case InteractionType.sale:
        return 'بيع';
      case InteractionType.followUp:
        return 'متابعة';
    }
  }

  String _getOutcomeLabel(InteractionOutcome outcome) {
    switch (outcome) {
      case InteractionOutcome.successful:
        return 'ناجح';
      case InteractionOutcome.noAnswer:
        return 'لم يرد';
      case InteractionOutcome.busy:
        return 'مشغول';
      case InteractionOutcome.rescheduled:
        return 'أعيد جدولته';
      case InteractionOutcome.notInterested:
        return 'غير مهتم';
      case InteractionOutcome.interested:
        return 'مهتم';
      case InteractionOutcome.converted:
        return 'تم التحويل';
      case InteractionOutcome.pending:
        return 'معلق';
      case InteractionOutcome.cancelled:
        return 'ملغي';
    }
  }
}

/// Interaction Details Sheet
class _InteractionDetailsSheet extends StatelessWidget {
  final Interaction interaction;
  final ScrollController scrollController;

  const _InteractionDetailsSheet({
    required this.interaction,
    required this.scrollController,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        // Handle
        Container(
          margin: const EdgeInsets.symmetric(vertical: 8),
          width: 40,
          height: 4,
          decoration: BoxDecoration(
            color: Colors.grey[300],
            borderRadius: BorderRadius.circular(2),
          ),
        ),

        // Header
        Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.blue.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Icon(
                  _getTypeIcon(interaction.type),
                  color: Colors.blue,
                  size: 24,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      interaction.displaySubject,
                      style: const TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    Text(
                      interaction.typeAr,
                      style: TextStyle(
                        color: Colors.grey[600],
                        fontSize: 12,
                      ),
                    ),
                  ],
                ),
              ),
              IconButton(
                icon: const Icon(Icons.close),
                onPressed: () => Navigator.pop(context),
              ),
            ],
          ),
        ),

        const Divider(height: 1),

        // Content
        Expanded(
          child: ListView(
            controller: scrollController,
            padding: const EdgeInsets.all(16),
            children: [
              // Description
              if (interaction.description != null) ...[
                const Text(
                  'التفاصيل',
                  style: TextStyle(fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 8),
                Text(interaction.displayDescription!),
                const SizedBox(height: 24),
              ],

              // Outcome
              _buildInfoRow('النتيجة', interaction.outcomeAr),

              // Duration
              if (interaction.durationMinutes != null)
                _buildInfoRow('المدة', interaction.durationFormatted!),

              // Follow-up
              if (interaction.hasFollowUp) ...[
                const SizedBox(height: 16),
                const Text(
                  'المتابعة',
                  style: TextStyle(fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 8),
                Text(
                  'التاريخ: ${_formatDate(interaction.followUpAt!)}',
                ),
                if (interaction.followUpNotes != null)
                  Text('ملاحظات: ${interaction.followUpNotes}'),
              ],

              // Location
              if (interaction.locationName != null) ...[
                const SizedBox(height: 16),
                _buildInfoRow('الموقع', interaction.locationName!),
              ],

              // Agent
              if (interaction.agentName != null)
                _buildInfoRow('المسؤول', interaction.agentName!),

              // Attachments
              if (interaction.hasAttachments) ...[
                const SizedBox(height: 24),
                const Text(
                  'المرفقات',
                  style: TextStyle(fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 8),
                if (interaction.photos.isNotEmpty) ...[
                  Text('${interaction.photos.length} صور'),
                ],
                if (interaction.documents.isNotEmpty) ...[
                  Text('${interaction.documents.length} مستندات'),
                ],
                if (interaction.voiceRecordingUrl != null) ...[
                  const Text('تسجيل صوتي'),
                ],
              ],
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildInfoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 80,
            child: Text(
              label,
              style: TextStyle(
                color: Colors.grey[600],
                fontSize: 12,
              ),
            ),
          ),
          Expanded(
            child: Text(value),
          ),
        ],
      ),
    );
  }

  IconData _getTypeIcon(InteractionType type) {
    switch (type) {
      case InteractionType.call:
        return Icons.phone;
      case InteractionType.visit:
        return Icons.location_on;
      case InteractionType.whatsapp:
        return Icons.chat;
      case InteractionType.sms:
        return Icons.sms;
      case InteractionType.email:
        return Icons.email;
      case InteractionType.meeting:
        return Icons.groups;
      case InteractionType.note:
        return Icons.note;
      default:
        return Icons.touch_app;
    }
  }

  String _formatDate(DateTime date) {
    return '${date.day}/${date.month}/${date.year}';
  }
}

/// Placeholder for AddInteractionScreen
class AddInteractionScreen extends StatelessWidget {
  final String farmerId;
  final String farmerName;

  const AddInteractionScreen({
    super.key,
    required this.farmerId,
    required this.farmerName,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('إضافة تفاعل')),
      body: Center(child: Text('Add interaction for: $farmerName')),
    );
  }
}
