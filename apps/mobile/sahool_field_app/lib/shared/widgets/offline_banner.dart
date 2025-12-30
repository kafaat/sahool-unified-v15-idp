// ═══════════════════════════════════════════════════════════════════════════
// SAHOOL - Enhanced Offline Banner Widget
// شريط حالة الاتصال المحسن
// ═══════════════════════════════════════════════════════════════════════════

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/connectivity/connectivity_service.dart';
import '../../core/connectivity/connectivity_provider.dart';

/// Enhanced offline banner with smooth animations and multiple states
/// شريط حالة الاتصال المحسن مع رسوم متحركة سلسة وحالات متعددة
class OfflineBanner extends ConsumerStatefulWidget {
  /// Show banner even when online (for testing)
  final bool alwaysShow;

  /// Custom height for the banner
  final double? height;

  /// Show retry button
  final bool showRetryButton;

  /// Custom message override
  final String? customMessage;

  const OfflineBanner({
    super.key,
    this.alwaysShow = false,
    this.height,
    this.showRetryButton = true,
    this.customMessage,
  });

  @override
  ConsumerState<OfflineBanner> createState() => _OfflineBannerState();
}

class _OfflineBannerState extends ConsumerState<OfflineBanner>
    with SingleTickerProviderStateMixin {
  late AnimationController _animationController;
  late Animation<Offset> _slideAnimation;
  late Animation<double> _fadeAnimation;

  @override
  void initState() {
    super.initState();

    _animationController = AnimationController(
      duration: const Duration(milliseconds: 300),
      vsync: this,
    );

    _slideAnimation = Tween<Offset>(
      begin: const Offset(0, -1),
      end: Offset.zero,
    ).animate(CurvedAnimation(
      parent: _animationController,
      curve: Curves.easeOut,
    ));

    _fadeAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _animationController,
      curve: Curves.easeIn,
    ));
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final connectivityState = ref.watch(enhancedConnectivityStateProvider);
    final shouldShow = widget.alwaysShow ||
        connectivityState.isOffline ||
        connectivityState.isPoorConnection ||
        connectivityState.isReconnecting;

    // Animate in/out based on connectivity
    if (shouldShow) {
      _animationController.forward();
    } else {
      _animationController.reverse();
    }

    return SlideTransition(
      position: _slideAnimation,
      child: FadeTransition(
        opacity: _fadeAnimation,
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 300),
          height: shouldShow ? (widget.height ?? 44) : 0,
          width: double.infinity,
          decoration: BoxDecoration(
            color: _getBackgroundColor(connectivityState.status),
            boxShadow: shouldShow
                ? [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.1),
                      blurRadius: 4,
                      offset: const Offset(0, 2),
                    ),
                  ]
                : null,
          ),
          child: shouldShow
              ? SafeArea(
                  bottom: false,
                  child: Padding(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 16,
                      vertical: 8,
                    ),
                    child: Row(
                      children: [
                        _buildIcon(connectivityState.status),
                        const SizedBox(width: 12),
                        Expanded(
                          child: _buildMessage(connectivityState),
                        ),
                        if (widget.showRetryButton &&
                            connectivityState.isOffline)
                          _buildRetryButton(),
                        if (connectivityState.isReconnecting)
                          const SizedBox(
                            width: 18,
                            height: 18,
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                              valueColor:
                                  AlwaysStoppedAnimation<Color>(Colors.white),
                            ),
                          ),
                      ],
                    ),
                  ),
                )
              : const SizedBox.shrink(),
        ),
      ),
    );
  }

  /// Build icon based on connectivity status
  Widget _buildIcon(ConnectivityStatus status) {
    IconData iconData;
    switch (status) {
      case ConnectivityStatus.online:
        iconData = Icons.cloud_done;
        break;
      case ConnectivityStatus.poorConnection:
        iconData = Icons.signal_cellular_alt_2_bar;
        break;
      case ConnectivityStatus.reconnecting:
        iconData = Icons.cloud_sync;
        break;
      case ConnectivityStatus.offline:
      case ConnectivityStatus.unknown:
        iconData = Icons.cloud_off;
        break;
    }

    return Icon(
      iconData,
      color: Colors.white,
      size: 20,
    );
  }

  /// Build message text
  Widget _buildMessage(EnhancedConnectivityState state) {
    String message = widget.customMessage ?? state.status.displayMessage;

    // Add pending sync count if applicable
    if (state.hasPendingSync && !state.isReconnecting) {
      message += ' • ${state.pendingSyncCount} عنصر في الانتظار';
    }

    return Text(
      message,
      style: const TextStyle(
        color: Colors.white,
        fontSize: 13,
        fontWeight: FontWeight.w500,
      ),
      maxLines: 1,
      overflow: TextOverflow.ellipsis,
    );
  }

  /// Build retry button
  Widget _buildRetryButton() {
    return TextButton(
      onPressed: () async {
        final notifier = ref.read(enhancedConnectivityStateProvider.notifier);
        final success = await notifier.reconnect();

        if (mounted && success) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('تم إعادة الاتصال بنجاح'),
              backgroundColor: Colors.green,
              duration: Duration(seconds: 2),
            ),
          );
        }
      },
      style: TextButton.styleFrom(
        foregroundColor: Colors.white,
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
        minimumSize: Size.zero,
        tapTargetSize: MaterialTapTargetSize.shrinkWrap,
      ),
      child: const Text(
        'إعادة المحاولة',
        style: TextStyle(
          fontSize: 12,
          fontWeight: FontWeight.bold,
        ),
      ),
    );
  }

  /// Get background color based on status
  Color _getBackgroundColor(ConnectivityStatus status) {
    switch (status) {
      case ConnectivityStatus.online:
        return const Color(0xFF367C2B); // Green
      case ConnectivityStatus.poorConnection:
        return Colors.orange.shade700;
      case ConnectivityStatus.reconnecting:
        return Colors.blue.shade700;
      case ConnectivityStatus.offline:
      case ConnectivityStatus.unknown:
        return Colors.red.shade700;
    }
  }
}

