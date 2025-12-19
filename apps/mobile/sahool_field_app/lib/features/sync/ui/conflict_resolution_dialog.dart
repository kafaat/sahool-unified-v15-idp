import 'package:flutter/material.dart';
import '../../../core/theme/sahool_theme.dart';
import '../../../core/storage/database.dart';

/// Conflict Resolution Choice
enum ConflictChoice {
  /// Keep local version
  keepLocal,

  /// Accept server version
  acceptServer,

  /// Review and merge manually
  reviewManually,
}

/// Conflict Resolution Dialog - حوار حل التعارضات
class ConflictResolutionDialog extends StatefulWidget {
  final SyncEvent conflict;
  final Map<String, dynamic>? localData;
  final Map<String, dynamic>? serverData;
  final Function(ConflictChoice) onResolved;

  const ConflictResolutionDialog({
    super.key,
    required this.conflict,
    this.localData,
    this.serverData,
    required this.onResolved,
  });

  @override
  State<ConflictResolutionDialog> createState() => _ConflictResolutionDialogState();
}

class _ConflictResolutionDialogState extends State<ConflictResolutionDialog> {
  ConflictChoice? _selectedChoice;
  bool _isProcessing = false;

  @override
  Widget build(BuildContext context) {
    return Dialog(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
      child: Container(
        width: MediaQuery.of(context).size.width * 0.9,
        constraints: const BoxConstraints(maxWidth: 400),
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            // Header
            _buildHeader(),

            const SizedBox(height: 20),

            // Conflict info
            _buildConflictInfo(),

            const SizedBox(height: 20),

            // Version comparison (if data available)
            if (widget.localData != null || widget.serverData != null) ...[
              _buildVersionComparison(),
              const SizedBox(height: 20),
            ],

            // Resolution options
            _buildResolutionOptions(),

            const SizedBox(height: 24),

            // Actions
            _buildActions(),
          ],
        ),
      ),
    );
  }

  Widget _buildHeader() {
    return Row(
      children: [
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: SahoolColors.warning.withOpacity(0.1),
            shape: BoxShape.circle,
          ),
          child: const Icon(
            Icons.warning_amber_rounded,
            color: SahoolColors.warning,
            size: 28,
          ),
        ),
        const SizedBox(width: 16),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'تعارض في البيانات',
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 18,
                ),
              ),
              const SizedBox(height: 4),
              Text(
                _getEntityTypeLabel(widget.conflict.entityType),
                style: TextStyle(
                  color: Colors.grey[600],
                  fontSize: 14,
                ),
              ),
            ],
          ),
        ),
        IconButton(
          onPressed: () => Navigator.pop(context),
          icon: const Icon(Icons.close),
          color: Colors.grey,
        ),
      ],
    );
  }

  Widget _buildConflictInfo() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: SahoolColors.warning.withOpacity(0.05),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: SahoolColors.warning.withOpacity(0.2)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.info_outline, size: 18, color: SahoolColors.warning),
              const SizedBox(width: 8),
              const Text(
                'ماذا حدث؟',
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            widget.conflict.message,
            style: TextStyle(color: Colors.grey[700]),
          ),
          const SizedBox(height: 12),
          Text(
            _formatConflictTime(widget.conflict.createdAt),
            style: TextStyle(color: Colors.grey[500], fontSize: 12),
          ),
        ],
      ),
    );
  }

  Widget _buildVersionComparison() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'مقارنة الإصدارات',
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 12),
        Row(
          children: [
            // Local version
            Expanded(
              child: _buildVersionCard(
                title: 'النسخة المحلية',
                icon: Icons.phone_android,
                color: SahoolColors.info,
                data: widget.localData,
                isSelected: _selectedChoice == ConflictChoice.keepLocal,
              ),
            ),
            const SizedBox(width: 12),
            // Server version
            Expanded(
              child: _buildVersionCard(
                title: 'نسخة السيرفر',
                icon: Icons.cloud,
                color: SahoolColors.primary,
                data: widget.serverData,
                isSelected: _selectedChoice == ConflictChoice.acceptServer,
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildVersionCard({
    required String title,
    required IconData icon,
    required Color color,
    required Map<String, dynamic>? data,
    required bool isSelected,
  }) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: isSelected ? color.withOpacity(0.1) : Colors.grey[50],
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: isSelected ? color : Colors.grey[200]!,
          width: isSelected ? 2 : 1,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(icon, size: 18, color: color),
              const SizedBox(width: 8),
              Text(
                title,
                style: TextStyle(
                  fontWeight: FontWeight.w500,
                  fontSize: 12,
                  color: color,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          if (data != null) ...[
            ...data.entries.take(3).map((e) => Padding(
                  padding: const EdgeInsets.only(bottom: 4),
                  child: Text(
                    '${e.key}: ${e.value}',
                    style: const TextStyle(fontSize: 11),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                )),
          ] else
            Text(
              'البيانات غير متوفرة',
              style: TextStyle(color: Colors.grey[500], fontSize: 11),
            ),
        ],
      ),
    );
  }

  Widget _buildResolutionOptions() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'اختر طريقة الحل',
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 12),
        _buildOptionTile(
          title: 'الاحتفاظ بنسختي',
          subtitle: 'استخدام التغييرات التي قمت بها',
          icon: Icons.phone_android,
          color: SahoolColors.info,
          choice: ConflictChoice.keepLocal,
        ),
        const SizedBox(height: 8),
        _buildOptionTile(
          title: 'قبول نسخة السيرفر',
          subtitle: 'استخدام أحدث نسخة من السيرفر',
          icon: Icons.cloud_done,
          color: SahoolColors.primary,
          choice: ConflictChoice.acceptServer,
        ),
        const SizedBox(height: 8),
        _buildOptionTile(
          title: 'مراجعة يدوياً',
          subtitle: 'فتح تفاصيل ${_getEntityTypeLabel(widget.conflict.entityType)} للمراجعة',
          icon: Icons.edit_note,
          color: SahoolColors.secondary,
          choice: ConflictChoice.reviewManually,
        ),
      ],
    );
  }

  Widget _buildOptionTile({
    required String title,
    required String subtitle,
    required IconData icon,
    required Color color,
    required ConflictChoice choice,
  }) {
    final isSelected = _selectedChoice == choice;

    return InkWell(
      onTap: () => setState(() => _selectedChoice = choice),
      borderRadius: BorderRadius.circular(12),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: isSelected ? color.withOpacity(0.1) : Colors.white,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: isSelected ? color : Colors.grey[200]!,
            width: isSelected ? 2 : 1,
          ),
        ),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: color.withOpacity(0.1),
                shape: BoxShape.circle,
              ),
              child: Icon(icon, size: 20, color: color),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: TextStyle(
                      fontWeight: FontWeight.w500,
                      color: isSelected ? color : Colors.black,
                    ),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    subtitle,
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.grey[600],
                    ),
                  ),
                ],
              ),
            ),
            Radio<ConflictChoice>(
              value: choice,
              groupValue: _selectedChoice,
              onChanged: (value) => setState(() => _selectedChoice = value),
              activeColor: color,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildActions() {
    return Row(
      children: [
        Expanded(
          child: OutlinedButton(
            onPressed: () => Navigator.pop(context),
            style: OutlinedButton.styleFrom(
              padding: const EdgeInsets.symmetric(vertical: 16),
            ),
            child: const Text('لاحقاً'),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: ElevatedButton(
            onPressed: _selectedChoice == null || _isProcessing ? null : _handleResolve,
            style: ElevatedButton.styleFrom(
              padding: const EdgeInsets.symmetric(vertical: 16),
            ),
            child: _isProcessing
                ? const SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  )
                : const Text('تطبيق'),
          ),
        ),
      ],
    );
  }

  void _handleResolve() async {
    if (_selectedChoice == null) return;

    setState(() => _isProcessing = true);

    try {
      widget.onResolved(_selectedChoice!);
      if (mounted) Navigator.pop(context);
    } finally {
      if (mounted) setState(() => _isProcessing = false);
    }
  }

  String _getEntityTypeLabel(String? type) {
    switch (type) {
      case 'field':
        return 'الحقل';
      case 'task':
        return 'المهمة';
      default:
        return 'البيانات';
    }
  }

  String _formatConflictTime(DateTime time) {
    final diff = DateTime.now().difference(time);
    if (diff.inMinutes < 60) return 'منذ ${diff.inMinutes} دقيقة';
    if (diff.inHours < 24) return 'منذ ${diff.inHours} ساعة';
    return 'منذ ${diff.inDays} يوم';
  }
}

