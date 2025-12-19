/// SAHOOL IoT Control Screen
/// شاشة التحكم عن بعد - إنترنت الأشياء
///
/// Features:
/// - Real-time sensor readings display
/// - Pump and valve control
/// - Irrigation scheduling
/// - Device status monitoring

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/theme/sahool_theme.dart';

// =============================================================================
// State Management
// =============================================================================

/// حالة بيانات إنترنت الأشياء
class IotState {
  final bool isPumpOn;
  final bool isValveOpen;
  final Map<String, SensorReading> sensors;
  final bool isLoading;
  final String? error;

  const IotState({
    this.isPumpOn = false,
    this.isValveOpen = false,
    this.sensors = const {},
    this.isLoading = false,
    this.error,
  });

  IotState copyWith({
    bool? isPumpOn,
    bool? isValveOpen,
    Map<String, SensorReading>? sensors,
    bool? isLoading,
    String? error,
  }) {
    return IotState(
      isPumpOn: isPumpOn ?? this.isPumpOn,
      isValveOpen: isValveOpen ?? this.isValveOpen,
      sensors: sensors ?? this.sensors,
      isLoading: isLoading ?? this.isLoading,
      error: error,
    );
  }
}

/// قراءة الحساس
class SensorReading {
  final String type;
  final double value;
  final String unit;
  final String quality;
  final DateTime timestamp;

  const SensorReading({
    required this.type,
    required this.value,
    required this.unit,
    required this.quality,
    required this.timestamp,
  });
}

/// مزود حالة IoT
class IotNotifier extends StateNotifier<IotState> {
  IotNotifier() : super(const IotState()) {
    _loadDemoData();
  }

  void _loadDemoData() {
    // بيانات تجريبية محاكاة للحساسات
    state = state.copyWith(
      sensors: {
        'soil_moisture': SensorReading(
          type: 'soil_moisture',
          value: 65.0,
          unit: '%',
          quality: 'good',
          timestamp: DateTime.now(),
        ),
        'soil_temperature': SensorReading(
          type: 'soil_temperature',
          value: 28.5,
          unit: '°C',
          quality: 'good',
          timestamp: DateTime.now(),
        ),
        'air_temperature': SensorReading(
          type: 'air_temperature',
          value: 32.0,
          unit: '°C',
          quality: 'warning',
          timestamp: DateTime.now(),
        ),
        'air_humidity': SensorReading(
          type: 'air_humidity',
          value: 45.0,
          unit: '%',
          quality: 'good',
          timestamp: DateTime.now(),
        ),
        'water_level': SensorReading(
          type: 'water_level',
          value: 75.0,
          unit: 'cm',
          quality: 'good',
          timestamp: DateTime.now(),
        ),
        'light_intensity': SensorReading(
          type: 'light_intensity',
          value: 45000,
          unit: 'lux',
          quality: 'good',
          timestamp: DateTime.now(),
        ),
      },
    );
  }

  Future<void> togglePump(bool value) async {
    state = state.copyWith(isLoading: true);

    // محاكاة طلب API
    await Future.delayed(const Duration(milliseconds: 500));

    state = state.copyWith(
      isPumpOn: value,
      isLoading: false,
    );
  }

  Future<void> toggleValve(bool value) async {
    state = state.copyWith(isLoading: true);

    await Future.delayed(const Duration(milliseconds: 500));

    state = state.copyWith(
      isValveOpen: value,
      isLoading: false,
    );
  }

  void refreshSensors() {
    // محاكاة تحديث البيانات
    _loadDemoData();
  }
}

final iotProvider = StateNotifierProvider<IotNotifier, IotState>((ref) {
  return IotNotifier();
});

// =============================================================================
// IoT Control Screen
// =============================================================================

class IoTControlScreen extends ConsumerWidget {
  const IoTControlScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final iotState = ref.watch(iotProvider);

