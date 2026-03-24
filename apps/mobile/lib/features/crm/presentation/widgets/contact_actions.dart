/// Contact Actions Widget
/// أزرار التواصل السريع
///
/// Quick action buttons for contacting farmers (call, WhatsApp, SMS, etc.)
library;

import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';

import '../../domain/models/farmer_profile.dart';

/// Contact Actions Widget
/// ويدجت أزرار التواصل السريع
class ContactActions extends StatelessWidget {
  final FarmerProfile farmer;
  final Function(String action)? onActionCompleted;
  final bool showLabels;
  final bool isCompact;

  const ContactActions({
    super.key,
    required this.farmer,
    this.onActionCompleted,
    this.showLabels = true,
    this.isCompact = false,
  });

  @override
  Widget build(BuildContext context) {
    if (isCompact) {
      return _buildCompactActions(context);
    }

    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
      children: [
        _buildActionButton(
          context,
          icon: Icons.phone,
          label: 'اتصال',
          color: Colors.blue,
          onPressed: () => _makePhoneCall(context),
        ),
        _buildActionButton(
          context,
          icon: Icons.chat,
          label: 'واتساب',
          color: const Color(0xFF25D366),
          onPressed: () => _openWhatsApp(context),
        ),
        _buildActionButton(
          context,
          icon: Icons.sms,
          label: 'رسالة',
          color: Colors.purple,
          onPressed: () => _sendSms(context),
        ),
        if (farmer.email != null)
          _buildActionButton(
            context,
            icon: Icons.email,
            label: 'بريد',
            color: Colors.red,
            onPressed: () => _sendEmail(context),
          ),
        if (farmer.hasCoordinates)
          _buildActionButton(
            context,
            icon: Icons.location_on,
            label: 'موقع',
            color: Colors.orange,
            onPressed: () => _openMap(context),
          ),
      ],
    );
  }

  Widget _buildCompactActions(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        IconButton(
          icon: const Icon(Icons.phone),
          color: Colors.blue,
          onPressed: () => _makePhoneCall(context),
          tooltip: 'اتصال',
        ),
        IconButton(
          icon: const Icon(Icons.chat),
          color: const Color(0xFF25D366),
          onPressed: () => _openWhatsApp(context),
          tooltip: 'واتساب',
        ),
        IconButton(
          icon: const Icon(Icons.sms),
          color: Colors.purple,
          onPressed: () => _sendSms(context),
          tooltip: 'رسالة',
        ),
      ],
    );
  }

  Widget _buildActionButton(
    BuildContext context, {
    required IconData icon,
    required String label,
    required Color color,
    required VoidCallback onPressed,
  }) {
    if (showLabels) {
      return Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Material(
            color: color.withValues(alpha: 0.1),
            shape: const CircleBorder(),
            child: InkWell(
              onTap: onPressed,
              customBorder: const CircleBorder(),
              child: Padding(
                padding: const EdgeInsets.all(12),
                child: Icon(icon, color: color, size: 24),
              ),
            ),
          ),
          const SizedBox(height: 4),
          Text(
            label,
            style: TextStyle(
              fontSize: 11,
              color: Colors.grey[600],
            ),
          ),
        ],
      );
    }

    return IconButton(
      icon: Icon(icon),
      color: color,
      onPressed: onPressed,
      tooltip: label,
    );
  }

  Future<void> _makePhoneCall(BuildContext context) async {
    final phone = farmer.phone.replaceAll(RegExp(r'[^\d+]'), '');
    final uri = Uri.parse('tel:$phone');

    if (await canLaunchUrl(uri)) {
      await launchUrl(uri);
      onActionCompleted?.call('call');
    } else {
      if (context.mounted) {
        _showError(context, 'لا يمكن إجراء المكالمة');
      }
    }
  }

  Future<void> _openWhatsApp(BuildContext context) async {
    final phone = (farmer.whatsappNumber ?? farmer.phone)
        .replaceAll(RegExp(r'[^\d]'), '');

    // Add country code if not present (assuming Yemen +967)
    final formattedPhone = phone.startsWith('967') ? phone : '967$phone';

    final uri = Uri.parse('https://wa.me/$formattedPhone');

    if (await canLaunchUrl(uri)) {
      await launchUrl(uri, mode: LaunchMode.externalApplication);
      onActionCompleted?.call('whatsapp');
    } else {
      if (context.mounted) {
        _showError(context, 'لا يمكن فتح واتساب');
      }
    }
  }

  Future<void> _sendSms(BuildContext context) async {
    final phone = farmer.phone.replaceAll(RegExp(r'[^\d+]'), '');
    final uri = Uri.parse('sms:$phone');

    if (await canLaunchUrl(uri)) {
      await launchUrl(uri);
      onActionCompleted?.call('sms');
    } else {
      if (context.mounted) {
        _showError(context, 'لا يمكن إرسال الرسالة');
      }
    }
  }

  Future<void> _sendEmail(BuildContext context) async {
    if (farmer.email == null) return;

    final uri = Uri.parse('mailto:${farmer.email}');

    if (await canLaunchUrl(uri)) {
      await launchUrl(uri);
      onActionCompleted?.call('email');
    } else {
      if (context.mounted) {
        _showError(context, 'لا يمكن فتح البريد الإلكتروني');
      }
    }
  }

  Future<void> _openMap(BuildContext context) async {
    if (!farmer.hasCoordinates) return;

    // Try Google Maps first, then Apple Maps
    final googleMapsUri = Uri.parse(
      'https://www.google.com/maps/search/?api=1&query=${farmer.latitude},${farmer.longitude}',
    );

    if (await canLaunchUrl(googleMapsUri)) {
      await launchUrl(googleMapsUri, mode: LaunchMode.externalApplication);
      onActionCompleted?.call('location');
    } else {
      if (context.mounted) {
        _showError(context, 'لا يمكن فتح الخريطة');
      }
    }
  }

  void _showError(BuildContext context, String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        behavior: SnackBarBehavior.floating,
      ),
    );
  }
}