/// Compact inline connectivity indicator
/// مؤشر الاتصال المضغوط
class ConnectivityStatusIndicator extends ConsumerWidget {
  final double size;
  final bool showLabel;

  const ConnectivityStatusIndicator({
    super.key,
    this.size = 24,
    this.showLabel = false,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final connectivityState = ref.watch(enhancedConnectivityStateProvider);

    if (showLabel) {
      return Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          _buildIndicator(connectivityState.status),
          const SizedBox(width: 8),
          Text(
            connectivityState.status.displayMessage,
            style: TextStyle(
              fontSize: 12,
              color: _getColor(connectivityState.status),
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      );
    }

    return _buildIndicator(connectivityState.status);
  }

  Widget _buildIndicator(ConnectivityStatus status) {
    return Tooltip(
      message: status.displayMessage,
      child: Container(
        width: size,
        height: size,
        decoration: BoxDecoration(
          color: _getColor(status).withOpacity(0.1),
          shape: BoxShape.circle,
        ),
        child: Icon(
          _getIcon(status),
          size: size * 0.6,
          color: _getColor(status),
        ),
      ),
    );
  }

  Color _getColor(ConnectivityStatus status) {
    switch (status) {
      case ConnectivityStatus.online:
        return Colors.green;
      case ConnectivityStatus.poorConnection:
        return Colors.orange;
      case ConnectivityStatus.reconnecting:
        return Colors.blue;
      case ConnectivityStatus.offline:
      case ConnectivityStatus.unknown:
        return Colors.red;
    }
  }

  IconData _getIcon(ConnectivityStatus status) {
    switch (status) {
      case ConnectivityStatus.online:
        return Icons.cloud_done;
      case ConnectivityStatus.poorConnection:
        return Icons.signal_cellular_alt_2_bar;
      case ConnectivityStatus.reconnecting:
        return Icons.cloud_sync;
      case ConnectivityStatus.offline:
      case ConnectivityStatus.unknown:
        return Icons.cloud_off;
    }
  }
}

/// Full-screen offline overlay
/// شاشة غير متصل بالكامل
class OfflineOverlay extends ConsumerWidget {
  final Widget child;
  final bool showOverlay;

  const OfflineOverlay({
    super.key,
    required this.child,
    this.showOverlay = true,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final connectivityState = ref.watch(enhancedConnectivityStateProvider);

    return Stack(
      children: [
        child,
        if (showOverlay && connectivityState.isOffline)
          Container(
            color: Colors.black54,
            child: Center(
              child: Card(
                margin: const EdgeInsets.all(32),
                child: Padding(
                  padding: const EdgeInsets.all(24),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const Icon(
                        Icons.cloud_off,
                        size: 64,
                        color: Colors.red,
                      ),
                      const SizedBox(height: 16),
                      const Text(
                        'غير متصل بالإنترنت',
                        style: TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 8),
                      const Text(
                        'تحقق من اتصالك بالإنترنت وحاول مرة أخرى',
                        textAlign: TextAlign.center,
                        style: TextStyle(
                          fontSize: 14,
                          color: Colors.grey,
                        ),
                      ),
                      const SizedBox(height: 24),
                      ElevatedButton.icon(
                        onPressed: () async {
                          final notifier = ref.read(
                              enhancedConnectivityStateProvider.notifier);
                          await notifier.reconnect();
                        },
                        icon: const Icon(Icons.refresh),
                        label: const Text('إعادة المحاولة'),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),
      ],
    );
  }
}