    return Directionality(
      textDirection: TextDirection.rtl,
      child: Scaffold(
        backgroundColor: SahoolColors.warmCream,
        appBar: AppBar(
          title: const Text('التحكم عن بعد'),
          backgroundColor: Colors.white,
          foregroundColor: SahoolColors.forestGreen,
          elevation: 0,
          actions: [
            IconButton(
              icon: const Icon(Icons.refresh),
              onPressed: () => ref.read(iotProvider.notifier).refreshSensors(),
            ),
          ],
        ),
        body: RefreshIndicator(
          onRefresh: () async {
            ref.read(iotProvider.notifier).refreshSensors();
          },
          child: ListView(
            padding: const EdgeInsets.all(16),
            children: [
              // Status Banner
              _StatusBanner(
                devicesOnline: 5,
                devicesTotal: 6,
              ),

              const SizedBox(height: 20),

              // Sensor Grid
              const Text(
                'قراءات الحساسات',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 12),

              GridView.count(
                crossAxisCount: 2,
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                mainAxisSpacing: 12,
                crossAxisSpacing: 12,
                childAspectRatio: 1.3,
                children: [
                  _SensorCard(
                    icon: Icons.water_drop,
                    label: 'رطوبة التربة',
                    value: '${iotState.sensors['soil_moisture']?.value ?? 0}',
                    unit: '%',
                    color: Colors.blue,
                    isWarning: (iotState.sensors['soil_moisture']?.value ?? 0) < 40,
                  ),
                  _SensorCard(
                    icon: Icons.thermostat,
                    label: 'درجة حرارة التربة',
                    value: '${iotState.sensors['soil_temperature']?.value ?? 0}',
                    unit: '°C',
                    color: Colors.brown,
                  ),
                  _SensorCard(
                    icon: Icons.device_thermostat,
                    label: 'درجة حرارة الهواء',
                    value: '${iotState.sensors['air_temperature']?.value ?? 0}',
                    unit: '°C',
                    color: Colors.orange,
                    isWarning: (iotState.sensors['air_temperature']?.value ?? 0) > 35,
                  ),
                  _SensorCard(
                    icon: Icons.cloud,
                    label: 'رطوبة الهواء',
                    value: '${iotState.sensors['air_humidity']?.value ?? 0}',
                    unit: '%',
                    color: Colors.cyan,
                  ),
                  _SensorCard(
                    icon: Icons.waves,
                    label: 'منسوب المياه',
                    value: '${iotState.sensors['water_level']?.value ?? 0}',
                    unit: 'cm',
                    color: Colors.indigo,
                  ),
                  _SensorCard(
                    icon: Icons.wb_sunny,
                    label: 'شدة الإضاءة',
                    value: '${((iotState.sensors['light_intensity']?.value ?? 0) / 1000).toStringAsFixed(0)}K',
                    unit: 'lux',
                    color: Colors.amber,
                  ),
                ],
              ),

              const SizedBox(height: 24),

              // Actuator Controls
              const Text(
                'التحكم بالمعدات',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 12),

              // Pump Control
              _ActuatorCard(
                icon: Icons.water,
                label: 'المضخة الرئيسية',
                subtitle: iotState.isPumpOn ? 'تعمل الآن...' : 'متوقفة',
                isOn: iotState.isPumpOn,
                isLoading: iotState.isLoading,
                onColor: Colors.blue,
                onToggle: (value) {
                  ref.read(iotProvider.notifier).togglePump(value);
                  _showFeedback(context, value, 'المضخة');
                },
              ),

              const SizedBox(height: 12),

              // Valve Control
              _ActuatorCard(
                icon: Icons.settings_input_component,
                label: 'الصمام الرئيسي',
                subtitle: iotState.isValveOpen ? 'مفتوح' : 'مغلق',
                isOn: iotState.isValveOpen,
                isLoading: iotState.isLoading,
                onColor: Colors.teal,
                onToggle: (value) {
                  ref.read(iotProvider.notifier).toggleValve(value);
                  _showFeedback(context, value, 'الصمام');
                },
              ),

              const SizedBox(height: 24),

              // Quick Actions
              const Text(
                'إجراءات سريعة',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 12),

              Row(
                children: [
                  Expanded(
                    child: _QuickActionButton(
                      icon: Icons.timer,
                      label: 'ري لمدة 30 دقيقة',
                      color: Colors.blue,
                      onTap: () => _showScheduleDialog(context, ref),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: _QuickActionButton(
                      icon: Icons.calendar_today,
                      label: 'جدولة الري',
                      color: Colors.green,
                      onTap: () => _showScheduleDialog(context, ref),
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 12),

              Row(
                children: [
                  Expanded(
                    child: _QuickActionButton(
                      icon: Icons.stop_circle,
                      label: 'إيقاف طارئ',
                      color: Colors.red,
                      onTap: () {
                        ref.read(iotProvider.notifier).togglePump(false);
                        ref.read(iotProvider.notifier).toggleValve(false);
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(
                            content: Text('تم إيقاف جميع المعدات'),
                            backgroundColor: Colors.red,
                          ),
                        );
                      },
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: _QuickActionButton(
                      icon: Icons.auto_mode,
                      label: 'الوضع التلقائي',
                      color: Colors.purple,
                      onTap: () => _showAutoModeDialog(context),
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 100),
            ],
          ),
        ),
      ),
    );
  }

  void _showFeedback(BuildContext context, bool isOn, String device) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Row(
          children: [
            Icon(
              isOn ? Icons.check_circle : Icons.cancel,
              color: Colors.white,
            ),
            const SizedBox(width: 8),
            Text(isOn ? 'تم تشغيل $device' : 'تم إيقاف $device'),
          ],
        ),
        backgroundColor: isOn ? Colors.green : Colors.grey,
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      ),
    );
  }

  void _showScheduleDialog(BuildContext context, WidgetRef ref) {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) => Directionality(
        textDirection: TextDirection.rtl,
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'جدولة الري',
                style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 16),
              ListTile(
                leading: const Icon(Icons.timer, color: Colors.blue),
                title: const Text('ري لمدة 15 دقيقة'),
                onTap: () {
                  Navigator.pop(context);
                  ref.read(iotProvider.notifier).togglePump(true);
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('بدأ الري لمدة 15 دقيقة')),
                  );
                },
              ),
              ListTile(
                leading: const Icon(Icons.timer, color: Colors.blue),
                title: const Text('ري لمدة 30 دقيقة'),
                onTap: () {
                  Navigator.pop(context);
                  ref.read(iotProvider.notifier).togglePump(true);
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('بدأ الري لمدة 30 دقيقة')),
                  );
                },
              ),
              ListTile(
                leading: const Icon(Icons.timer, color: Colors.blue),
                title: const Text('ري لمدة ساعة'),
                onTap: () {
                  Navigator.pop(context);
                  ref.read(iotProvider.notifier).togglePump(true);
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('بدأ الري لمدة ساعة')),
                  );
                },
              ),
              const SizedBox(height: 16),
            ],
          ),
        ),
      ),
    );
  }

  void _showAutoModeDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => Directionality(
        textDirection: TextDirection.rtl,
        child: AlertDialog(
          title: const Text('الوضع التلقائي'),
          content: const Text(
            'في الوضع التلقائي، سيتم التحكم بالري تلقائياً بناءً على:\n\n'
            '• رطوبة التربة (أقل من 40%)\n'
            '• درجة حرارة الهواء\n'
            '• توقعات الطقس\n\n'
            'هل تريد تفعيل الوضع التلقائي؟',
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('إلغاء'),
            ),
            ElevatedButton(
              onPressed: () {
                Navigator.pop(context);
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                    content: Text('تم تفعيل الوضع التلقائي'),
                    backgroundColor: Colors.green,
                  ),
                );
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: SahoolColors.forestGreen,
              ),
              child: const Text('تفعيل', style: TextStyle(color: Colors.white)),
            ),
          ],
        ),
      ),
    );
  }
}

