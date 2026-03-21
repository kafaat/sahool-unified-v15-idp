import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../utils/app_logger.dart';

/// Secure Input Widget for Sensitive Data
/// عنصر إدخال آمن للبيانات الحساسة
///
/// Features:
/// - Automatic clipboard clearing after paste
/// - Obscure text with secure toggle
/// - Disables text selection in sensitive mode
/// - Prevents third-party keyboard suggestions
/// - Secure input type for passwords and PINs
/// - Configurable auto-clear delay
///
/// المميزات:
/// - مسح الحافظة تلقائياً بعد اللصق
/// - إخفاء النص مع تبديل آمن
/// - تعطيل تحديد النص في الوضع الحساس
/// - منع اقتراحات لوحة المفاتيح الخارجية
/// - نوع إدخال آمن لكلمات المرور والأرقام السرية
/// - تأخير قابل للتكوين لمسح الحافظة

/// Secure Text Field for Passwords and Sensitive Data
class SecureTextField extends StatefulWidget {
  /// Controller for the text field
  final TextEditingController? controller;

  /// Placeholder text
  final String? hintText;

  /// Label text
  final String? labelText;

  /// Error text
  final String? errorText;

  /// Whether the field is for password entry (obscures text)
  final bool isPassword;

  /// Whether to show/hide toggle for password
  final bool showPasswordToggle;

  /// Whether to clear clipboard after paste
  final bool clearClipboardAfterPaste;

  /// Delay before clearing clipboard (in seconds)
  final int clipboardClearDelay;

  /// Whether to disable autocomplete suggestions
  final bool disableAutocomplete;

  /// Whether to disable text selection
  final bool disableSelection;

  /// Input type for the field
  final TextInputType? keyboardType;

  /// Input action
  final TextInputAction? textInputAction;

  /// Maximum length
  final int? maxLength;

  /// Validation function
  final String? Function(String?)? validator;

  /// Called when text changes
  final void Function(String)? onChanged;

  /// Called when editing is complete
  final void Function()? onEditingComplete;

  /// Called when submitted
  final void Function(String)? onSubmitted;

  /// Focus node
  final FocusNode? focusNode;

  /// Prefix icon
  final Widget? prefixIcon;

  /// Suffix icon (overridden if showPasswordToggle is true)
  final Widget? suffixIcon;

  /// Whether the field is enabled
  final bool enabled;

  /// Whether the field is read-only
  final bool readOnly;

  /// Input formatters
  final List<TextInputFormatter>? inputFormatters;

  /// Decoration (used as base, some properties may be overridden)
  final InputDecoration? decoration;

  /// Text style
  final TextStyle? style;

  const SecureTextField({
    super.key,
    this.controller,
    this.hintText,
    this.labelText,
    this.errorText,
    this.isPassword = false,
    this.showPasswordToggle = true,
    this.clearClipboardAfterPaste = true,
    this.clipboardClearDelay = 30,
    this.disableAutocomplete = true,
    this.disableSelection = false,
    this.keyboardType,
    this.textInputAction,
    this.maxLength,
    this.validator,
    this.onChanged,
    this.onEditingComplete,
    this.onSubmitted,
    this.focusNode,
    this.prefixIcon,
    this.suffixIcon,
    this.enabled = true,
    this.readOnly = false,
    this.inputFormatters,
    this.decoration,
    this.style,
  });

  @override
  State<SecureTextField> createState() => _SecureTextFieldState();
}

class _SecureTextFieldState extends State<SecureTextField> {
  late TextEditingController _controller;
  late FocusNode _focusNode;
  bool _obscureText = true;
  Timer? _clipboardClearTimer;
  String? _previousClipboardContent;

  @override
  void initState() {
    super.initState();
    _controller = widget.controller ?? TextEditingController();
    _focusNode = widget.focusNode ?? FocusNode();
    _obscureText = widget.isPassword;

    // Store current clipboard content to detect pastes
    _storeClipboardContent();
  }

  @override
  void dispose() {
    _clipboardClearTimer?.cancel();
    if (widget.controller == null) {
      _controller.dispose();
    }
    if (widget.focusNode == null) {
      _focusNode.dispose();
    }
    super.dispose();
  }

