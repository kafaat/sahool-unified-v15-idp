import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/config/theme.dart';
import '../../state/settings_providers.dart';
import '../widgets/widgets.dart';

/// Notification Settings Screen
/// شاشة إعدادات الإشعارات
class NotificationSettingsScreen extends ConsumerWidget {
  const NotificationSettingsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final settings = ref.watch(appSettingsProvider);
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Directionality(
      textDirection: TextDirection.rtl,
      child: Scaffold(
        backgroundColor: isDark ? Colors.black : Colors.grey[100],
        appBar: AppBar(
          backgroundColor: isDark ? Colors.grey[900] : Colors.white,
          elevation: 0,
          title: Text(
            'إعدادات الإشعارات',
            style: TextStyle(
              color: isDark ? Colors.white : Colors.black87,
              fontWeight: FontWeight.bold,
            ),
          ),
          centerTitle: true,
          leading: IconButton(
            icon: const Icon(Icons.arrow_forward_ios),
            color: isDark ? Colors.white : Colors.black87,
            onPressed: () => Navigator.pop(context),
          ),
        ),
        body: ListView(
          padding: const EdgeInsets.only(bottom: 32),
          children: [
            // Master toggle
            SettingsSection(
              title: 'General',
              titleAr: 'عام',
              icon: Icons.notifications_outlined,
              children: [
                SwitchSettingsTile(
                  title: 'Enable Notifications',
                  titleAr: 'تفعيل الإشعارات',
                  icon: Icons.notifications_rounded,
                  value: settings.notificationsEnabled,
                  dynamicSubtitle: (v) => v
                      ? 'ستتلقى إشعارات من التطبيق'
                      : 'لن تتلقى أي إشعارات',
                  onChanged: (value) {
                    ref.read(appSettingsProvider.notifier).setNotificationsEnabled(value);
                  },
                ),
              ],
            ),

            // Notification categories
            SettingsSection(
              title: 'Categories',
              titleAr: 'الفئات',
              icon: Icons.category_outlined,
              subtitle: 'اختر أنواع الإشعارات التي تريد استلامها',
              showDividers: true,
              children: [
                SwitchSettingsTile(
                  title: 'Alerts',
                  titleAr: 'التنبيهات',
                  icon: Icons.warning_amber_rounded,
                  iconColor: SahoolTheme.warning,
                  value: settings.alertsEnabled,
                  subtitle: 'تنبيهات الآفات والأمراض والطوارئ',
                  enabled: settings.notificationsEnabled,
                  onChanged: (value) {
                    ref.read(appSettingsProvider.notifier).setAlertsEnabled(value);
                  },
                ),
                SwitchSettingsTile(
                  title: 'Weather Alerts',
                  titleAr: 'تنبيهات الطقس',
                  icon: Icons.cloud_rounded,
                  iconColor: SahoolTheme.info,
                  value: settings.weatherAlertsEnabled,
                  subtitle: 'تحذيرات الصقيع والأمطار والحرارة',
                  enabled: settings.notificationsEnabled,
                  onChanged: (value) {
                    ref.read(appSettingsProvider.notifier).setWeatherAlertsEnabled(value);
                  },
                ),
                SwitchSettingsTile(
                  title: 'Task Reminders',
                  titleAr: 'تذكيرات المهام',
                  icon: Icons.task_alt_rounded,
                  iconColor: SahoolTheme.success,
                  value: settings.taskRemindersEnabled,
                  subtitle: 'تذكير بالمهام والمواعيد',
                  enabled: settings.notificationsEnabled,
                  onChanged: (value) {
                    ref.read(appSettingsProvider.notifier).setTaskRemindersEnabled(value);
                  },
                ),
                _NotificationCategoryTile(
                  titleAr: 'تحديثات السوق',
                  icon: Icons.store_rounded,
                  iconColor: Colors.purple,
                  enabled: settings.notificationsEnabled,
                ),
                _NotificationCategoryTile(
                  titleAr: 'نصائح زراعية',
                  icon: Icons.tips_and_updates_rounded,
                  iconColor: Colors.teal,
                  enabled: settings.notificationsEnabled,
                ),
                _NotificationCategoryTile(
                  titleAr: 'رسائل المجتمع',
                  icon: Icons.forum_rounded,
                  iconColor: Colors.orange,
                  enabled: settings.notificationsEnabled,
                ),
              ],
            ),

            // Sound & Vibration
            SettingsSection(
              title: 'Sound & Vibration',
              titleAr: 'الصوت والاهتزاز',
              icon: Icons.volume_up_outlined,
              showDividers: true,
              children: [
                SwitchSettingsTile(
                  title: 'Sound',
                  titleAr: 'الصوت',
                  icon: Icons.volume_up_rounded,
                  value: settings.soundEnabled,
                  enabled: settings.notificationsEnabled,
                  onChanged: (value) {
                    ref.read(appSettingsProvider.notifier).setSoundEnabled(value);
                  },
                ),
                SwitchSettingsTile(
                  title: 'Vibration',
                  titleAr: 'الاهتزاز',
                  icon: Icons.vibration_rounded,
                  value: settings.vibrationEnabled,
                  enabled: settings.notificationsEnabled,
                  onChanged: (value) {
                    ref.read(appSettingsProvider.notifier).setVibrationEnabled(value);
                  },
                ),
                SettingsTile(
                  title: 'Notification Sound',
                  titleAr: 'نغمة الإشعار',
                  icon: Icons.music_note_rounded,
                  subtitle: 'افتراضي',
                  enabled: settings.notificationsEnabled && settings.soundEnabled,
                  onTap: () => _showSoundPicker(context),
                ),
              ],
            ),

            // Quiet Hours
            SettingsSection(
              title: 'Quiet Hours',
              titleAr: 'ساعات الهدوء',
              icon: Icons.do_not_disturb_outlined,
              subtitle: 'إيقاف الإشعارات خلال أوقات محددة',
              children: [
                _QuietHoursTile(
                  start: settings.quietHoursStart,
                  end: settings.quietHoursEnd,
                  enabled: settings.notificationsEnabled,
                  onChanged: (start, end) {
                    ref.read(appSettingsProvider.notifier).setQuietHours(start, end);
                  },
                ),
              ],
            ),

            // Priority
            SettingsSection(
              title: 'Priority',
              titleAr: 'الأولوية',
              icon: Icons.priority_high_outlined,
              children: [
                DescriptiveSwitchTile(
                  titleAr: 'الإشعارات ذات الأولوية العالية فقط',
                  description:
                      'عند تفعيل هذا الخيار، ستتلقى فقط الإشعارات الهامة والطارئة مثل تنبيهات الآفات الحرجة وتحذيرات الطقس الشديد.',
                  icon: Icons.priority_high_rounded,
                  iconColor: SahoolTheme.error,
                  value: false,
                  enabled: settings.notificationsEnabled,
                  onChanged: (value) {
                    // Handle high priority only toggle
                  },
                ),
              ],
            ),

            // Test notification
            const SizedBox(height: 16),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              child: OutlinedButton.icon(
                onPressed: settings.notificationsEnabled
                    ? () => _sendTestNotification(context)
                    : null,
                icon: const Icon(Icons.notifications_active),
                label: const Text('إرسال إشعار تجريبي'),
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _showSoundPicker(BuildContext context) {
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.transparent,
      builder: (context) => DecoratedBox(
        decoration: BoxDecoration(
          color: Theme.of(context).brightness == Brightness.dark
              ? Colors.grey[900]
              : Colors.white,
          borderRadius: const BorderRadius.vertical(top: Radius.circular(20)),
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              margin: const EdgeInsets.only(top: 12),
              width: 40,
              height: 4,
              decoration: BoxDecoration(
                color: Colors.grey[400],
                borderRadius: BorderRadius.circular(2),
              ),
            ),
            const Padding(
              padding: EdgeInsets.all(16),
              child: Text(
                'اختر نغمة الإشعار',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
            ),
            const _SoundOption(name: 'افتراضي', isSelected: true),
            const _SoundOption(name: 'نغمة 1'),
            const _SoundOption(name: 'نغمة 2'),
            const _SoundOption(name: 'نغمة 3'),
            const _SoundOption(name: 'صامت'),
            SizedBox(height: MediaQuery.of(context).padding.bottom + 16),
          ],
        ),
      ),
    );
  }

  void _sendTestNotification(BuildContext context) {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('تم إرسال إشعار تجريبي'),
        backgroundColor: SahoolTheme.success,
      ),
    );
  }
}

/// Notification Category Tile with toggle
class _NotificationCategoryTile extends StatefulWidget {
  final String titleAr;
  final IconData icon;
  final Color iconColor;
  final bool enabled;

