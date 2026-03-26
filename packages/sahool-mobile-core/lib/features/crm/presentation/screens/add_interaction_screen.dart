/// Add Interaction Screen
/// شاشة إضافة تفاعل
///
/// Form to add a new interaction with a farmer
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../domain/models/interaction.dart';
import '../../state/crm_controller.dart';

/// Add Interaction Screen
/// شاشة إضافة تفاعل جديد
class AddInteractionScreen extends ConsumerStatefulWidget {
  final String farmerId;
  final String farmerName;
  final InteractionType? initialType;

  const AddInteractionScreen({
    super.key,
    required this.farmerId,
    required this.farmerName,
    this.initialType,
  });

  @override
  ConsumerState<AddInteractionScreen> createState() =>
      _AddInteractionScreenState();
}

class _AddInteractionScreenState extends ConsumerState<AddInteractionScreen> {
  final _formKey = GlobalKey<FormState>();
  final _subjectController = TextEditingController();
  final _descriptionController = TextEditingController();
  final _followUpNotesController = TextEditingController();

  late InteractionType _selectedType;
  InteractionOutcome _selectedOutcome = InteractionOutcome.successful;
  InteractionDirection _selectedDirection = InteractionDirection.outbound;
  int? _durationMinutes;
  DateTime? _followUpDate;
  bool _isSubmitting = false;

  @override
  void initState() {
    super.initState();
    _selectedType = widget.initialType ?? InteractionType.call;
  }