  Future<void> _storeClipboardContent() async {
    try {
      final data = await Clipboard.getData(Clipboard.kTextPlain);
      _previousClipboardContent = data?.text;
    } catch (e) {
      // Clipboard access may fail on some platforms
    }
  }

  Future<void> _checkForPaste() async {
    if (!widget.clearClipboardAfterPaste) return;

    try {
      final data = await Clipboard.getData(Clipboard.kTextPlain);
      final currentClipboard = data?.text;

      // If clipboard content is now in our text field, schedule clearing
      if (currentClipboard != null &&
          currentClipboard.isNotEmpty &&
          _controller.text.contains(currentClipboard) &&
          currentClipboard != _previousClipboardContent) {
        _scheduleClearClipboard();
      }

      _previousClipboardContent = currentClipboard;
    } catch (e) {
      // Clipboard access may fail on some platforms
    }
  }

  void _scheduleClearClipboard() {
    _clipboardClearTimer?.cancel();
    _clipboardClearTimer = Timer(
      Duration(seconds: widget.clipboardClearDelay),
      _clearClipboard,
    );

    AppLogger.d('Clipboard clear scheduled', tag: 'SecureInput', data: {
      'delay': widget.clipboardClearDelay,
    });
  }

  Future<void> _clearClipboard() async {
    try {
      await Clipboard.setData(const ClipboardData(text: ''));
      AppLogger.d('Clipboard cleared for security', tag: 'SecureInput');
    } catch (e) {
      AppLogger.w('Failed to clear clipboard: $e', tag: 'SecureInput');
    }
  }

  void _toggleObscure() {
    setState(() {
      _obscureText = !_obscureText;
    });
  }

  void _handleChanged(String value) {
    _checkForPaste();
    widget.onChanged?.call(value);
  }

  @override
  Widget build(BuildContext context) {
    final isArabic = Localizations.localeOf(context).languageCode == 'ar';

    // Build suffix icon
    Widget? suffixIcon = widget.suffixIcon;
    if (widget.isPassword && widget.showPasswordToggle) {
      suffixIcon = IconButton(
        icon: Icon(
          _obscureText ? Icons.visibility_off : Icons.visibility,
          color: Colors.grey,
        ),
        onPressed: _toggleObscure,
        tooltip: _obscureText
            ? (isArabic ? 'إظهار كلمة المرور' : 'Show password')
            : (isArabic ? 'إخفاء كلمة المرور' : 'Hide password'),
      );
    }

    // Build input decoration
    final decoration = (widget.decoration ?? const InputDecoration()).copyWith(
      hintText: widget.hintText,
      labelText: widget.labelText,
      errorText: widget.errorText,
      prefixIcon: widget.prefixIcon,
      suffixIcon: suffixIcon,
    );

    // Determine keyboard type
    TextInputType keyboardType = widget.keyboardType ?? TextInputType.text;
    if (widget.isPassword) {
      keyboardType = TextInputType.visiblePassword;
    }

    return TextFormField(
      controller: _controller,
      focusNode: _focusNode,
      obscureText: widget.isPassword && _obscureText,
      keyboardType: keyboardType,
      textInputAction: widget.textInputAction,
      maxLength: widget.maxLength,
      enabled: widget.enabled,
      readOnly: widget.readOnly,
      style: widget.style,
      decoration: decoration,
      validator: widget.validator,
      onChanged: _handleChanged,
      onEditingComplete: widget.onEditingComplete,
      onFieldSubmitted: widget.onSubmitted,
      inputFormatters: widget.inputFormatters,
      enableSuggestions: !widget.disableAutocomplete,
      autocorrect: !widget.disableAutocomplete,
      enableInteractiveSelection: !widget.disableSelection,
      // Secure keyboard settings
      autofillHints: widget.disableAutocomplete ? null : null,
      textCapitalization: TextCapitalization.none,
    );
  }
}

/// Secure PIN Input Field
/// حقل إدخال رقم التعريف الشخصي الآمن
class SecurePinField extends StatefulWidget {
  /// PIN length
  final int length;

  /// Called when PIN is complete
  final void Function(String)? onCompleted;

  /// Called when PIN changes
  final void Function(String)? onChanged;

  /// Whether to obscure PIN digits
  final bool obscureText;

  /// Whether to clear clipboard after paste
  final bool clearClipboardAfterPaste;