  const _NotificationCategoryTile({
    required this.titleAr,
    required this.icon,
    required this.iconColor,
    this.enabled = true,
  });

  @override
  State<_NotificationCategoryTile> createState() => _NotificationCategoryTileState();
}

class _NotificationCategoryTileState extends State<_NotificationCategoryTile> {
  bool _isEnabled = true;

  @override
  Widget build(BuildContext context) {
    return SwitchSettingsTile(
      title: '',
      titleAr: widget.titleAr,
      icon: widget.icon,
      iconColor: widget.iconColor,
      value: _isEnabled,
      enabled: widget.enabled,
      onChanged: (value) => setState(() => _isEnabled = value),
    );
  }
}

/// Quiet Hours Tile
class _QuietHoursTile extends StatefulWidget {
  final TimeOfDay? start;
  final TimeOfDay? end;
  final bool enabled;
  final Function(TimeOfDay?, TimeOfDay?) onChanged;

  const _QuietHoursTile({
    this.start,
    this.end,
    this.enabled = true,
    required this.onChanged,
  });

  @override
  State<_QuietHoursTile> createState() => _QuietHoursTileState();
}

class _QuietHoursTileState extends State<_QuietHoursTile> {
  bool _isEnabled = false;
  TimeOfDay _start = const TimeOfDay(hour: 22, minute: 0);
  TimeOfDay _end = const TimeOfDay(hour: 7, minute: 0);