// =============================================================================
// Widget Components
// =============================================================================

class _StatusBanner extends StatelessWidget {
  final int devicesOnline;
  final int devicesTotal;

  const _StatusBanner({
    required this.devicesOnline,
    required this.devicesTotal,
  });

  @override
  Widget build(BuildContext context) {
    final allOnline = devicesOnline == devicesTotal;

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: allOnline
              ? [SahoolColors.forestGreen, SahoolColors.sageGreen]
              : [Colors.orange.shade600, Colors.orange.shade400],
        ),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.2),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Icon(
              allOnline ? Icons.wifi : Icons.wifi_off,
              color: Colors.white,
              size: 28,
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  allOnline ? 'جميع الأجهزة متصلة' : 'بعض الأجهزة غير متصلة',
                  style: const TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                    fontSize: 16,
                  ),
                ),
                Text(
                  '$devicesOnline من $devicesTotal جهاز',
                  style: TextStyle(
                    color: Colors.white.withOpacity(0.8),
                    fontSize: 13,
                  ),
                ),
              ],
            ),
          ),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.2),
              borderRadius: BorderRadius.circular(20),
            ),
            child: Row(
              children: [
                Container(
                  width: 8,
                  height: 8,
                  decoration: BoxDecoration(
                    color: allOnline ? Colors.greenAccent : Colors.yellow,
                    shape: BoxShape.circle,
                  ),
                ),
                const SizedBox(width: 6),
                Text(
                  allOnline ? 'مباشر' : 'تحذير',
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 12,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _SensorCard extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;
  final String unit;
  final Color color;
  final bool isWarning;

  const _SensorCard({
    required this.icon,
    required this.label,
    required this.value,
    required this.unit,
    required this.color,
    this.isWarning = false,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: isWarning
            ? Border.all(color: Colors.orange, width: 2)
            : null,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Icon(icon, color: color, size: 24),
              if (isWarning)
                const Icon(Icons.warning_amber, color: Colors.orange, size: 20),
            ],
          ),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  Text(
                    value,
                    style: TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                      color: isWarning ? Colors.orange : color,
                    ),
                  ),
                  const SizedBox(width: 4),
                  Text(
                    unit,
                    style: TextStyle(
                      fontSize: 14,
                      color: Colors.grey[600],
                    ),
                  ),
                ],
              ),
              Text(
                label,
                style: TextStyle(
                  fontSize: 12,
                  color: Colors.grey[600],
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _ActuatorCard extends StatelessWidget {
  final IconData icon;
  final String label;
  final String subtitle;
  final bool isOn;
  final bool isLoading;
  final Color onColor;
  final ValueChanged<bool> onToggle;

  const _ActuatorCard({
    required this.icon,
    required this.label,
    required this.subtitle,
    required this.isOn,
    required this.isLoading,
    required this.onColor,
    required this.onToggle,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: isOn ? onColor.withOpacity(0.1) : Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: isOn ? onColor : Colors.grey.shade300,
          width: isOn ? 2 : 1,
        ),
        boxShadow: isOn
            ? [
                BoxShadow(
                  color: onColor.withOpacity(0.2),
                  blurRadius: 10,
                  offset: const Offset(0, 4),
                ),
              ]
            : null,
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: isOn ? onColor.withOpacity(0.2) : Colors.grey.shade100,
              borderRadius: BorderRadius.circular(12),
            ),
            child: Icon(
              icon,
              color: isOn ? onColor : Colors.grey,
              size: 28,
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  label,
                  style: const TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 16,
                  ),
                ),
                Row(
                  children: [
                    if (isOn)
                      Container(
                        width: 8,
                        height: 8,
                        margin: const EdgeInsets.only(left: 6),
                        decoration: BoxDecoration(
                          color: onColor,
                          shape: BoxShape.circle,
                        ),
                      ),
                    Text(
                      subtitle,
                      style: TextStyle(
                        color: isOn ? onColor : Colors.grey,
                        fontSize: 13,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
          if (isLoading)
            const SizedBox(
              width: 48,
              height: 48,
              child: Center(
                child: SizedBox(
                  width: 24,
                  height: 24,
                  child: CircularProgressIndicator(strokeWidth: 2),
                ),
              ),
            )
          else
            Transform.scale(
              scale: 1.3,
              child: Switch(
                value: isOn,
                onChanged: onToggle,
                activeColor: onColor,
              ),
            ),
        ],
      ),
    );
  }
}

class _QuickActionButton extends StatelessWidget {
  final IconData icon;
  final String label;
  final Color color;
  final VoidCallback onTap;

  const _QuickActionButton({
    required this.icon,
    required this.label,
    required this.color,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Material(
      color: color.withOpacity(0.1),
      borderRadius: BorderRadius.circular(12),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(icon, color: color, size: 22),
              const SizedBox(width: 8),
              Flexible(
                child: Text(
                  label,
                  style: TextStyle(
                    color: color,
                    fontWeight: FontWeight.w600,
                    fontSize: 13,
                  ),
                  overflow: TextOverflow.ellipsis,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