/// Show conflict resolution dialog
Future<ConflictChoice?> showConflictResolutionDialog({
  required BuildContext context,
  required SyncEvent conflict,
  Map<String, dynamic>? localData,
  Map<String, dynamic>? serverData,
}) {
  return showDialog<ConflictChoice>(
    context: context,
    barrierDismissible: false,
    builder: (context) => ConflictResolutionDialog(
      conflict: conflict,
      localData: localData,
      serverData: serverData,
      onResolved: (choice) => Navigator.pop(context, choice),
    ),
  );
}

/// Conflict List Item Widget - عنصر قائمة التعارضات
class ConflictListItem extends StatelessWidget {
  final SyncEvent conflict;
  final VoidCallback onTap;
  final VoidCallback? onDismiss;

  const ConflictListItem({
    super.key,
    required this.conflict,
    required this.onTap,
    this.onDismiss,
  });

  @override
  Widget build(BuildContext context) {
    return Dismissible(
      key: Key('conflict_${conflict.id}'),
      direction: onDismiss != null ? DismissDirection.endToStart : DismissDirection.none,
      onDismissed: (_) => onDismiss?.call(),
      background: Container(
        alignment: Alignment.centerLeft,
        padding: const EdgeInsets.symmetric(horizontal: 20),
        decoration: BoxDecoration(
          color: SahoolColors.danger,
          borderRadius: BorderRadius.circular(12),
        ),
        child: const Icon(Icons.delete, color: Colors.white),
      ),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: SahoolColors.warning.withOpacity(0.3)),
            boxShadow: SahoolShadows.small,
          ),
          child: Row(
            children: [
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: SahoolColors.warning.withOpacity(0.1),
                  shape: BoxShape.circle,
                ),
                child: const Icon(
                  Icons.warning_amber_rounded,
                  color: SahoolColors.warning,
                  size: 20,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      _getEntityTitle(),
                      style: const TextStyle(fontWeight: FontWeight.w500),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      conflict.message,
                      style: TextStyle(
                        color: Colors.grey[600],
                        fontSize: 12,
                      ),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ],
                ),
              ),
              const Icon(Icons.chevron_left, color: Colors.grey),
            ],
          ),
        ),
      ),
    );
  }

  String _getEntityTitle() {
    final type = conflict.entityType ?? 'data';
    switch (type) {
      case 'field':
        return 'تعارض في بيانات الحقل';
      case 'task':
        return 'تعارض في المهمة';
      default:
        return 'تعارض في البيانات';
    }
  }
}