/// Quick Contact Sheet
/// نافذة التواصل السريع
class QuickContactSheet extends StatelessWidget {
  final FarmerProfile farmer;
  final Function(String action)? onActionCompleted;

  const QuickContactSheet({
    super.key,
    required this.farmer,
    this.onActionCompleted,
  });

  static Future<void> show(
    BuildContext context, {
    required FarmerProfile farmer,
    Function(String action)? onActionCompleted,
  }) {
    return showModalBottomSheet(
      context: context,
      builder: (context) => QuickContactSheet(
        farmer: farmer,
        onActionCompleted: onActionCompleted,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: Column(
        mainAxisSize: MainAxisSize.min,
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

          // Farmer info
          Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              children: [
                CircleAvatar(
                  radius: 24,
                  backgroundColor: Colors.blue.withValues(alpha: 0.2),
                  backgroundImage: farmer.avatarUrl != null
                      ? NetworkImage(farmer.avatarUrl!)
                      : null,
                  child: farmer.avatarUrl == null
                      ? Text(
                          farmer.name.substring(0, 1).toUpperCase(),
                          style: const TextStyle(
                            color: Colors.blue,
                            fontWeight: FontWeight.bold,
                            fontSize: 18,
                          ),
                        )
                      : null,
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        farmer.displayName,
                        style: Theme.of(context).textTheme.titleMedium?.copyWith(
                              fontWeight: FontWeight.bold,
                            ),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        farmer.phone,
                        style: TextStyle(
                          color: Colors.grey[600],
                          fontSize: 14,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),

          const Divider(height: 1),

          // Actions
          _buildActionTile(
            context,
            icon: Icons.phone,
            label: 'اتصال هاتفي',
            subtitle: farmer.phone,
            color: Colors.blue,
            onTap: () => _handleAction(context, 'call'),
          ),

          _buildActionTile(
            context,
            icon: Icons.chat,
            label: 'رسالة واتساب',
            subtitle: farmer.whatsappNumber ?? farmer.phone,
            color: const Color(0xFF25D366),
            onTap: () => _handleAction(context, 'whatsapp'),
          ),

          _buildActionTile(
            context,
            icon: Icons.sms,
            label: 'رسالة نصية',
            subtitle: farmer.phone,
            color: Colors.purple,
            onTap: () => _handleAction(context, 'sms'),
          ),

          if (farmer.email != null)
            _buildActionTile(
              context,
              icon: Icons.email,
              label: 'بريد إلكتروني',
              subtitle: farmer.email!,
              color: Colors.red,
              onTap: () => _handleAction(context, 'email'),
            ),

          if (farmer.hasCoordinates)
            _buildActionTile(
              context,
              icon: Icons.location_on,
              label: 'عرض الموقع',
              subtitle: farmer.fullLocation,
              color: Colors.orange,
              onTap: () => _handleAction(context, 'location'),
            ),

          const SizedBox(height: 16),
        ],
      ),
    );
  }

  Widget _buildActionTile(
    BuildContext context, {
    required IconData icon,
    required String label,
    required String subtitle,
    required Color color,
    required VoidCallback onTap,
  }) {
    return ListTile(
      leading: Container(
        padding: const EdgeInsets.all(8),
        decoration: BoxDecoration(
          color: color.withValues(alpha: 0.1),
          shape: BoxShape.circle,
        ),
        child: Icon(icon, color: color, size: 24),
      ),
      title: Text(label),
      subtitle: Text(
        subtitle,
        style: TextStyle(
          color: Colors.grey[500],
          fontSize: 12,
        ),
      ),
      trailing: Icon(Icons.chevron_left, color: Colors.grey[400]),
      onTap: onTap,
    );
  }

  Future<void> _handleAction(BuildContext context, String action) async {
    Navigator.pop(context);

    final contactActions = ContactActions(
      farmer: farmer,
      onActionCompleted: onActionCompleted,
    );

    switch (action) {
      case 'call':
        await contactActions._makePhoneCall(context);
        break;
      case 'whatsapp':
        await contactActions._openWhatsApp(context);
        break;
      case 'sms':
        await contactActions._sendSms(context);
        break;
      case 'email':
        await contactActions._sendEmail(context);
        break;
      case 'location':
        await contactActions._openMap(context);
        break;
    }
  }
}

/// Floating Contact FAB
/// زر التواصل العائم
class ContactFAB extends StatelessWidget {
  final FarmerProfile farmer;
  final Function(String action)? onActionCompleted;

  const ContactFAB({
    super.key,
    required this.farmer,
    this.onActionCompleted,
  });

  @override
  Widget build(BuildContext context) {
    return FloatingActionButton(
      onPressed: () => QuickContactSheet.show(
        context,
        farmer: farmer,
        onActionCompleted: onActionCompleted,
      ),
      backgroundColor: const Color(0xFF367C2B),
      child: const Icon(Icons.contact_phone, color: Colors.white),
    );
  }
}
