/// Pivot Control Panel - Valley Style
/// لوحة تحكم المحوري - بأسلوب فالي
library;

import 'package:flutter/material.dart';
import '../../domain/models/pivot_models.dart';

/// Valley-style pivot control panel
/// لوحة تحكم المحوري بأسلوب فالي
class PivotControlPanel extends StatefulWidget {
  final PivotConfiguration config;
  final PivotStatus status;
  final Function(PivotControlCommand) onCommand;
  final bool isConnected;

  const PivotControlPanel({
    super.key,
    required this.config,
    required this.status,
    required this.onCommand,
    this.isConnected = true,
  });

  @override
  State<PivotControlPanel> createState() => _PivotControlPanelState();
}

class _PivotControlPanelState extends State<PivotControlPanel> {
  double _speedSliderValue = 100;
  double _timerValue = 0;
  bool _endGunEnabled = false;

  @override
  void initState() {
    super.initState();
    _speedSliderValue = widget.status.speedPercent;
    _endGunEnabled = widget.status.endGunActive;
  }

  @override
  void didUpdateWidget(PivotControlPanel oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.status.speedPercent != widget.status.speedPercent) {
      _speedSliderValue = widget.status.speedPercent;
    }
    if (oldWidget.status.endGunActive != widget.status.endGunActive) {
      _endGunEnabled = widget.status.endGunActive;
    }
  }

  @override
  Widget build(BuildContext context) {
    final isRunning = widget.status.operatingStatus == PivotOperatingStatus.running;
    final isPaused = widget.status.operatingStatus == PivotOperatingStatus.paused;
    final hasFault = widget.status.operatingStatus == PivotOperatingStatus.fault;

    return Card(
      margin: const EdgeInsets.all(8),
      elevation: 4,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header with status
            _buildHeader(isRunning, isPaused, hasFault),

            const Divider(height: 24),

            // Main control buttons
            _buildMainControls(isRunning, isPaused),

            const SizedBox(height: 16),

            // Speed control
            _buildSpeedControl(),

            const SizedBox(height: 16),

            // Direction control
            _buildDirectionControl(),

            const SizedBox(height: 16),

            // Timer control
            _buildTimerControl(),

            const SizedBox(height: 16),

            // End gun toggle
            if (widget.config.hasEndGun) _buildEndGunControl(),

            const SizedBox(height: 16),

            // Status info
            _buildStatusInfo(),

            // Alerts
            if (widget.status.activeAlerts.isNotEmpty) ...[
              const Divider(height: 24),
              _buildAlerts(),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildHeader(bool isRunning, bool isPaused, bool hasFault) {
    return Row(
      children: [
        // Status indicator
        Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: _statusColor(widget.status.operatingStatus).withOpacity(0.1),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Icon(
            _statusIcon(widget.status.operatingStatus),
            color: _statusColor(widget.status.operatingStatus),
            size: 28,
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                widget.config.name,
                style: const TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
              Text(
                _statusText(widget.status.operatingStatus),
                style: TextStyle(
                  color: _statusColor(widget.status.operatingStatus),
                  fontWeight: FontWeight.w500,
                ),
              ),
            ],
          ),
        ),
        // Connection indicator
        Icon(
          widget.isConnected ? Icons.wifi : Icons.wifi_off,
          color: widget.isConnected ? Colors.green : Colors.red,
        ),
      ],
    );
  }

  Widget _buildMainControls(bool isRunning, bool isPaused) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
      children: [
        // Start/Resume button
        _ControlButton(
          icon: Icons.play_arrow,
          label: isRunning ? 'يعمل' : (isPaused ? 'استمرار' : 'تشغيل'),
          labelEn: isRunning ? 'Running' : (isPaused ? 'Resume' : 'Start'),
          color: Colors.green,
          isActive: isRunning,
          onPressed: isRunning
              ? null
              : () => _sendCommand(
                    isPaused ? PivotCommandType.resume : PivotCommandType.start,
                  ),
        ),

        // Pause button
        _ControlButton(
          icon: Icons.pause,
          label: 'إيقاف مؤقت',
          labelEn: 'Pause',
          color: Colors.orange,
          isActive: isPaused,
          onPressed: !isRunning
              ? null
              : () => _sendCommand(PivotCommandType.pause),
        ),

        // Stop button
        _ControlButton(
          icon: Icons.stop,
          label: 'إيقاف',
          labelEn: 'Stop',
          color: Colors.red,
          onPressed: (!isRunning && !isPaused)
              ? null
              : () => _sendCommand(PivotCommandType.stop),
        ),

        // Emergency stop
        _ControlButton(
          icon: Icons.emergency,
          label: 'طوارئ',
          labelEn: 'Emergency',
          color: Colors.red[900]!,
          onPressed: () => _showEmergencyStopDialog(),
        ),
      ],
    );
  }

  Widget _buildSpeedControl() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            const Row(
              children: [
                Icon(Icons.speed, size: 20),
                SizedBox(width: 8),
                Text(
                  'السرعة | Speed',
                  style: TextStyle(fontWeight: FontWeight.bold),
                ),
              ],
            ),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
              decoration: BoxDecoration(
                color: Colors.blue.withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Text(
                '${_speedSliderValue.toInt()}%',
                style: const TextStyle(
                  fontWeight: FontWeight.bold,
                  color: Colors.blue,
                ),
              ),
            ),
          ],
        ),
        const SizedBox(height: 8),
        SliderTheme(
          data: SliderTheme.of(context).copyWith(
            activeTrackColor: Colors.blue,
            inactiveTrackColor: Colors.blue.withOpacity(0.2),
            thumbColor: Colors.blue,
            overlayColor: Colors.blue.withOpacity(0.1),
            trackHeight: 8,
          ),
          child: Slider(
            value: _speedSliderValue,
            min: 0,
            max: 100,
            divisions: 20,
            onChanged: (value) {
              setState(() => _speedSliderValue = value);
            },
            onChangeEnd: (value) {
              _sendCommand(PivotCommandType.setSpeed, speedPercent: value);
            },
          ),
        ),
        // Speed presets
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceEvenly,
          children: [25, 50, 75, 100].map((speed) {
            final isSelected = _speedSliderValue == speed;
            return ChoiceChip(
              label: Text('$speed%'),
              selected: isSelected,
              onSelected: (selected) {
                if (selected) {
                  setState(() => _speedSliderValue = speed.toDouble());
                  _sendCommand(PivotCommandType.setSpeed,
                      speedPercent: speed.toDouble());
                }
              },
              selectedColor: Colors.blue,
              labelStyle: TextStyle(
                color: isSelected ? Colors.white : Colors.black87,
              ),
            );
          }).toList(),
        ),
      ],
    );
  }

  Widget _buildDirectionControl() {
    final currentDirection = widget.status.direction;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Row(
          children: [
            Icon(Icons.rotate_right, size: 20),
            SizedBox(width: 8),
            Text(
              'الاتجاه | Direction',
              style: TextStyle(fontWeight: FontWeight.bold),
            ),
          ],
        ),
        const SizedBox(height: 8),
        Row(
          children: [
            Expanded(
              child: _DirectionButton(
                icon: Icons.rotate_left,
                label: 'عكس عقارب الساعة',
                labelEn: 'Counter-clockwise',
                isSelected: currentDirection == PivotDirection.reverse,
                onPressed: () => _sendCommand(
                  PivotCommandType.setDirection,
                  direction: PivotDirection.reverse,
                ),
              ),
            ),
            const SizedBox(width: 8),
            Expanded(
              child: _DirectionButton(
                icon: Icons.rotate_right,
                label: 'مع عقارب الساعة',
                labelEn: 'Clockwise',
                isSelected: currentDirection == PivotDirection.forward,
                onPressed: () => _sendCommand(
                  PivotCommandType.setDirection,
                  direction: PivotDirection.forward,
                ),
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildTimerControl() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Row(
          children: [
            Icon(Icons.timer, size: 20),
            SizedBox(width: 8),
            Text(
              'المؤقت | Timer',
              style: TextStyle(fontWeight: FontWeight.bold),
            ),
          ],
        ),
        const SizedBox(height: 8),
        Row(
          children: [
            Expanded(
              child: TextField(
                keyboardType: TextInputType.number,
                decoration: InputDecoration(
                  hintText: 'ساعات | Hours',
                  suffixText: 'ساعة',
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                  contentPadding: const EdgeInsets.symmetric(
                    horizontal: 16,
                    vertical: 12,
                  ),
                ),
                onChanged: (value) {
                  _timerValue = double.tryParse(value) ?? 0;
                },
              ),
            ),
            const SizedBox(width: 8),
            ElevatedButton.icon(
              onPressed: _timerValue > 0
                  ? () => _sendCommand(PivotCommandType.setTimer,
                      timerHours: _timerValue)
                  : null,
              icon: const Icon(Icons.timer),
              label: const Text('تعيين'),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.blue,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
              ),
            ),
          ],
        ),
        // Quick timer presets
        const SizedBox(height: 8),
        Wrap(
          spacing: 8,
          children: [2, 4, 6, 12, 24].map((hours) {
            return ActionChip(
              label: Text('$hours س'),
              onPressed: () {
                _sendCommand(PivotCommandType.setTimer,
                    timerHours: hours.toDouble());
              },
            );
          }).toList(),
        ),
      ],
    );
  }

  Widget _buildEndGunControl() {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: _endGunEnabled
            ? Colors.blue.withOpacity(0.1)
            : Colors.grey.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        children: [
          Icon(
            Icons.water,
            color: _endGunEnabled ? Colors.blue : Colors.grey,
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'المدفع الطرفي | End Gun',
                  style: TextStyle(fontWeight: FontWeight.bold),
                ),
                Text(
                  _endGunEnabled ? 'مفعل | Active' : 'معطل | Inactive',
                  style: TextStyle(
                    color: _endGunEnabled ? Colors.blue : Colors.grey,
                    fontSize: 12,
                  ),
                ),
              ],
            ),
          ),
          Switch(
            value: _endGunEnabled,
            onChanged: (value) {
              setState(() => _endGunEnabled = value);
              _sendCommand(PivotCommandType.toggleEndGun, endGunEnabled: value);
            },
            activeColor: Colors.blue,
          ),
        ],
      ),
    );
  }

  Widget _buildStatusInfo() {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.grey.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        children: [
          _StatusRow(
            icon: Icons.location_on,
            label: 'الموقع | Position',
            value: '${widget.status.currentAngle.toStringAsFixed(1)}°',
          ),
          const Divider(height: 16),
          _StatusRow(
            icon: Icons.water_drop,
            label: 'التدفق | Flow',
            value: '${widget.status.currentFlowRateLph.toStringAsFixed(0)} L/h',
          ),
          const Divider(height: 16),
          _StatusRow(
            icon: Icons.compress,
            label: 'الضغط | Pressure',
            value: '${widget.status.currentPressureBar.toStringAsFixed(1)} bar',
          ),
          const Divider(height: 16),
          _StatusRow(
            icon: Icons.opacity,
            label: 'المياه المطبقة | Water Applied',
            value: '${widget.status.waterAppliedM3.toStringAsFixed(1)} م³',
          ),
          if (widget.status.estimatedCompletionTime != null) ...[
            const Divider(height: 16),
            _StatusRow(
              icon: Icons.schedule,
              label: 'وقت الإنتهاء | Completion',
              value: _formatTime(widget.status.estimatedCompletionTime!),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildAlerts() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Icon(Icons.warning_amber, color: Colors.orange[700], size: 20),
            const SizedBox(width: 8),
            Text(
              'التنبيهات | Alerts (${widget.status.activeAlerts.length})',
              style: const TextStyle(fontWeight: FontWeight.bold),
            ),
          ],
        ),
        const SizedBox(height: 8),
        ...widget.status.activeAlerts.take(3).map((alert) => _AlertTile(alert: alert)),
      ],
    );
  }

  void _sendCommand(
    PivotCommandType type, {
    double? speedPercent,
    double? targetAngle,
    PivotDirection? direction,
    bool? endGunEnabled,
    double? timerHours,
  }) {
    widget.onCommand(PivotControlCommand(
      pivotId: widget.config.id,
      commandType: type,
      speedPercent: speedPercent,
      targetAngle: targetAngle,
      direction: direction,
      endGunEnabled: endGunEnabled,
      timerHours: timerHours,
      issuedBy: 'current_user', // Replace with actual user ID
      timestamp: DateTime.now(),
    ));
  }

  void _showEmergencyStopDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Row(
          children: [
            Icon(Icons.emergency, color: Colors.red[900]),
            const SizedBox(width: 8),
            const Text('إيقاف طوارئ | Emergency Stop'),
          ],
        ),
        content: const Text(
          'هل أنت متأكد من إيقاف المحوري فوراً؟\n'
          'Are you sure you want to emergency stop?',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('إلغاء | Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              _sendCommand(PivotCommandType.emergencyStop);
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.red[900],
              foregroundColor: Colors.white,
            ),
            child: const Text('إيقاف طوارئ'),
          ),
        ],
      ),
    );
  }

  String _statusText(PivotOperatingStatus status) {
    switch (status) {
      case PivotOperatingStatus.running:
        return 'يعمل | Running';
      case PivotOperatingStatus.paused:
        return 'متوقف مؤقتاً | Paused';
      case PivotOperatingStatus.stopped:
        return 'متوقف | Stopped';
      case PivotOperatingStatus.fault:
        return 'عطل | Fault';
      case PivotOperatingStatus.maintenance:
        return 'صيانة | Maintenance';
      case PivotOperatingStatus.scheduled:
        return 'مجدول | Scheduled';
    }
  }

  IconData _statusIcon(PivotOperatingStatus status) {
    switch (status) {
      case PivotOperatingStatus.running:
        return Icons.play_circle;
      case PivotOperatingStatus.paused:
        return Icons.pause_circle;
      case PivotOperatingStatus.stopped:
        return Icons.stop_circle;
      case PivotOperatingStatus.fault:
        return Icons.error;
      case PivotOperatingStatus.maintenance:
        return Icons.build_circle;
      case PivotOperatingStatus.scheduled:
        return Icons.schedule;
    }
  }

  Color _statusColor(PivotOperatingStatus status) {
    switch (status) {
      case PivotOperatingStatus.running:
        return Colors.green;
      case PivotOperatingStatus.paused:
        return Colors.orange;
      case PivotOperatingStatus.stopped:
        return Colors.grey;
      case PivotOperatingStatus.fault:
        return Colors.red;
      case PivotOperatingStatus.maintenance:
        return Colors.blue;
      case PivotOperatingStatus.scheduled:
        return Colors.purple;
    }
  }

  String _formatTime(DateTime time) {
    return '${time.hour.toString().padLeft(2, '0')}:${time.minute.toString().padLeft(2, '0')}';
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Helper Widgets
// ═══════════════════════════════════════════════════════════════════════════

class _ControlButton extends StatelessWidget {
  final IconData icon;
  final String label;
  final String labelEn;
  final Color color;
  final bool isActive;
  final VoidCallback? onPressed;

  const _ControlButton({
    required this.icon,
    required this.label,
    required this.labelEn,
    required this.color,
    this.isActive = false,
    this.onPressed,
  });

  @override
  Widget build(BuildContext context) {
    final isEnabled = onPressed != null;

    return GestureDetector(
      onTap: onPressed,
      child: Opacity(
        opacity: isEnabled ? 1.0 : 0.4,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: isActive ? color : color.withOpacity(0.1),
                shape: BoxShape.circle,
                border: Border.all(
                  color: color.withOpacity(0.5),
                  width: 2,
                ),
              ),
              child: Icon(
                icon,
                color: isActive ? Colors.white : color,
                size: 28,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              label,
              style: TextStyle(
                fontSize: 10,
                color: isEnabled ? color : Colors.grey,
                fontWeight: FontWeight.w500,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _DirectionButton extends StatelessWidget {
  final IconData icon;
  final String label;
  final String labelEn;
  final bool isSelected;
  final VoidCallback onPressed;

  const _DirectionButton({
    required this.icon,
    required this.label,
    required this.labelEn,
    required this.isSelected,
    required this.onPressed,
  });

  @override
  Widget build(BuildContext context) {
    return Material(
      color: isSelected ? Colors.blue.withOpacity(0.1) : Colors.grey.withOpacity(0.05),
      borderRadius: BorderRadius.circular(12),
      child: InkWell(
        onTap: onPressed,
        borderRadius: BorderRadius.circular(12),
        child: Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            border: Border.all(
              color: isSelected ? Colors.blue : Colors.grey.withOpacity(0.3),
              width: isSelected ? 2 : 1,
            ),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Column(
            children: [
              Icon(
                icon,
                color: isSelected ? Colors.blue : Colors.grey,
                size: 32,
              ),
              const SizedBox(height: 4),
              Text(
                label,
                style: TextStyle(
                  fontSize: 10,
                  color: isSelected ? Colors.blue : Colors.grey,
                  fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                ),
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _StatusRow extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;

  const _StatusRow({
    required this.icon,
    required this.label,
    required this.value,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Icon(icon, size: 18, color: Colors.grey[600]),
        const SizedBox(width: 8),
        Expanded(
          child: Text(
            label,
            style: TextStyle(color: Colors.grey[600], fontSize: 13),
          ),
        ),
        Text(
          value,
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
      ],
    );
  }
}

class _AlertTile extends StatelessWidget {
  final PivotAlert alert;

  const _AlertTile({required this.alert});

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(8),
      decoration: BoxDecoration(
        color: _severityColor(alert.severity).withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: _severityColor(alert.severity).withOpacity(0.3),
        ),
      ),
      child: Row(
        children: [
          Icon(
            _severityIcon(alert.severity),
            color: _severityColor(alert.severity),
            size: 18,
          ),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              alert.messageAr,
              style: TextStyle(
                fontSize: 12,
                color: _severityColor(alert.severity),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Color _severityColor(AlertSeverity severity) {
    switch (severity) {
      case AlertSeverity.info:
        return Colors.blue;
      case AlertSeverity.warning:
        return Colors.orange;
      case AlertSeverity.critical:
        return Colors.red;
      case AlertSeverity.emergency:
        return Colors.red[900]!;
    }
  }

  IconData _severityIcon(AlertSeverity severity) {
    switch (severity) {
      case AlertSeverity.info:
        return Icons.info;
      case AlertSeverity.warning:
        return Icons.warning;
      case AlertSeverity.critical:
        return Icons.error;
      case AlertSeverity.emergency:
        return Icons.emergency;
    }
  }
}
