/// Farmer Profile Screen
/// شاشة ملف المزارع
///
/// Displays detailed farmer profile with interactions and opportunities

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../../domain/models/farmer_profile.dart';
import '../../domain/models/interaction.dart';
import '../../domain/models/opportunity.dart';
import '../../state/crm_providers.dart';
import '../widgets/contact_actions.dart';
import '../widgets/interaction_timeline.dart';
import 'interaction_history_screen.dart' hide AddInteractionScreen;
import 'add_interaction_screen.dart';
import 'farmer_analytics_screen.dart';

/// Farmer Profile Screen
/// شاشة عرض تفاصيل ملف المزارع
class FarmerProfileScreen extends ConsumerWidget {
  final String farmerId;

  const FarmerProfileScreen({super.key, required this.farmerId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final farmerAsync = ref.watch(farmerDetailsProvider(farmerId));

    return farmerAsync.when(
      data: (farmer) => _FarmerProfileContent(farmer: farmer),
      loading: () => const Scaffold(
        body: Center(child: CircularProgressIndicator()),
      ),
      error: (error, _) => Scaffold(
        appBar: AppBar(title: const Text('ملف المزارع')),
        body: Center(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(Icons.error_outline, size: 64, color: Colors.red[300]),
              const SizedBox(height: 16),
              Text(error.toString()),
              const SizedBox(height: 16),
              ElevatedButton(
                onPressed: () => ref.invalidate(farmerDetailsProvider(farmerId)),
                child: const Text('إعادة المحاولة'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _FarmerProfileContent extends ConsumerWidget {
  final FarmerProfile farmer;

  const _FarmerProfileContent({required this.farmer});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final interactionsAsync = ref.watch(farmerInteractionsProvider(farmer.id));
    final opportunitiesAsync = ref.watch(farmerOpportunitiesProvider(farmer.id));

    return Scaffold(
      body: CustomScrollView(
        slivers: [
          // App bar with farmer info
          _buildSliverAppBar(context),

          // Content
          SliverPadding(
            padding: const EdgeInsets.all(16),
            sliver: SliverList(
              delegate: SliverChildListDelegate([
                // Quick actions
                ContactActions(farmer: farmer),

                const SizedBox(height: 24),

                // Stats summary
                _buildStatsSummary(context),

                const SizedBox(height: 24),

                // Contact info
                _buildContactSection(context),

                const SizedBox(height: 24),

                // Location info
                if (farmer.governorate != null || farmer.hasCoordinates)
                  _buildLocationSection(context),

                const SizedBox(height: 24),

                // Farm info
                if (farmer.totalAreaHectares != null || farmer.mainCrops.isNotEmpty)
                  _buildFarmSection(context),

                const SizedBox(height: 24),

                // Recent interactions
                _buildInteractionsSection(context, ref, interactionsAsync),

                const SizedBox(height: 24),

                // Opportunities
                _buildOpportunitiesSection(context, ref, opportunitiesAsync),

                const SizedBox(height: 24),

                // Notes
                if (farmer.notes != null && farmer.notes!.isNotEmpty)
                  _buildNotesSection(context),

                const SizedBox(height: 80), // Space for FAB
              ]),
            ),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => _navigateToAddInteraction(context),
        backgroundColor: const Color(0xFF367C2B),
        icon: const Icon(Icons.add, color: Colors.white),
        label: const Text('تفاعل جديد', style: TextStyle(color: Colors.white)),
      ),
    );
  }

  Widget _buildSliverAppBar(BuildContext context) {
    return SliverAppBar(
      expandedHeight: 200,
      pinned: true,
      flexibleSpace: FlexibleSpaceBar(
        background: Container(
          decoration: BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topCenter,
              end: Alignment.bottomCenter,
              colors: [
                const Color(0xFF367C2B),
                const Color(0xFF367C2B).withOpacity(0.8),
              ],
            ),
          ),
          child: SafeArea(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const SizedBox(height: 40),
                // Avatar
                CircleAvatar(
                  radius: 40,
                  backgroundColor: Colors.white.withOpacity(0.2),
                  backgroundImage: farmer.avatarUrl != null
                      ? NetworkImage(farmer.avatarUrl!)
                      : null,
                  child: farmer.avatarUrl == null
                      ? Text(
                          _getInitials(),
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 28,
                            fontWeight: FontWeight.bold,
                          ),
                        )
                      : null,
                ),
                const SizedBox(height: 12),
                // Name
                Text(
                  farmer.displayName,
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 4),
                // Badges
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    _buildBadge(farmer.statusAr, _getStatusColor()),
                    const SizedBox(width: 8),
                    _buildBadge(farmer.segmentAr, _getSegmentColor()),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
      actions: [
        IconButton(
          icon: const Icon(Icons.edit),
          onPressed: () => _navigateToEdit(context),
        ),
        PopupMenuButton<String>(
          onSelected: (value) => _handleMenuAction(context, value),
          itemBuilder: (context) => [
            const PopupMenuItem(
              value: 'analytics',
              child: ListTile(
                leading: Icon(Icons.analytics_outlined),
                title: Text('التحليلات'),
                contentPadding: EdgeInsets.zero,
              ),
            ),
            const PopupMenuItem(
              value: 'history',
              child: ListTile(
                leading: Icon(Icons.history),
                title: Text('سجل التفاعلات'),
                contentPadding: EdgeInsets.zero,
              ),
            ),
            const PopupMenuItem(
              value: 'share',
              child: ListTile(
                leading: Icon(Icons.share),
                title: Text('مشاركة'),
                contentPadding: EdgeInsets.zero,
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildBadge(String label, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.2),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Text(
        label,
        style: const TextStyle(
          color: Colors.white,
          fontSize: 12,
          fontWeight: FontWeight.w500,
        ),
      ),
    );
  }

  Widget _buildStatsSummary(BuildContext context) {
    return Row(
      children: [
        Expanded(
          child: _buildStatCard(
            Icons.touch_app,
            farmer.interactionCount.toString(),
            'التفاعلات',
            Colors.blue,
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _buildStatCard(
            Icons.access_time,
            farmer.lastInteractionAt != null
                ? _formatDate(farmer.lastInteractionAt!)
                : 'لا يوجد',
            'آخر تفاعل',
            Colors.green,
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _buildStatCard(
            Icons.star,
            farmer.rating?.toStringAsFixed(1) ?? '-',
            'التقييم',
            Colors.amber,
          ),
        ),
      ],
    );
  }

  Widget _buildStatCard(
    IconData icon,
    String value,
    String label,
    Color color,
  ) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        children: [
          Icon(icon, color: color, size: 24),
          const SizedBox(height: 8),
          Text(
            value,
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
          const SizedBox(height: 2),
          Text(
            label,
            style: TextStyle(
              fontSize: 10,
              color: Colors.grey[600],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildContactSection(BuildContext context) {
    return _buildSection(
      'معلومات الاتصال',
      Column(
        children: [
          _buildInfoRow(Icons.phone, 'الهاتف', farmer.phone),
          if (farmer.phoneAlt != null)
            _buildInfoRow(Icons.phone_android, 'هاتف بديل', farmer.phoneAlt!),
          if (farmer.whatsappNumber != null)
            _buildInfoRow(Icons.chat, 'واتساب', farmer.whatsappNumber!),
          if (farmer.email != null)
            _buildInfoRow(Icons.email, 'البريد', farmer.email!),
          _buildInfoRow(
            Icons.language,
            'لغة التواصل',
            farmer.languagePreference == LanguagePreference.arabic
                ? 'العربية'
                : farmer.languagePreference == LanguagePreference.english
                    ? 'الإنجليزية'
                    : 'كلاهما',
          ),
        ],
      ),
    );
  }

  Widget _buildLocationSection(BuildContext context) {
    return _buildSection(
      'الموقع',
      Column(
        children: [
          if (farmer.governorate != null)
            _buildInfoRow(Icons.location_city, 'المحافظة', farmer.governorate!),
          if (farmer.district != null)
            _buildInfoRow(Icons.location_on, 'المديرية', farmer.district!),
          if (farmer.village != null)
            _buildInfoRow(Icons.home, 'القرية', farmer.village!),
          if (farmer.address != null)
            _buildInfoRow(Icons.place, 'العنوان', farmer.address!),
          if (farmer.hasCoordinates)
            ListTile(
              leading: const Icon(Icons.map, color: Colors.orange),
              title: const Text('عرض على الخريطة'),
              trailing: const Icon(Icons.chevron_left),
              contentPadding: EdgeInsets.zero,
              onTap: () {
                // Open map
              },
            ),
        ],
      ),
    );
  }

  Widget _buildFarmSection(BuildContext context) {
    return _buildSection(
      'معلومات المزرعة',
      Column(
        children: [
          if (farmer.totalAreaHectares != null)
            _buildInfoRow(
              Icons.landscape,
              'المساحة',
              '${farmer.totalAreaHectares!.toStringAsFixed(1)} هكتار',
            ),
          if (farmer.fieldCount != null)
            _buildInfoRow(
              Icons.grid_view,
              'عدد الحقول',
              '${farmer.fieldCount}',
            ),
          if (farmer.waterSource != null)
            _buildInfoRow(Icons.water_drop, 'مصدر المياه', farmer.waterSource!),
          if (farmer.irrigationType != null)
            _buildInfoRow(Icons.grass, 'نوع الري', farmer.irrigationType!),
          if (farmer.mainCrops.isNotEmpty) ...[
            const SizedBox(height: 8),
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Icon(Icons.eco, size: 20, color: Colors.grey[600]),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'المحاصيل الرئيسية',
                        style: TextStyle(
                          color: Colors.grey[600],
                          fontSize: 12,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Wrap(
                        spacing: 4,
                        runSpacing: 4,
                        children: farmer.mainCrops.map((crop) {
                          return Chip(
                            label: Text(crop),
                            backgroundColor: Colors.green.withOpacity(0.1),
                            labelStyle: const TextStyle(
                              fontSize: 12,
                              color: Colors.green,
                            ),
                            padding: EdgeInsets.zero,
                            materialTapTargetSize:
                                MaterialTapTargetSize.shrinkWrap,
                          );
                        }).toList(),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildInteractionsSection(
    BuildContext context,
    WidgetRef ref,
    AsyncValue<List<Interaction>> interactionsAsync,
  ) {
    return _buildSection(
      'التفاعلات الأخيرة',
      interactionsAsync.when(
        data: (interactions) {
          if (interactions.isEmpty) {
            return Center(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Text(
                  'لا توجد تفاعلات',
                  style: TextStyle(color: Colors.grey[500]),
                ),
              ),
            );
          }
          return InteractionTimeline(
            interactions: interactions.take(5).toList(),
            maxItems: 5,
            onInteractionTap: (interaction) {
              // View interaction details
            },
          );
        },
        loading: () => const Center(
          child: Padding(
            padding: EdgeInsets.all(16),
            child: CircularProgressIndicator(),
          ),
        ),
        error: (error, _) => Center(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Text(
              error.toString(),
              style: TextStyle(color: Colors.red[400]),
            ),
          ),
        ),
      ),
      trailing: TextButton(
        onPressed: () => _navigateToInteractionHistory(context),
        child: const Text('عرض الكل'),
      ),
    );
  }

  Widget _buildOpportunitiesSection(
    BuildContext context,
    WidgetRef ref,
    AsyncValue<List<Opportunity>> opportunitiesAsync,
  ) {
    return _buildSection(
      'الفرص',
      opportunitiesAsync.when(
        data: (opportunities) {
          if (opportunities.isEmpty) {
            return Center(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  children: [
                    Text(
                      'لا توجد فرص',
                      style: TextStyle(color: Colors.grey[500]),
                    ),
                    const SizedBox(height: 8),
                    TextButton.icon(
                      onPressed: () {
                        // Add opportunity
                      },
                      icon: const Icon(Icons.add),
                      label: const Text('إضافة فرصة'),
                    ),
                  ],
                ),
              ),
            );
          }
          return Column(
            children: opportunities.take(3).map((opp) {
              return _buildOpportunityTile(context, opp);
            }).toList(),
          );
        },
        loading: () => const Center(
          child: Padding(
            padding: EdgeInsets.all(16),
            child: CircularProgressIndicator(),
          ),
        ),
        error: (error, _) => Center(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Text(
              error.toString(),
              style: TextStyle(color: Colors.red[400]),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildOpportunityTile(BuildContext context, Opportunity opportunity) {
    return ListTile(
      contentPadding: EdgeInsets.zero,
      leading: Container(
        padding: const EdgeInsets.all(8),
        decoration: BoxDecoration(
          color: _getStageColor(opportunity.stage).withOpacity(0.1),
          borderRadius: BorderRadius.circular(8),
        ),
        child: Icon(
          Icons.lightbulb_outline,
          color: _getStageColor(opportunity.stage),
        ),
      ),
      title: Text(
        opportunity.displayName,
        style: const TextStyle(fontWeight: FontWeight.w600),
      ),
      subtitle: Text(
        '${opportunity.stageAr} - ${opportunity.formattedExpectedAmount}',
        style: TextStyle(color: Colors.grey[600], fontSize: 12),
      ),
      trailing: const Icon(Icons.chevron_left),
      onTap: () {
        // View opportunity
      },
    );
  }

  Widget _buildNotesSection(BuildContext context) {
    return _buildSection(
      'ملاحظات',
      Text(
        farmer.notes!,
        style: TextStyle(color: Colors.grey[700]),
      ),
    );
  }

  Widget _buildSection(
    String title,
    Widget content, {
    Widget? trailing,
  }) {
    return Card(
      elevation: 1,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const Spacer(),
                if (trailing != null) trailing,
              ],
            ),
            const SizedBox(height: 12),
            content,
          ],
        ),
      ),
    );
  }

  Widget _buildInfoRow(IconData icon, String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Row(
        children: [
          Icon(icon, size: 20, color: Colors.grey[600]),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  label,
                  style: TextStyle(
                    color: Colors.grey[500],
                    fontSize: 11,
                  ),
                ),
                Text(
                  value,
                  style: const TextStyle(fontSize: 14),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  void _navigateToEdit(BuildContext context) {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('تعديل المزارع')),
    );
  }

  void _navigateToAddInteraction(BuildContext context) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => AddInteractionScreen(
          farmerId: farmer.id,
          farmerName: farmer.displayName,
        ),
      ),
    );
  }

  void _navigateToInteractionHistory(BuildContext context) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => InteractionHistoryScreen(
          farmerId: farmer.id,
          farmerName: farmer.displayName,
        ),
      ),
    );
  }

  void _handleMenuAction(BuildContext context, String action) {
    switch (action) {
      case 'analytics':
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => FarmerAnalyticsScreen(
              farmerId: farmer.id,
              farmerName: farmer.displayName,
            ),
          ),
        );
        break;
      case 'history':
        _navigateToInteractionHistory(context);
        break;
      case 'share':
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('مشاركة بيانات المزارع')),
        );
        break;
    }
  }

  String _getInitials() {
    final parts = farmer.name.split(' ');
    if (parts.length >= 2) {
      return '${parts[0][0]}${parts[1][0]}'.toUpperCase();
    }
    return farmer.name.substring(0, 1).toUpperCase();
  }

  String _formatDate(DateTime date) {
    final now = DateTime.now();
    final diff = now.difference(date);

    if (diff.inDays == 0) {
      return 'اليوم';
    } else if (diff.inDays == 1) {
      return 'أمس';
    } else if (diff.inDays < 7) {
      return 'منذ ${diff.inDays} أيام';
    } else {
      return DateFormat('d/M/yyyy').format(date);
    }
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
        return Colors.amber;
      case FarmerSegment.regular:
        return Colors.blue;
      case FarmerSegment.newFarmer:
        return Colors.green;
      case FarmerSegment.potential:
        return Colors.purple;
    }
  }

  Color _getStageColor(OpportunityStage stage) {
    switch (stage) {
      case OpportunityStage.lead:
        return Colors.grey;
      case OpportunityStage.qualified:
        return Colors.blue;
      case OpportunityStage.proposal:
        return Colors.orange;
      case OpportunityStage.negotiation:
        return Colors.purple;
      case OpportunityStage.closedWon:
        return Colors.green;
      case OpportunityStage.closedLost:
        return Colors.red;
    }
  }
}
