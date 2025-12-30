// ═══════════════════════════════════════════════════════════════════════════
// SAHOOL - Connectivity-Aware Button Widget
// زر واعي بحالة الاتصال
// ═══════════════════════════════════════════════════════════════════════════

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/connectivity/connectivity_provider.dart';

/// Button that automatically disables when offline for online-only actions
/// زر يتم تعطيله تلقائياً عند عدم الاتصال للإجراءات التي تتطلب الاتصال
class ConnectivityAwareButton extends ConsumerWidget {
  /// The button text or label
  final Widget child;

  /// Callback when button is pressed (only called when online)
  final VoidCallback? onPressed;

  /// Whether this action requires internet connectivity
  final bool requiresOnline;

  /// Whether to allow action with poor connection
  final bool allowPoorConnection;

  /// Custom offline tooltip message
  final String? offlineTooltip;

  /// Button style
  final ButtonStyle? style;

  /// Leading icon
  final Widget? icon;

  /// Button type
  final ConnectivityButtonType type;

  /// Show connectivity indicator on button
  final bool showConnectivityIndicator;

  const ConnectivityAwareButton({
    super.key,
    required this.child,
    required this.onPressed,
    this.requiresOnline = true,
    this.allowPoorConnection = true,
    this.offlineTooltip,
    this.style,
    this.icon,
    this.type = ConnectivityButtonType.elevated,
    this.showConnectivityIndicator = false,
  });

  /// Factory constructor for ElevatedButton style
  factory ConnectivityAwareButton.elevated({
    Key? key,
    required Widget child,
    required VoidCallback? onPressed,
    bool requiresOnline = true,
    bool allowPoorConnection = true,
    String? offlineTooltip,
    ButtonStyle? style,
    Widget? icon,
    bool showConnectivityIndicator = false,
  }) {
    return ConnectivityAwareButton(
      key: key,
      onPressed: onPressed,
      requiresOnline: requiresOnline,
      allowPoorConnection: allowPoorConnection,
      offlineTooltip: offlineTooltip,
      style: style,
      icon: icon,
      type: ConnectivityButtonType.elevated,
      showConnectivityIndicator: showConnectivityIndicator,
      child: child,
    );
  }

  /// Factory constructor for TextButton style
  factory ConnectivityAwareButton.text({
    Key? key,
    required Widget child,
    required VoidCallback? onPressed,
    bool requiresOnline = true,
    bool allowPoorConnection = true,
    String? offlineTooltip,
    ButtonStyle? style,
    Widget? icon,
    bool showConnectivityIndicator = false,
  }) {
    return ConnectivityAwareButton(
      key: key,
      onPressed: onPressed,
      requiresOnline: requiresOnline,
      allowPoorConnection: allowPoorConnection,
      offlineTooltip: offlineTooltip,
      style: style,
      icon: icon,
      type: ConnectivityButtonType.text,
      showConnectivityIndicator: showConnectivityIndicator,
      child: child,
    );
  }

  /// Factory constructor for OutlinedButton style
  factory ConnectivityAwareButton.outlined({
    Key? key,
    required Widget child,
    required VoidCallback? onPressed,
    bool requiresOnline = true,
    bool allowPoorConnection = true,
    String? offlineTooltip,
    ButtonStyle? style,
    Widget? icon,
    bool showConnectivityIndicator = false,
  }) {
    return ConnectivityAwareButton(
      key: key,
      onPressed: onPressed,
      requiresOnline: requiresOnline,
      allowPoorConnection: allowPoorConnection,
      offlineTooltip: offlineTooltip,
      style: style,
      icon: icon,
      type: ConnectivityButtonType.outlined,
      showConnectivityIndicator: showConnectivityIndicator,
      child: child,
    );
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final connectivityState = ref.watch(enhancedConnectivityStateProvider);

    // Determine if button should be enabled
    final bool isConnected = connectivityState.isOnline ||
        (allowPoorConnection && connectivityState.isPoorConnection);

    final bool shouldEnable = !requiresOnline || isConnected;
    final VoidCallback? effectiveOnPressed =
        shouldEnable ? onPressed : null;

    // Build button content with optional connectivity indicator
    Widget buttonChild = child;
    if (showConnectivityIndicator && requiresOnline) {
      buttonChild = Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          if (!isConnected)
            Padding(
              padding: const EdgeInsets.only(right: 8),
              child: Icon(
                Icons.cloud_off,
                size: 16,
                color: Theme.of(context).disabledColor,
              ),
            ),
          child,
        ],
      );
    }

    // Wrap in tooltip if offline
    Widget button = _buildButton(
      context,
      effectiveOnPressed,
      buttonChild,
    );

    if (requiresOnline && !isConnected) {
      button = Tooltip(
        message: offlineTooltip ??
            _getDefaultOfflineMessage(connectivityState.isPoorConnection),
        child: button,
      );
    }

    return button;
  }

  /// Build the appropriate button type
  Widget _buildButton(
    BuildContext context,
    VoidCallback? onPressed,
    Widget child,
  ) {
    switch (type) {
      case ConnectivityButtonType.elevated:
        if (icon != null) {
          return ElevatedButton.icon(
            onPressed: onPressed,
            icon: icon!,
            label: child,
            style: style,
          );
        }
        return ElevatedButton(
          onPressed: onPressed,
          style: style,
          child: child,
        );

      case ConnectivityButtonType.text:
        if (icon != null) {
          return TextButton.icon(
            onPressed: onPressed,
            icon: icon!,
            label: child,
            style: style,
          );
        }
        return TextButton(
          onPressed: onPressed,
          style: style,
          child: child,
        );

      case ConnectivityButtonType.outlined:
        if (icon != null) {
          return OutlinedButton.icon(
            onPressed: onPressed,
            icon: icon!,
            label: child,
            style: style,
          );
        }
        return OutlinedButton(
          onPressed: onPressed,
          style: style,
          child: child,
        );
    }
  }

  /// Get default offline message
  String _getDefaultOfflineMessage(bool isPoorConnection) {
    if (isPoorConnection) {
      return 'الاتصال ضعيف - قد لا تعمل هذه الميزة بشكل صحيح';
    }
    return 'يتطلب هذا الإجراء الاتصال بالإنترنت';
  }
}