  /// Size of each PIN box
  final double boxSize;

  /// Spacing between boxes
  final double spacing;

  /// Border radius
  final double borderRadius;

  /// Active (focused) color
  final Color? activeColor;

  /// Inactive color
  final Color? inactiveColor;

  /// Error color
  final Color? errorColor;

  /// Whether there's an error
  final bool hasError;

  /// Text style for PIN digits
  final TextStyle? textStyle;

  /// Whether the field is enabled
  final bool enabled;

  /// Controller
  final TextEditingController? controller;

  /// Focus node
  final FocusNode? focusNode;

  const SecurePinField({
    super.key,
    this.length = 6,
    this.onCompleted,
    this.onChanged,
    this.obscureText = true,
    this.clearClipboardAfterPaste = true,
    this.boxSize = 50,
    this.spacing = 8,
    this.borderRadius = 8,
    this.activeColor,
    this.inactiveColor,
    this.errorColor,
    this.hasError = false,
    this.textStyle,
    this.enabled = true,
    this.controller,
    this.focusNode,
  });

  @override
  State<SecurePinField> createState() => _SecurePinFieldState();
}

class _SecurePinFieldState extends State<SecurePinField> {
  late TextEditingController _controller;
  late FocusNode _focusNode;
  List<String> _digits = [];

  @override
  void initState() {
    super.initState();
    _controller = widget.controller ?? TextEditingController();
    _focusNode = widget.focusNode ?? FocusNode();
    _digits = List.filled(widget.length, '');
    _controller.addListener(_onTextChanged);
  }

  @override
  void dispose() {
    _controller.removeListener(_onTextChanged);
    if (widget.controller == null) {
      _controller.dispose();
    }
    if (widget.focusNode == null) {
      _focusNode.dispose();
    }
    super.dispose();
  }

  void _onTextChanged() {
    final text = _controller.text;
    setState(() {
      _digits = List.filled(widget.length, '');
      for (int i = 0; i < text.length && i < widget.length; i++) {
        _digits[i] = text[i];
      }
    });

    widget.onChanged?.call(text);

    if (text.length == widget.length) {
      widget.onCompleted?.call(text);
      _clearClipboardIfNeeded();
    }
  }

  Future<void> _clearClipboardIfNeeded() async {
    if (!widget.clearClipboardAfterPaste) return;

    try {
      final data = await Clipboard.getData(Clipboard.kTextPlain);
      if (data?.text != null && data!.text!.length == widget.length) {
        // Likely a PIN was pasted, clear it
        await Clipboard.setData(const ClipboardData(text: ''));
        AppLogger.d('Clipboard cleared after PIN paste', tag: 'SecureInput');
      }
    } catch (e) {
      // Ignore clipboard errors
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final activeColor = widget.activeColor ?? theme.primaryColor;
    final inactiveColor = widget.inactiveColor ?? Colors.grey.shade300;
    final errorColor = widget.errorColor ?? theme.colorScheme.error;

    return GestureDetector(
      onTap: () {
        _focusNode.requestFocus();
      },
      child: Stack(
        children: [
          // Hidden text field for input
          Opacity(
            opacity: 0,
            child: TextField(
              controller: _controller,
              focusNode: _focusNode,
              keyboardType: TextInputType.number,
              maxLength: widget.length,
              enabled: widget.enabled,
              inputFormatters: [
                FilteringTextInputFormatter.digitsOnly,
                LengthLimitingTextInputFormatter(widget.length),
              ],
              enableSuggestions: false,
              autocorrect: false,
              decoration: const InputDecoration(
                counterText: '',
              ),
            ),
          ),

          // Visual PIN boxes
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: List.generate(widget.length, (index) {
              final isActive = index == _controller.text.length && _focusNode.hasFocus;
              final isFilled = _digits[index].isNotEmpty;

              return Container(
                width: widget.boxSize,
                height: widget.boxSize,
                margin: EdgeInsets.symmetric(horizontal: widget.spacing / 2),
                decoration: BoxDecoration(
                  color: theme.scaffoldBackgroundColor,
                  borderRadius: BorderRadius.circular(widget.borderRadius),
                  border: Border.all(
                    color: widget.hasError
                        ? errorColor
                        : isActive
                            ? activeColor
                            : inactiveColor,
                    width: isActive ? 2 : 1,
                  ),
                ),
                child: Center(
                  child: isFilled
                      ? widget.obscureText
                          ? Container(
                              width: 12,
                              height: 12,
                              decoration: BoxDecoration(
                                color: widget.hasError ? errorColor : activeColor,
                                shape: BoxShape.circle,
                              ),
                            )
                          : Text(
                              _digits[index],
                              style: widget.textStyle ??
                                  TextStyle(
                                    fontSize: 24,
                                    fontWeight: FontWeight.bold,
                                    color: widget.hasError ? errorColor : activeColor,
                                  ),
                            )
                      : isActive
                          ? Container(
                              width: 2,
                              height: 24,
                              color: activeColor,
                            )
                          : null,
                ),
              );
            }),
          ),
        ],
      ),
    );
  }
}

