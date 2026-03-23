/// Farmer Card Widget
/// بطاقة المزارع
///
/// Displays farmer summary information in a card format
library;

import 'package:flutter/material.dart';

import '../../domain/models/farmer_profile.dart';

/// Farmer Card Widget
/// بطاقة عرض ملخص بيانات المزارع
class FarmerCard extends StatelessWidget {
  final FarmerProfile farmer;
  final VoidCallback? onTap;
  final VoidCallback? onCall;
  final VoidCallback? onWhatsApp;
  final bool showActions;
  final bool isCompact;

  const FarmerCard({
    super.key,
    required this.farmer,
    this.onTap,
    this.onCall,
    this.onWhatsApp,
    this.showActions = true,
    this.isCompact = false,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: EdgeInsets.all(isCompact ? 12 : 16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header row
              Row(
                children: [
                  // Avatar
                  _buildAvatar(),
                  const SizedBox(width: 12),

                  // Name and info
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Expanded(
                              child: Text(
                                farmer.displayName,
                                style: theme.textTheme.titleMedium?.copyWith(
                                  fontWeight: FontWeight.bold,
                                ),
                                maxLines: 1,
                                overflow: TextOverflow.ellipsis,
                              ),
                            ),
                            if (farmer.isPremium) ...[
                              const SizedBox(width: 4),
                              Icon(
                                Icons.star,
                                size: 16,
                                color: Colors.amber[700],
                              ),
                            ],
                          ],
                        ),
                        const SizedBox(height: 2),
                        Text(
                          farmer.phone,
                          style: theme.textTheme.bodyMedium?.copyWith(
                            color: Colors.grey[600],
                          ),
                        ),
                      ],
                    ),
                  ),