/// Button type enumeration
enum ConnectivityButtonType {
  elevated,
  text,
  outlined,
}

/// IconButton variant that is connectivity-aware
/// زر أيقونة واعي بحالة الاتصال
class ConnectivityAwareIconButton extends ConsumerWidget {
  final Widget icon;
  final VoidCallback? onPressed;
  final bool requiresOnline;
  final bool allowPoorConnection;
  final String? offlineTooltip;
  final String? tooltip;
  final double? iconSize;
  final Color? color;
  final Color? disabledColor;

  const ConnectivityAwareIconButton({
    super.key,
    required this.icon,
    required this.onPressed,
    this.requiresOnline = true,
    this.allowPoorConnection = true,
    this.offlineTooltip,
    this.tooltip,
    this.iconSize,
    this.color,
    this.disabledColor,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final connectivityState = ref.watch(enhancedConnectivityStateProvider);

    final bool isConnected = connectivityState.isOnline ||
        (allowPoorConnection && connectivityState.isPoorConnection);

    final bool shouldEnable = !requiresOnline || isConnected;
    final VoidCallback? effectiveOnPressed =
        shouldEnable ? onPressed : null;

    String effectiveTooltip = tooltip ?? '';
    if (requiresOnline && !isConnected) {
      effectiveTooltip = offlineTooltip ??
          (connectivityState.isPoorConnection
              ? 'الاتصال ضعيف - قد لا تعمل هذه الميزة'
              : 'يتطلب الاتصال بالإنترنت');
    }

    return Tooltip(
      message: effectiveTooltip,
      child: IconButton(
        icon: icon,
        onPressed: effectiveOnPressed,
        iconSize: iconSize,
        color: color,
        disabledColor: disabledColor,
      ),
    );
  }
}

/// FloatingActionButton variant that is connectivity-aware
/// زر عائم واعي بحالة الاتصال
class ConnectivityAwareFAB extends ConsumerWidget {
  final Widget child;
  final VoidCallback? onPressed;
  final bool requiresOnline;
  final bool allowPoorConnection;
  final String? offlineTooltip;
  final String? tooltip;
  final Color? backgroundColor;
  final Color? foregroundColor;

  const ConnectivityAwareFAB({
    super.key,
    required this.child,
    required this.onPressed,
    this.requiresOnline = true,
    this.allowPoorConnection = true,
    this.offlineTooltip,
    this.tooltip,
    this.backgroundColor,
    this.foregroundColor,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final connectivityState = ref.watch(enhancedConnectivityStateProvider);

    final bool isConnected = connectivityState.isOnline ||
        (allowPoorConnection && connectivityState.isPoorConnection);

    final bool shouldEnable = !requiresOnline || isConnected;
    final VoidCallback? effectiveOnPressed =
        shouldEnable ? onPressed : null;

    String effectiveTooltip = tooltip ?? '';
    if (requiresOnline && !isConnected) {
      effectiveTooltip = offlineTooltip ?? 'يتطلب الاتصال بالإنترنت';
    }

    return FloatingActionButton(
      onPressed: effectiveOnPressed,
      tooltip: effectiveTooltip,
      backgroundColor: backgroundColor,
      foregroundColor: foregroundColor,
      child: child,
    );
  }
}

/// Action button with connectivity status indicator
/// زر إجراء مع مؤشر حالة الاتصال
class ConnectivityActionButton extends ConsumerWidget {
  final String label;
  final VoidCallback? onPressed;
  final IconData? icon;
  final bool requiresOnline;
  final bool showStatus;

  const ConnectivityActionButton({
    super.key,
    required this.label,
    required this.onPressed,
    this.icon,
    this.requiresOnline = true,
    this.showStatus = true,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final connectivityState = ref.watch(enhancedConnectivityStateProvider);

    return ConnectivityAwareButton.elevated(
      onPressed: onPressed,
      requiresOnline: requiresOnline,
      icon: icon != null ? Icon(icon) : null,
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(label),
          if (showStatus && requiresOnline) ...[
            const SizedBox(width: 8),
            Container(
              width: 8,
              height: 8,
              decoration: BoxDecoration(
                color: connectivityState.isOnline
                    ? Colors.green
                    : Colors.red,
                shape: BoxShape.circle,
              ),
            ),
          ],
        ],
      ),
    );
  }
}
