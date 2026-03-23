/// SAHOOL Notification Settings Screen
/// شاشة إعدادات الإشعارات
///
/// Configure notification preferences including:
/// - Per-category toggles
/// - Quiet hours
/// - Sound and vibration
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../domain/models/notification_category.dart';
import '../../domain/models/notification_settings.dart';
import '../../state/notifications_providers.dart';

class NotificationSettingsScreen extends ConsumerStatefulWidget {
  const NotificationSettingsScreen({super.key});

  @override
  ConsumerState<NotificationSettingsScreen> createState() =>
      _NotificationSettingsScreenState();
}

class _NotificationSettingsScreenState
    extends ConsumerState<NotificationSettingsScreen> {
  NotificationSettingsModel? _settings;
  bool _isLoading = true;
  bool _hasChanges = false;

  @override
  void initState() {
    super.initState();
    _loadSettings();
  }

  Future<void> _loadSettings() async {
    final settings =
        await ref.read(notificationsControllerProvider.notifier).getSettings();
    setState(() {
      _settings = settings;
      _isLoading = false;
    });
  }

  void _updateSettings(NotificationSettingsModel newSettings) {
    setState(() {
      _settings = newSettings;
      _hasChanges = true;
    });
  }

  Future<void> _saveSettings() async {
    if (_settings == null) return;

    await ref
        .read(notificationsControllerProvider.notifier)
        .saveSettings(_settings!);

    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('تم حفظ الإعدادات')),
      );
      setState(() {
        _hasChanges = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('إعدادات الإشعارات'),
        actions: [
          if (_hasChanges)
            TextButton(
              onPressed: _saveSettings,
              child: const Text(
                'حفظ',
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
            ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _settings == null
              ? const Center(child: Text('فشل تحميل الإعدادات'))
              : _buildSettingsList(),
    );
  }

  Widget _buildSettingsList() {
    return ListView(
      children: [
        // Global toggle
        _buildSection(
          title: 'الإشعارات',
          children: [
            SwitchListTile(
              title: const Text('تفعيل الإشعارات'),
              subtitle: const Text('السماح بجميع الإشعارات'),
              value: _settings!.enabled,
              onChanged: (value) {
                _updateSettings(_settings!.copyWith(enabled: value));
              },
            ),
          ],
        ),

        // Category settings
        _buildSection(
          title: 'فئات الإشعارات',
          children: NotificationCategory.values.map((category) {
            final categorySettings =
                _settings!.categorySettings[category] ?? const CategorySettings();
            return _buildCategoryTile(category, categorySettings);
          }).toList(),
        ),

        // Quiet hours
        _buildSection(
          title: 'ساعات الهدوء',
          children: [
            SwitchListTile(
              title: const Text('تفعيل ساعات الهدوء'),
              subtitle: Text(
                _settings!.quietHours.enabled
                    ? 'من ${_settings!.quietHours.startTimeFormatted} إلى ${_settings!.quietHours.endTimeFormatted}'
                    : 'إيقاف الإشعارات خلال فترة محددة',
              ),
              value: _settings!.quietHours.enabled,
              onChanged: (value) {
                _updateSettings(
                  _settings!.copyWith(
                    quietHours: _settings!.quietHours.copyWith(enabled: value),
                  ),
                );
              },
            ),
            if (_settings!.quietHours.enabled) ...[
              ListTile(
                title: const Text('وقت البداية'),
                subtitle: Text(_settings!.quietHours.startTimeFormatted),
                trailing: const Icon(Icons.access_time),
                onTap: () => _selectTime(isStart: true),
              ),
              ListTile(
                title: const Text('وقت النهاية'),
                subtitle: Text(_settings!.quietHours.endTimeFormatted),
                trailing: const Icon(Icons.access_time),
                onTap: () => _selectTime(isStart: false),
              ),
              SwitchListTile(
                title: const Text('السماح بالتنبيهات الحرجة'),
                subtitle: const Text('إظهار التنبيهات الهامة خلال ساعات الهدوء'),
                value: _settings!.quietHours.allowCritical,
                onChanged: (value) {
                  _updateSettings(
                    _settings!.copyWith(
                      quietHours:
                          _settings!.quietHours.copyWith(allowCritical: value),
                    ),
                  );
                },
              ),
            ],
          ],
        ),

        // Sound settings
        _buildSection(
          title: 'الصوت والاهتزاز',
          children: [
            SwitchListTile(
              title: const Text('الصوت'),
              subtitle: const Text('تشغيل صوت عند استلام إشعار'),
              secondary: const Icon(Icons.volume_up),
              value: _settings!.soundSettings.enabled,
              onChanged: (value) {
                _updateSettings(
                  _settings!.copyWith(
                    soundSettings:
                        _settings!.soundSettings.copyWith(enabled: value),
                  ),
                );
              },
            ),
            SwitchListTile(
              title: const Text('الاهتزاز'),
              subtitle: const Text('اهتزاز الهاتف عند استلام إشعار'),
              secondary: const Icon(Icons.vibration),
              value: _settings!.soundSettings.vibrationEnabled,
              onChanged: (value) {
                _updateSettings(
                  _settings!.copyWith(
                    soundSettings: _settings!.soundSettings
                        .copyWith(vibrationEnabled: value),
                  ),
                );
              },
            ),
          ],
        ),

        // Badge settings
        _buildSection(
          title: 'شارة التطبيق',
          children: [
            SwitchListTile(
              title: const Text('إظهار الشارة'),
              subtitle: const Text('عرض عدد الإشعارات على أيقونة التطبيق'),
              secondary: const Icon(Icons.brightness_1),
              value: _settings!.badgeSettings.showBadge,
              onChanged: (value) {
                _updateSettings(
                  _settings!.copyWith(
                    badgeSettings:
                        _settings!.badgeSettings.copyWith(showBadge: value),
                  ),
                );
              },
            ),
          ],
        ),

        // Preview settings
        _buildSection(
          title: 'معاينة الإشعارات',
          children: [
            SwitchListTile(
              title: const Text('إظهار المحتوى'),
              subtitle: const Text('عرض نص الإشعار في شريط الإشعارات'),
              value: _settings!.previewSettings.showPreview,
              onChanged: (value) {
                _updateSettings(
                  _settings!.copyWith(
                    previewSettings:
                        _settings!.previewSettings.copyWith(showPreview: value),
                  ),
                );
              },
            ),
            SwitchListTile(
              title: const Text('إظهار الصور'),
              subtitle: const Text('عرض الصور المرفقة في الإشعارات'),
              value: _settings!.previewSettings.showImage,
              onChanged: (value) {
                _updateSettings(
                  _settings!.copyWith(
                    previewSettings:
                        _settings!.previewSettings.copyWith(showImage: value),
                  ),
                );
              },
            ),
          ],
        ),

        const SizedBox(height: 24),

        // Reset button
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16),
          child: OutlinedButton.icon(
            onPressed: _resetToDefaults,
            icon: const Icon(Icons.restore),
            label: const Text('استعادة الإعدادات الافتراضية'),
          ),
        ),

        const SizedBox(height: 24),
      ],
    );
  }

  Widget _buildSection({
    required String title,
    required List<Widget> children,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
          child: Text(
            title,
            style: TextStyle(
              fontWeight: FontWeight.bold,
              color: Theme.of(context).primaryColor,
            ),
          ),
        ),
        ...children,
        const Divider(),
      ],
    );
  }

  Widget _buildCategoryTile(
    NotificationCategory category,
    CategorySettings settings,
  ) {
    return ExpansionTile(
      leading: Icon(category.icon, color: category.color),
      title: Text(category.labelAr),
      subtitle: Text(
        settings.enabled ? 'مفعل' : 'معطل',
        style: TextStyle(
          color: settings.enabled ? Colors.green : Colors.grey,
        ),
      ),
      trailing: Switch(
        value: settings.enabled,
        onChanged: (value) {
          _updateSettings(
            _settings!.updateCategorySettings(
              category,
              settings.copyWith(enabled: value),
            ),
          );
        },
      ),
      children: [
        Padding(
          padding: const EdgeInsets.only(right: 16),
          child: Column(
            children: [
              SwitchListTile(
                title: const Text('الصوت'),
                value: settings.soundEnabled,
                onChanged: settings.enabled
                    ? (value) {
                        _updateSettings(
                          _settings!.updateCategorySettings(
                            category,
                            settings.copyWith(soundEnabled: value),
                          ),
                        );
                      }
                    : null,
              ),
              SwitchListTile(
                title: const Text('الاهتزاز'),
                value: settings.vibrationEnabled,
                onChanged: settings.enabled
                    ? (value) {
                        _updateSettings(
                          _settings!.updateCategorySettings(
                            category,
                            settings.copyWith(vibrationEnabled: value),
                          ),
                        );
                      }
                    : null,
              ),
              SwitchListTile(
                title: const Text('إظهار المعاينة'),
                value: settings.showPreview,
                onChanged: settings.enabled
                    ? (value) {
                        _updateSettings(
                          _settings!.updateCategorySettings(
                            category,
                            settings.copyWith(showPreview: value),
                          ),
                        );
                      }
                    : null,
              ),
            ],
          ),
        ),
      ],
    );
  }

  Future<void> _selectTime({required bool isStart}) async {
    final currentHour =
        isStart ? _settings!.quietHours.startHour : _settings!.quietHours.endHour;
    final currentMinute = isStart
        ? _settings!.quietHours.startMinute
        : _settings!.quietHours.endMinute;

    final time = await showTimePicker(
      context: context,
      initialTime: TimeOfDay(hour: currentHour, minute: currentMinute),
      builder: (context, child) {
        return Directionality(
          textDirection: TextDirection.rtl,
          child: child!,
        );
      },
    );

    if (time != null) {
      _updateSettings(
        _settings!.copyWith(
          quietHours: isStart
              ? _settings!.quietHours.copyWith(
                  startHour: time.hour,
                  startMinute: time.minute,
                )
              : _settings!.quietHours.copyWith(
                  endHour: time.hour,
                  endMinute: time.minute,
                ),
        ),
      );
    }
  }

  void _resetToDefaults() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('استعادة الافتراضي'),
        content: const Text('هل تريد استعادة جميع الإعدادات إلى القيم الافتراضية؟'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('إلغاء'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              _updateSettings(NotificationSettingsModel.defaultSettings());
            },
            child: const Text('استعادة'),
          ),
        ],
      ),
    );
  }
}