  @override
  void initState() {
    super.initState();
    _isEnabled = widget.start != null && widget.end != null;
    if (widget.start != null) _start = widget.start!;
    if (widget.end != null) _end = widget.end!;
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Material(
      color: Colors.transparent,
      child: Opacity(
        opacity: widget.enabled ? 1.0 : 0.5,
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Container(
                    width: 40,
                    height: 40,
                    decoration: BoxDecoration(
                      color: SahoolTheme.info.withValues(alpha: isDark ? 0.2 : 0.1),
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: const Icon(
                      Icons.do_not_disturb_on_rounded,
                      color: SahoolTheme.info,
                      size: 22,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'تفعيل ساعات الهدوء',
                          style: TextStyle(
                            fontSize: 15,
                            fontWeight: FontWeight.w500,
                            color: isDark ? Colors.white : Colors.black87,
                          ),
                        ),
                        Text(
                          _isEnabled
                              ? 'من ${_formatTime(_start)} إلى ${_formatTime(_end)}'
                              : 'معطّل',
                          style: TextStyle(
                            fontSize: 13,
                            color: isDark ? Colors.grey[400] : Colors.grey[600],
                          ),
                        ),
                      ],
                    ),
                  ),
                  Switch.adaptive(
                    value: _isEnabled,
                    onChanged: widget.enabled
                        ? (value) {
                            setState(() => _isEnabled = value);
                            widget.onChanged(
                              value ? _start : null,
                              value ? _end : null,
                            );
                          }
                        : null,
                    activeColor: SahoolTheme.primary,
                  ),
                ],
              ),
              if (_isEnabled) ...[
                const SizedBox(height: 16),
                Row(
                  children: [
                    Expanded(
                      child: _TimePickerButton(
                        label: 'من',
                        time: _start,
                        onChanged: (time) {
                          setState(() => _start = time);
                          widget.onChanged(_start, _end);
                        },
                      ),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: _TimePickerButton(
                        label: 'إلى',
                        time: _end,
                        onChanged: (time) {
                          setState(() => _end = time);
                          widget.onChanged(_start, _end);
                        },
                      ),
                    ),
                  ],
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  String _formatTime(TimeOfDay time) {
    final hour = time.hourOfPeriod == 0 ? 12 : time.hourOfPeriod;
    final minute = time.minute.toString().padLeft(2, '0');
    final period = time.period == DayPeriod.am ? 'ص' : 'م';
    return '$hour:$minute $period';
  }
}

/// Time Picker Button
class _TimePickerButton extends StatelessWidget {
  final String label;
  final TimeOfDay time;
  final ValueChanged<TimeOfDay> onChanged;

  const _TimePickerButton({
    required this.label,
    required this.time,
    required this.onChanged,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: () async {
        final selected = await showTimePicker(
          context: context,
          initialTime: time,
        );
        if (selected != null) {
          onChanged(selected);
        }
      },
      borderRadius: BorderRadius.circular(12),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        decoration: BoxDecoration(
          border: Border.all(color: Colors.grey.withValues(alpha: 0.3)),
          borderRadius: BorderRadius.circular(12),
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              label,
              style: TextStyle(color: Colors.grey[600], fontSize: 14),
            ),
            Text(
              _formatTime(time),
              style: const TextStyle(
                fontWeight: FontWeight.bold,
                fontSize: 16,
              ),
            ),
          ],
        ),
      ),
    );
  }

  String _formatTime(TimeOfDay time) {
    final hour = time.hourOfPeriod == 0 ? 12 : time.hourOfPeriod;
    final minute = time.minute.toString().padLeft(2, '0');
    final period = time.period == DayPeriod.am ? 'ص' : 'م';
    return '$hour:$minute $period';
  }
}

/// Sound Option
class _SoundOption extends StatelessWidget {
  final String name;
  final bool isSelected;

  const _SoundOption({
    required this.name,
    this.isSelected = false,
  });

  @override
  Widget build(BuildContext context) {
    return ListTile(
      leading: Icon(
        isSelected ? Icons.radio_button_checked : Icons.radio_button_off,
        color: isSelected ? SahoolTheme.primary : Colors.grey,
      ),
      title: Text(name),
      trailing: IconButton(
        icon: const Icon(Icons.play_arrow),
        onPressed: () {
          // Play sound preview
        },
      ),
      onTap: () => Navigator.pop(context),
    );
  }
}