                  // Status badge
                  _buildStatusBadge(theme),
                ],
              ),

              if (!isCompact) ...[
                const SizedBox(height: 12),
                const Divider(height: 1),
                const SizedBox(height: 12),

                // Info row
                Row(
                  children: [
                    // Location
                    Expanded(
                      child: _buildInfoItem(
                        Icons.location_on_outlined,
                        farmer.fullLocation,
                        theme,
                      ),
                    ),

                    // Segment
                    _buildSegmentChip(theme),
                  ],
                ),

                if (farmer.mainCrops.isNotEmpty) ...[
                  const SizedBox(height: 8),
                  _buildCropsRow(theme),
                ],

                if (farmer.totalAreaHectares != null) ...[
                  const SizedBox(height: 8),
                  _buildAreaRow(theme),
                ],
              ],

              // Quick actions
              if (showActions && !isCompact) ...[
                const SizedBox(height: 12),
                _buildActionsRow(context),
              ],

              // Compact actions
              if (showActions && isCompact) ...[
                const SizedBox(height: 8),
                _buildCompactActionsRow(),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildAvatar() {
    return CircleAvatar(
      radius: isCompact ? 20 : 24,
      backgroundColor: _getSegmentColor().withOpacity(0.2),
      backgroundImage:
          farmer.avatarUrl != null ? NetworkImage(farmer.avatarUrl!) : null,
      child: farmer.avatarUrl == null
          ? Text(
              _getInitials(),
              style: TextStyle(
                color: _getSegmentColor(),
                fontWeight: FontWeight.bold,
                fontSize: isCompact ? 14 : 16,
              ),
            )
          : null,
    );
  }

  Widget _buildStatusBadge(ThemeData theme) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: _getStatusColor().withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: 6,
            height: 6,
            decoration: BoxDecoration(
              color: _getStatusColor(),
              shape: BoxShape.circle,
            ),
          ),
          const SizedBox(width: 4),
          Text(
            farmer.statusAr,
            style: TextStyle(
              color: _getStatusColor(),
              fontSize: 11,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSegmentChip(ThemeData theme) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: _getSegmentColor().withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: _getSegmentColor().withOpacity(0.3),
          width: 1,
        ),
      ),
      child: Text(
        farmer.segmentAr,
        style: TextStyle(
          color: _getSegmentColor(),
          fontSize: 11,
          fontWeight: FontWeight.w600,
        ),
      ),
    );
  }

  Widget _buildInfoItem(IconData icon, String text, ThemeData theme) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(icon, size: 14, color: Colors.grey[500]),
        const SizedBox(width: 4),
        Flexible(
          child: Text(
            text,
            style: TextStyle(
              color: Colors.grey[600],
              fontSize: 12,
            ),
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
        ),
      ],
    );
  }

  Widget _buildCropsRow(ThemeData theme) {
    return Row(
      children: [
        Icon(Icons.eco_outlined, size: 14, color: Colors.grey[500]),
        const SizedBox(width: 4),
        Expanded(
          child: Wrap(
            spacing: 4,
            runSpacing: 4,
            children: farmer.mainCrops.take(3).map((crop) {
              return Container(
                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                decoration: BoxDecoration(
                  color: Colors.green.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(4),
                ),
                child: Text(
                  crop,
                  style: const TextStyle(
                    color: Colors.green,
                    fontSize: 10,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              );
            }).toList(),
          ),
        ),
      ],
    );
  }

  Widget _buildAreaRow(ThemeData theme) {
    return Row(
      children: [
        Icon(Icons.landscape_outlined, size: 14, color: Colors.grey[500]),
        const SizedBox(width: 4),
        Text(
          '${farmer.totalAreaHectares!.toStringAsFixed(1)} هكتار',
          style: TextStyle(
            color: Colors.grey[600],
            fontSize: 12,
          ),
        ),
        if (farmer.fieldCount != null) ...[
          const SizedBox(width: 12),
          Icon(Icons.grid_view_outlined, size: 14, color: Colors.grey[500]),
          const SizedBox(width: 4),
          Text(
            '${farmer.fieldCount} حقول',
            style: TextStyle(
              color: Colors.grey[600],
              fontSize: 12,
            ),
          ),
        ],
      ],
    );
  }

  Widget _buildActionsRow(BuildContext context) {
    return Row(
      children: [
        // Call button
        Expanded(
          child: OutlinedButton.icon(
            onPressed: onCall,
            icon: const Icon(Icons.phone_outlined, size: 18),
            label: const Text('اتصال'),
            style: OutlinedButton.styleFrom(
              foregroundColor: Colors.blue,
              side: const BorderSide(color: Colors.blue),
              padding: const EdgeInsets.symmetric(vertical: 8),
            ),
          ),
        ),
        const SizedBox(width: 8),

        // WhatsApp button
        Expanded(
          child: OutlinedButton.icon(
            onPressed: onWhatsApp,
            icon: const Icon(Icons.chat_outlined, size: 18),
            label: const Text('واتساب'),
            style: OutlinedButton.styleFrom(
              foregroundColor: const Color(0xFF25D366),
              side: const BorderSide(color: Color(0xFF25D366)),
              padding: const EdgeInsets.symmetric(vertical: 8),
            ),
          ),
        ),

        const SizedBox(width: 8),

        // More menu
        IconButton(
          onPressed: () => _showMoreMenu(context),
          icon: Icon(Icons.more_vert, color: Colors.grey[600]),
          padding: EdgeInsets.zero,
          constraints: const BoxConstraints(),
        ),
      ],
    );
  }

  Widget _buildCompactActionsRow() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.end,
      children: [
        IconButton(
          onPressed: onCall,
          icon: const Icon(Icons.phone, size: 20),
          color: Colors.blue,
          padding: EdgeInsets.zero,
          constraints: const BoxConstraints(),
        ),
        const SizedBox(width: 12),
        IconButton(
          onPressed: onWhatsApp,
          icon: const Icon(Icons.chat, size: 20),
          color: const Color(0xFF25D366),
          padding: EdgeInsets.zero,
          constraints: const BoxConstraints(),
        ),
      ],
    );
  }

  void _showMoreMenu(BuildContext context) {
    showModalBottomSheet(
      context: context,
      builder: (context) => SafeArea(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            ListTile(
              leading: const Icon(Icons.edit_outlined),
              title: const Text('تعديل'),
              onTap: () {
                Navigator.pop(context);
                // Navigate to edit
              },
            ),
            ListTile(
              leading: const Icon(Icons.history),
              title: const Text('سجل التفاعلات'),
              onTap: () {
                Navigator.pop(context);
                // Navigate to history
              },
            ),
            ListTile(
              leading: const Icon(Icons.analytics_outlined),
              title: const Text('التحليلات'),
              onTap: () {
                Navigator.pop(context);
                // Navigate to analytics
              },
            ),
            ListTile(
              leading: const Icon(Icons.note_add_outlined),
              title: const Text('إضافة ملاحظة'),
              onTap: () {
                Navigator.pop(context);
                // Add note
              },
            ),
          ],
        ),
      ),
    );
  }

  String _getInitials() {
    final parts = farmer.name.split(' ');
    if (parts.length >= 2) {
      return '${parts[0][0]}${parts[1][0]}'.toUpperCase();
    }
    return farmer.name.substring(0, 1).toUpperCase();
  }

  Color _getStatusColor() {
    switch (farmer.status) {
      case FarmerStatus.active:
        return Colors.green;
      case FarmerStatus.inactive:
        return Colors.grey;
      case FarmerStatus.pending:
        return Colors.orange;
      case FarmerStatus.suspended:
        return Colors.red;
    }
  }

  Color _getSegmentColor() {
    switch (farmer.segment) {
      case FarmerSegment.premium:
        return Colors.amber[700]!;
      case FarmerSegment.regular:
        return Colors.blue;
      case FarmerSegment.newFarmer:
        return Colors.green;
      case FarmerSegment.potential:
        return Colors.purple;
    }
  }
}