  @override
  void dispose() {
    _subjectController.dispose();
    _descriptionController.dispose();
    _followUpNotesController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('إضافة تفاعل'),
            Text(
              widget.farmerName,
              style: const TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.normal,
              ),
            ),
          ],
        ),
      ),
      body: Form(
        key: _formKey,
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Interaction type
              _buildSectionTitle('نوع التفاعل'),
              const SizedBox(height: 8),
              _buildTypeSelector(),

              const SizedBox(height: 24),

              // Direction
              _buildSectionTitle('الاتجاه'),
              const SizedBox(height: 8),
              _buildDirectionSelector(),

              const SizedBox(height: 24),

              // Subject
              _buildSectionTitle('الموضوع'),
              const SizedBox(height: 8),
              TextFormField(
                controller: _subjectController,
                decoration: const InputDecoration(
                  hintText: 'موضوع التفاعل...',
                  border: OutlineInputBorder(),
                ),
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'الرجاء إدخال الموضوع';
                  }
                  return null;
                },
              ),

              const SizedBox(height: 24),

              // Description
              _buildSectionTitle('التفاصيل'),
              const SizedBox(height: 8),
              TextFormField(
                controller: _descriptionController,
                maxLines: 4,
                decoration: const InputDecoration(
                  hintText: 'تفاصيل إضافية...',
                  border: OutlineInputBorder(),
                ),
              ),

              const SizedBox(height: 24),

              // Outcome
              _buildSectionTitle('النتيجة'),
              const SizedBox(height: 8),
              _buildOutcomeSelector(),

              const SizedBox(height: 24),

              // Duration (for calls/visits)
              if (_selectedType == InteractionType.call ||
                  _selectedType == InteractionType.visit ||
                  _selectedType == InteractionType.meeting) ...[
                _buildSectionTitle('المدة (دقائق)'),
                const SizedBox(height: 8),
                _buildDurationSelector(),
                const SizedBox(height: 24),
              ],

              // Follow-up
              _buildSectionTitle('جدولة متابعة (اختياري)'),
              const SizedBox(height: 8),
              _buildFollowUpSection(),

              const SizedBox(height: 32),

              // Submit button
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: _isSubmitting ? null : _submitForm,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF367C2B),
                    padding: const EdgeInsets.symmetric(vertical: 16),
                  ),
                  child: _isSubmitting
                      ? const SizedBox(
                          height: 20,
                          width: 20,
                          child: CircularProgressIndicator(
                            strokeWidth: 2,
                            valueColor:
                                AlwaysStoppedAnimation<Color>(Colors.white),
                          ),
                        )
                      : const Text(
                          'حفظ التفاعل',
                          style: TextStyle(color: Colors.white, fontSize: 16),
                        ),
                ),
              ),

              const SizedBox(height: 24),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildSectionTitle(String title) {
    return Text(
      title,
      style: const TextStyle(
        fontSize: 14,
        fontWeight: FontWeight.w600,
      ),
    );
  }

  Widget _buildTypeSelector() {
    final types = [
      (InteractionType.call, Icons.phone, 'مكالمة'),
      (InteractionType.visit, Icons.location_on, 'زيارة'),
      (InteractionType.whatsapp, Icons.chat, 'واتساب'),
      (InteractionType.sms, Icons.sms, 'رسالة'),
      (InteractionType.meeting, Icons.groups, 'اجتماع'),
      (InteractionType.note, Icons.note, 'ملاحظة'),
    ];

    return Wrap(
      spacing: 8,
      runSpacing: 8,
      children: types.map((type) {
        final isSelected = _selectedType == type.$1;
        return ChoiceChip(
          avatar: Icon(
            type.$2,
            size: 18,
            color: isSelected ? Colors.white : Colors.grey[600],
          ),
          label: Text(type.$3),
          selected: isSelected,
          selectedColor: const Color(0xFF367C2B),
          labelStyle: TextStyle(
            color: isSelected ? Colors.white : Colors.grey[700],
          ),
          onSelected: (selected) {
            if (selected) {
              setState(() => _selectedType = type.$1);
            }
          },
        );
      }).toList(),
    );
  }

  Widget _buildDirectionSelector() {
    return SegmentedButton<InteractionDirection>(
      segments: const [
        ButtonSegment(
          value: InteractionDirection.outbound,
          label: Text('صادر (أنا تواصلت)'),
          icon: Icon(Icons.call_made),
        ),
        ButtonSegment(
          value: InteractionDirection.inbound,
          label: Text('وارد (هو تواصل)'),
          icon: Icon(Icons.call_received),
        ),
      ],
      selected: {_selectedDirection},
      onSelectionChanged: (selected) {
        setState(() => _selectedDirection = selected.first);
      },
    );
  }

  Widget _buildOutcomeSelector() {
    final outcomes = [
      (InteractionOutcome.successful, 'ناجح', Colors.green),
      (InteractionOutcome.interested, 'مهتم', Colors.blue),
      (InteractionOutcome.noAnswer, 'لم يرد', Colors.grey),
      (InteractionOutcome.busy, 'مشغول', Colors.orange),
      (InteractionOutcome.rescheduled, 'أعيد جدولته', Colors.purple),
      (InteractionOutcome.notInterested, 'غير مهتم', Colors.red),
    ];

    return Wrap(
      spacing: 8,
      runSpacing: 8,
      children: outcomes.map((outcome) {
        final isSelected = _selectedOutcome == outcome.$1;
        return ChoiceChip(
          label: Text(outcome.$2),
          selected: isSelected,
          selectedColor: outcome.$3.withValues(alpha: 0.2),
          labelStyle: TextStyle(
            color: isSelected ? outcome.$3 : Colors.grey[700],
            fontWeight: isSelected ? FontWeight.w600 : FontWeight.normal,
          ),
          onSelected: (selected) {
            if (selected) {
              setState(() => _selectedOutcome = outcome.$1);
            }
          },
        );
      }).toList(),
    );
  }

  Widget _buildDurationSelector() {
    final durations = [5, 10, 15, 30, 45, 60];

    return Wrap(
      spacing: 8,
      runSpacing: 8,
      children: [
        ...durations.map((minutes) {
          final isSelected = _durationMinutes == minutes;
          return ChoiceChip(
            label: Text('$minutes د'),
            selected: isSelected,
            onSelected: (selected) {
              setState(() => _durationMinutes = selected ? minutes : null);
            },
          );
        }),
        ActionChip(
          avatar: const Icon(Icons.edit, size: 16),
          label: const Text('مخصص'),
          onPressed: () async {
            final result = await showDialog<int>(
              context: context,
              builder: (context) => _DurationInputDialog(
                initialValue: _durationMinutes,
              ),
            );
            if (result != null) {
              setState(() => _durationMinutes = result);
            }
          },
        ),
      ],
    );
  }

  Widget _buildFollowUpSection() {
    return Column(
      children: [
        // Date picker
        InkWell(
          onTap: () async {
            final date = await showDatePicker(
              context: context,
              initialDate: _followUpDate ?? DateTime.now().add(const Duration(days: 7)),
              firstDate: DateTime.now(),
              lastDate: DateTime.now().add(const Duration(days: 365)),
            );
            if (date != null) {
              setState(() => _followUpDate = date);
            }
          },
          child: Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              border: Border.all(color: Colors.grey[300]!),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Row(
              children: [
                Icon(
                  Icons.event,
                  color: _followUpDate != null
                      ? const Color(0xFF367C2B)
                      : Colors.grey[500],
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Text(
                    _followUpDate != null
                        ? '${_followUpDate!.day}/${_followUpDate!.month}/${_followUpDate!.year}'
                        : 'اختر تاريخ المتابعة',
                    style: TextStyle(
                      color: _followUpDate != null
                          ? Colors.black87
                          : Colors.grey[500],
                    ),
                  ),
                ),
                if (_followUpDate != null)
                  IconButton(
                    icon: const Icon(Icons.close, size: 20),
                    onPressed: () => setState(() => _followUpDate = null),
                  ),
              ],
            ),
          ),
        ),

        // Follow-up notes
        if (_followUpDate != null) ...[
          const SizedBox(height: 12),
          TextFormField(
            controller: _followUpNotesController,
            decoration: const InputDecoration(
              hintText: 'ملاحظات المتابعة...',
              border: OutlineInputBorder(),
            ),
          ),
        ],
      ],
    );
  }

  Future<void> _submitForm() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isSubmitting = true);

    try {
      final controller = ref.read(interactionControllerProvider.notifier);

      Interaction? result;

      switch (_selectedType) {
        case InteractionType.call:
          result = await controller.logCall(
            farmerId: widget.farmerId,
            farmerName: widget.farmerName,
            subject: _subjectController.text,
            outcome: _selectedOutcome,
            description: _descriptionController.text.isEmpty
                ? null
                : _descriptionController.text,
            durationMinutes: _durationMinutes,
            followUpAt: _followUpDate,
            followUpNotes: _followUpNotesController.text.isEmpty
                ? null
                : _followUpNotesController.text,
          );
          break;

        case InteractionType.visit:
          result = await controller.logVisit(
            farmerId: widget.farmerId,
            farmerName: widget.farmerName,
            subject: _subjectController.text,
            outcome: _selectedOutcome,
            description: _descriptionController.text.isEmpty
                ? null
                : _descriptionController.text,
            durationMinutes: _durationMinutes,
            followUpAt: _followUpDate,
            followUpNotes: _followUpNotesController.text.isEmpty
                ? null
                : _followUpNotesController.text,
          );
          break;

        case InteractionType.whatsapp:
        case InteractionType.sms:
          result = await controller.logMessage(
            farmerId: widget.farmerId,
            farmerName: widget.farmerName,
            type: _selectedType,
            subject: _subjectController.text,
            outcome: _selectedOutcome,
            description: _descriptionController.text.isEmpty
                ? null
                : _descriptionController.text,
            direction: _selectedDirection,
          );
          break;

        case InteractionType.note:
          result = await controller.addNote(
            farmerId: widget.farmerId,
            farmerName: widget.farmerName,
            subject: _subjectController.text,
            description: _descriptionController.text.isEmpty
                ? null
                : _descriptionController.text,
          );
          break;

        default:
          // Generic interaction
          final now = DateTime.now();
          final interaction = Interaction(
            id: 'local_${now.millisecondsSinceEpoch}',
            tenantId: '',
            farmerId: widget.farmerId,
            farmerName: widget.farmerName,
            type: _selectedType,
            direction: _selectedDirection,
            outcome: _selectedOutcome,
            subject: _subjectController.text,
            description: _descriptionController.text.isEmpty
                ? null
                : _descriptionController.text,
            durationMinutes: _durationMinutes,
            interactionAt: now,
            followUpAt: _followUpDate,
            followUpNotes: _followUpNotesController.text.isEmpty
                ? null
                : _followUpNotesController.text,
            createdAt: now,
            updatedAt: now,
          );
          result = await controller.createInteraction(interaction);
      }

      if (mounted) {
        if (result != null) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('تم حفظ التفاعل بنجاح'),
              backgroundColor: Color(0xFF367C2B),
            ),
          );
          Navigator.pop(context, result);
        } else {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('فشل في حفظ التفاعل'),
              backgroundColor: Colors.red,
            ),
          );
        }
      }
    } finally {
      if (mounted) {
        setState(() => _isSubmitting = false);
      }
    }
  }
}

/// Duration Input Dialog
class _DurationInputDialog extends StatefulWidget {
  final int? initialValue;

  const _DurationInputDialog({this.initialValue});

  @override
  State<_DurationInputDialog> createState() => _DurationInputDialogState();
}

class _DurationInputDialogState extends State<_DurationInputDialog> {
  late final TextEditingController _controller;

  @override
  void initState() {
    super.initState();
    _controller = TextEditingController(
      text: widget.initialValue?.toString() ?? '',
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('المدة بالدقائق'),
      content: TextField(
        controller: _controller,
        keyboardType: TextInputType.number,
        autofocus: true,
        decoration: const InputDecoration(
          suffixText: 'دقيقة',
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: const Text('إلغاء'),
        ),
        ElevatedButton(
          onPressed: () {
            final value = int.tryParse(_controller.text);
            Navigator.pop(context, value);
          },
          child: const Text('تأكيد'),
        ),
      ],
    );
  }
}