/// Clipboard Security Manager
/// Provides utilities for secure clipboard operations
class ClipboardSecurityManager {
  static Timer? _clearTimer;

  /// Copy text to clipboard with auto-clear
  static Future<void> copyWithAutoClear(
    String text, {
    Duration clearDelay = const Duration(seconds: 30),
    String? label,
  }) async {
    try {
      await Clipboard.setData(ClipboardData(text: text));

      AppLogger.d('Copied to clipboard', tag: 'ClipboardSecurity', data: {
        'label': label ?? 'text',
        'clearDelay': clearDelay.inSeconds,
      });

      // Schedule clearing
      _clearTimer?.cancel();
      _clearTimer = Timer(clearDelay, () async {
        await clearClipboard();
      });
    } catch (e) {
      AppLogger.e('Failed to copy to clipboard', tag: 'ClipboardSecurity', error: e);
    }
  }

  /// Clear clipboard immediately
  static Future<void> clearClipboard() async {
    try {
      await Clipboard.setData(const ClipboardData(text: ''));
      _clearTimer?.cancel();
      _clearTimer = null;
      AppLogger.d('Clipboard cleared', tag: 'ClipboardSecurity');
    } catch (e) {
      AppLogger.w('Failed to clear clipboard: $e', tag: 'ClipboardSecurity');
    }
  }

  /// Cancel scheduled clipboard clear
  static void cancelScheduledClear() {
    _clearTimer?.cancel();
    _clearTimer = null;
  }

  /// Check if clipboard has content
  static Future<bool> hasContent() async {
    try {
      final data = await Clipboard.getData(Clipboard.kTextPlain);
      return data?.text?.isNotEmpty ?? false;
    } catch (e) {
      return false;
    }
  }
}

/// Secure Form Field Wrapper
/// Adds security features to any form field
class SecureFormField extends StatelessWidget {
  final Widget child;
  final bool preventScreenshot;
  final bool disableSelection;
  final VoidCallback? onInteraction;

  const SecureFormField({
    super.key,
    required this.child,
    this.preventScreenshot = false,
    this.disableSelection = false,
    this.onInteraction,
  });

  @override
  Widget build(BuildContext context) {
    Widget result = child;

    if (disableSelection) {
      result = SelectionContainer.disabled(child: result);
    }

    if (onInteraction != null) {
      result = GestureDetector(
        onTap: onInteraction,
        child: result,
      );
    }

    return result;
  }
}

/// OTP Input Field with Secure Features
/// حقل إدخال رمز التحقق لمرة واحدة مع ميزات آمنة
class SecureOtpField extends StatefulWidget {
  /// OTP length
  final int length;

  /// Called when OTP is complete
  final void Function(String)? onCompleted;

  /// Called when OTP changes
  final void Function(String)? onChanged;

  /// Whether to obscure digits
  final bool obscureText;

  /// Whether to auto-focus
  final bool autofocus;

  /// Whether field is enabled
  final bool enabled;

  /// Error message
  final String? errorText;

  /// Controller
  final TextEditingController? controller;

  const SecureOtpField({
    super.key,
    this.length = 6,
    this.onCompleted,
    this.onChanged,
    this.obscureText = false,
    this.autofocus = true,
    this.enabled = true,
    this.errorText,
    this.controller,
  });

  @override
  State<SecureOtpField> createState() => _SecureOtpFieldState();
}

