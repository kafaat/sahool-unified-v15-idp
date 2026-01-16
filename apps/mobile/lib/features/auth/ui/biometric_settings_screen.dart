import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:local_auth/local_auth.dart';

import '../../../core/auth/biometric_service.dart';
import '../../../core/theme/sahool_theme.dart';

/// SAHOOL Biometric Settings Screen
/// شاشة إعدادات البصمة
///
/// Allows users to enable/disable biometric authentication
/// and view biometric information.

class BiometricSettingsScreen extends ConsumerStatefulWidget {
  const BiometricSettingsScreen({super.key});

  @override
  ConsumerState<BiometricSettingsScreen> createState() =>
      _BiometricSettingsScreenState();
}

class _BiometricSettingsScreenState
    extends ConsumerState<BiometricSettingsScreen> {
  bool _isLoading = true;
  bool _isAvailable = false;
  bool _isEnabled = false;
  List<BiometricType> _availableBiometrics = [];
  String? _errorMessage;
  bool _isToggling = false;

  @override
  void initState() {
    super.initState();
    _loadBiometricStatus();
  }

  Future<void> _loadBiometricStatus() async {
    setState(() => _isLoading = true);

    try {
      final biometricService = ref.read(biometricServiceProvider);

      final available = await biometricService.isAvailable();
      final enabled = await biometricService.isEnabled();
      final biometrics = await biometricService.getAvailableBiometrics();

      if (mounted) {
        setState(() {
          _isAvailable = available;
          _isEnabled = enabled;
          _availableBiometrics = biometrics;
          _isLoading = false;
          _errorMessage = null;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _isLoading = false;
          _errorMessage = 'فشل في تحميل إعدادات البصمة';
        });
      }
    }
  }

  Future<void> _toggleBiometric(bool enable) async {
    if (_isToggling) return;

    setState(() {
      _isToggling = true;
      _errorMessage = null;
    });

    try {
      final biometricService = ref.read(biometricServiceProvider);

      if (enable) {
        final success = await biometricService.enable();
        if (success) {
          setState(() => _isEnabled = true);
          _showSuccessSnackBar('تم تفعيل تسجيل الدخول بالبصمة');
        }
      } else {
        await biometricService.disable();
        setState(() => _isEnabled = false);
        _showSuccessSnackBar('تم إلغاء تفعيل تسجيل الدخول بالبصمة');
      }
    } on BiometricException catch (e) {
      _showErrorSnackBar(e.message);
    } catch (e) {
      _showErrorSnackBar('حدث خطأ. حاول مرة أخرى.');
    } finally {
      if (mounted) {
        setState(() => _isToggling = false);
      }
    }
  }

  void _showSuccessSnackBar(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Row(
          children: [
            const Icon(Icons.check_circle, color: Colors.white),
            const SizedBox(width: 12),
            Text(message),
          ],
        ),
        backgroundColor: Colors.green,
        behavior: SnackBarBehavior.floating,
      ),
    );
  }

  void _showErrorSnackBar(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Row(
          children: [
            const Icon(Icons.error, color: Colors.white),
            const SizedBox(width: 12),
            Expanded(child: Text(message)),
          ],
        ),
        backgroundColor: Colors.red,
        behavior: SnackBarBehavior.floating,
      ),
    );
  }

  String _getBiometricTypeName(BiometricType type) {
    switch (type) {
      case BiometricType.fingerprint:
        return 'بصمة الإصبع';
      case BiometricType.face:
        return 'بصمة الوجه (Face ID)';
      case BiometricType.iris:
        return 'بصمة العين';
      case BiometricType.strong:
        return 'مصادقة قوية';
      case BiometricType.weak:
        return 'مصادقة ضعيفة';
    }
  }

  IconData _getBiometricTypeIcon(BiometricType type) {
    switch (type) {
      case BiometricType.fingerprint:
        return Icons.fingerprint;
      case BiometricType.face:
        return Icons.face;
      case BiometricType.iris:
        return Icons.remove_red_eye;
      case BiometricType.strong:
        return Icons.security;
      case BiometricType.weak:
        return Icons.lock_outline;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('إعدادات البصمة'),
        centerTitle: true,
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _buildContent(),
    );
  }

  Widget _buildContent() {
    if (_errorMessage != null) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.error_outline, size: 64, color: Colors.red[300]),
            const SizedBox(height: 16),
            Text(
              _errorMessage!,
              style: TextStyle(color: Colors.grey[600]),
            ),
            const SizedBox(height: 24),
            ElevatedButton.icon(
              onPressed: _loadBiometricStatus,
              icon: const Icon(Icons.refresh),
              label: const Text('إعادة المحاولة'),
            ),
          ],
        ),
      );
    }

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header Card
          _buildHeaderCard(),

          const SizedBox(height: 24),

          // Main Toggle
          _buildMainToggle(),

          const SizedBox(height: 24),

          // Available Biometrics
          if (_availableBiometrics.isNotEmpty) ...[
            _buildSectionTitle('أنواع البصمة المتاحة'),
            const SizedBox(height: 12),
            _buildAvailableBiometrics(),
          ],

          const SizedBox(height: 24),

          // Security Info
          _buildSecurityInfo(),

          const SizedBox(height: 24),

          // Help Section
          _buildHelpSection(),
        ],
      ),
    );
  }

  Widget _buildHeaderCard() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            SahoolColors.primary,
            SahoolColors.primary.withOpacity(0.8),
          ],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: SahoolColors.primary.withOpacity(0.3),
            blurRadius: 20,
            offset: const Offset(0, 8),
          ),
        ],
      ),
      child: Column(
        children: [
          Container(
            width: 80,
            height: 80,
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.2),
              shape: BoxShape.circle,
            ),
            child: Icon(
              _isEnabled ? Icons.fingerprint : Icons.fingerprint_outlined,
              size: 48,
              color: Colors.white,
            ),
          ),
          const SizedBox(height: 16),
          Text(
            _isAvailable
                ? (_isEnabled ? 'البصمة مُفعّلة' : 'البصمة غير مُفعّلة')
                : 'البصمة غير متاحة',
            style: const TextStyle(
              color: Colors.white,
              fontSize: 22,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            _isAvailable
                ? 'سجّل دخولك بسرعة وأمان باستخدام بصمتك'
                : 'جهازك لا يدعم المصادقة بالبصمة',
            style: TextStyle(
              color: Colors.white.withOpacity(0.9),
              fontSize: 14,
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildMainToggle() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Row(
        children: [
          Container(
            width: 48,
            height: 48,
            decoration: BoxDecoration(
              color: _isEnabled
                  ? SahoolColors.primary.withOpacity(0.1)
                  : Colors.grey[100],
              borderRadius: BorderRadius.circular(12),
            ),
            child: Icon(
              Icons.fingerprint,
              color: _isEnabled ? SahoolColors.primary : Colors.grey,
              size: 28,
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'تسجيل الدخول بالبصمة',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  _isEnabled
                      ? 'يمكنك تسجيل الدخول باستخدام بصمتك'
                      : 'فعّل للوصول السريع',
                  style: TextStyle(
                    fontSize: 13,
                    color: Colors.grey[600],
                  ),
                ),
              ],
            ),
          ),
          if (_isToggling)
            const SizedBox(
              width: 24,
              height: 24,
              child: CircularProgressIndicator(strokeWidth: 2),
            )
          else
            Switch.adaptive(
              value: _isEnabled,
              onChanged: _isAvailable ? _toggleBiometric : null,
              activeColor: SahoolColors.primary,
            ),
        ],
      ),
    );
  }

  Widget _buildSectionTitle(String title) {
    return Text(
      title,
      style: const TextStyle(
        fontSize: 16,
        fontWeight: FontWeight.bold,
        color: Colors.black87,
      ),
    );
  }

  Widget _buildAvailableBiometrics() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        children: _availableBiometrics.map((type) {
          return Padding(
            padding: const EdgeInsets.symmetric(vertical: 8),
            child: Row(
              children: [
                Container(
                  width: 40,
                  height: 40,
                  decoration: BoxDecoration(
                    color: SahoolColors.primary.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: Icon(
                    _getBiometricTypeIcon(type),
                    color: SahoolColors.primary,
                    size: 22,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Text(
                    _getBiometricTypeName(type),
                    style: const TextStyle(
                      fontSize: 15,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ),
                Icon(
                  Icons.check_circle,
                  color: Colors.green[400],
                  size: 20,
                ),
              ],
            ),
          );
        }).toList(),
      ),
    );
  }

  Widget _buildSecurityInfo() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.blue[50],
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.blue[100]!),
      ),
      child: Row(
        children: [
          Icon(Icons.security, color: Colors.blue[700], size: 32),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'معلومات الأمان',
                  style: TextStyle(
                    fontSize: 15,
                    fontWeight: FontWeight.bold,
                    color: Colors.blue[800],
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  'بيانات البصمة لا تغادر جهازك أبداً ولا يتم تخزينها على خوادمنا. التحقق يتم محلياً على جهازك.',
                  style: TextStyle(
                    fontSize: 13,
                    color: Colors.blue[700],
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildHelpSection() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.grey[100],
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Icon(Icons.help_outline, color: Colors.grey),
              SizedBox(width: 8),
              Text(
                'الأسئلة الشائعة',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          _buildFaqItem(
            'كيف أفعّل البصمة؟',
            'اضغط على زر التفعيل أعلاه، ثم قم بالتحقق باستخدام بصمتك.',
          ),
          _buildFaqItem(
            'هل بياناتي آمنة؟',
            'نعم، بيانات البصمة تبقى على جهازك فقط ولا يتم إرسالها لأي مكان.',
          ),
          _buildFaqItem(
            'ماذا لو لم تعمل البصمة؟',
            'يمكنك دائماً تسجيل الدخول باستخدام رقم هاتفك ورمز التحقق.',
          ),
        ],
      ),
    );
  }

  Widget _buildFaqItem(String question, String answer) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            question,
            style: const TextStyle(
              fontWeight: FontWeight.w600,
              fontSize: 14,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            answer,
            style: TextStyle(
              fontSize: 13,
              color: Colors.grey[700],
            ),
          ),
        ],
      ),
    );
  }
}