class _SecureOtpFieldState extends State<SecureOtpField> {
  late List<TextEditingController> _controllers;
  late List<FocusNode> _focusNodes;

  @override
  void initState() {
    super.initState();
    _controllers = List.generate(
      widget.length,
      (_) => TextEditingController(),
    );
    _focusNodes = List.generate(
      widget.length,
      (_) => FocusNode(),
    );

    // Sync with external controller if provided
    if (widget.controller != null) {
      widget.controller!.addListener(_syncFromExternalController);
    }

    // Auto-focus first field
    if (widget.autofocus) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        _focusNodes[0].requestFocus();
      });
    }
  }

  @override
  void dispose() {
    for (final controller in _controllers) {
      controller.dispose();
    }
    for (final node in _focusNodes) {
      node.dispose();
    }
    if (widget.controller != null) {
      widget.controller!.removeListener(_syncFromExternalController);
    }
    super.dispose();
  }

  void _syncFromExternalController() {
    final text = widget.controller!.text;
    for (int i = 0; i < widget.length; i++) {
      _controllers[i].text = i < text.length ? text[i] : '';
    }
  }

  String _getOtp() {
    return _controllers.map((c) => c.text).join();
  }

  void _onChanged(int index, String value) {
    if (value.length > 1) {
      // Handle paste
      final chars = value.split('');
      for (int i = 0; i < chars.length && (index + i) < widget.length; i++) {
        _controllers[index + i].text = chars[i];
      }
      // Focus last filled or next empty
      final lastIndex = (index + chars.length - 1).clamp(0, widget.length - 1);
      if (lastIndex < widget.length - 1) {
        _focusNodes[lastIndex + 1].requestFocus();
      }
      // Clear clipboard for security
      ClipboardSecurityManager.clearClipboard();
    } else if (value.isNotEmpty) {
      // Move to next field
      if (index < widget.length - 1) {
        _focusNodes[index + 1].requestFocus();
      }
    }

    final otp = _getOtp();
    widget.onChanged?.call(otp);

    if (otp.length == widget.length) {
      widget.onCompleted?.call(otp);
    }
  }

  void _onKeyDown(int index, KeyEvent event) {
    if (event is KeyDownEvent) {
      if (event.logicalKey == LogicalKeyboardKey.backspace) {
        if (_controllers[index].text.isEmpty && index > 0) {
          _focusNodes[index - 1].requestFocus();
          _controllers[index - 1].clear();
        }
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final hasError = widget.errorText != null;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: List.generate(widget.length, (index) {
            return Container(
              width: 48,
              height: 56,
              margin: const EdgeInsets.symmetric(horizontal: 4),
              child: KeyboardListener(
                focusNode: FocusNode(),
                onKeyEvent: (event) => _onKeyDown(index, event),
                child: TextField(
                  controller: _controllers[index],
                  focusNode: _focusNodes[index],
                  textAlign: TextAlign.center,
                  keyboardType: TextInputType.number,
                  maxLength: widget.length, // Allow paste
                  enabled: widget.enabled,
                  obscureText: widget.obscureText,
                  style: const TextStyle(
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                  ),
                  decoration: InputDecoration(
                    counterText: '',
                    contentPadding: EdgeInsets.zero,
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(8),
                      borderSide: BorderSide(
                        color: hasError
                            ? theme.colorScheme.error
                            : theme.dividerColor,
                      ),
                    ),
                    focusedBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(8),
                      borderSide: BorderSide(
                        color: hasError
                            ? theme.colorScheme.error
                            : theme.primaryColor,
                        width: 2,
                      ),
                    ),
                    errorBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(8),
                      borderSide: BorderSide(
                        color: theme.colorScheme.error,
                      ),
                    ),
                  ),
                  inputFormatters: [
                    FilteringTextInputFormatter.digitsOnly,
                  ],
                  enableSuggestions: false,
                  autocorrect: false,
                  onChanged: (value) => _onChanged(index, value),
                ),
              ),
            );
          }),
        ),
        if (widget.errorText != null) ...[
          const SizedBox(height: 8),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 8),
            child: Text(
              widget.errorText!,
              style: TextStyle(
                color: theme.colorScheme.error,
                fontSize: 12,
              ),
            ),
          ),
        ],
      ],
    );
  }
}
