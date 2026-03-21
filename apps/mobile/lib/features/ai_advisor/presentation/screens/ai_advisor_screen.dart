/// AI Advisor Screen - Main Chat Interface
/// شاشة المستشار الذكي - واجهة المحادثة الرئيسية
///
/// Features:
/// - Chat interface with AI
/// - Quick question chips
/// - Context indicator
/// - Image upload for diagnosis
/// - Voice input support

import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:image_picker/image_picker.dart';
import 'package:go_router/go_router.dart';
import '../../../../core/config/theme.dart';
import '../../domain/models/advisory_request.dart';
import '../../state/ai_advisor_providers.dart';
import '../widgets/chat_bubble.dart';
import '../widgets/quick_question_chips.dart';
import '../widgets/context_indicator.dart';
import '../widgets/typing_indicator.dart';

class AiAdvisorScreen extends ConsumerStatefulWidget {
  final String? fieldId;
  final String? fieldName;
  final String? initialQuestion;

  const AiAdvisorScreen({
    super.key,
    this.fieldId,
    this.fieldName,
    this.initialQuestion,
  });

  @override
  ConsumerState<AiAdvisorScreen> createState() => _AiAdvisorScreenState();
}

class _AiAdvisorScreenState extends ConsumerState<AiAdvisorScreen> {
  final TextEditingController _messageController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  final FocusNode _focusNode = FocusNode();
  final ImagePicker _imagePicker = ImagePicker();

  bool _isComposing = false;
  bool _showQuickQuestions = true;
  File? _selectedImage;

  @override
  void initState() {
    super.initState();

    // Set initial field context if provided
    if (widget.fieldId != null) {
      Future.microtask(() {
        ref.read(aiAdvisorProvider.notifier).setFieldContext(
          widget.fieldId!,
          widget.fieldName,
        );
      });
    }

    // Load chat history
    Future.microtask(() {
      ref.read(aiAdvisorProvider.notifier).loadChatHistory();
    });

    // Send initial question if provided
    if (widget.initialQuestion != null && widget.initialQuestion!.isNotEmpty) {
      Future.microtask(() {
        _sendMessage(widget.initialQuestion!);
      });
    }
  }

  @override
  void dispose() {
    _messageController.dispose();
    _scrollController.dispose();
    _focusNode.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(aiAdvisorProvider);
    final isRTL = Directionality.of(context) == TextDirection.rtl;

    return Scaffold(
      appBar: AppBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('المستشار الذكي'),
            if (widget.fieldName != null)
              Text(
                widget.fieldName!,
                style: const TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.normal,
                ),
              ),
          ],
        ),
        actions: [
          // Context indicator button
          IconButton(
            icon: const Icon(Icons.info_outline),
            onPressed: () => _showContextSheet(context),
            tooltip: 'معلومات السياق',
          ),
          // History button
          IconButton(
            icon: const Icon(Icons.history),
            onPressed: () => context.push('/ai-advisor/history'),
            tooltip: 'سجل التوصيات',
          ),
          // More options
          PopupMenuButton(
            itemBuilder: (context) => [
              const PopupMenuItem(
                value: 'new_chat',
                child: Row(
                  children: [
                    Icon(Icons.add_comment),
                    SizedBox(width: 8),
                    Text('محادثة جديدة'),
                  ],
                ),
              ),
              const PopupMenuItem(
                value: 'clear_history',
                child: Row(
                  children: [
                    Icon(Icons.delete_sweep),
                    SizedBox(width: 8),
                    Text('مسح المحادثة'),
                  ],
                ),
              ),
            ],
            onSelected: _handleMenuAction,
          ),
        ],
      ),
      body: Column(
        children: [
          // Context indicator
          if (state.context != null)
            ContextIndicator(
              context: state.context!,
              fieldName: widget.fieldName,
              onTap: () => _showContextSheet(context),
            ),

          // Messages list
          Expanded(
            child: state.messages.isEmpty && !state.isLoading
                ? _buildWelcomeView()
                : _buildMessagesList(state),
          ),

          // Quick question chips (show when no messages or after welcome)
          if (_showQuickQuestions && state.messages.length < 3)
            QuickQuestionChips(
              questions: QuickQuestion.predefined,
              onQuestionSelected: _handleQuickQuestion,
            ),

          // Image preview (if selected)
          if (_selectedImage != null) _buildImagePreview(),

          // Typing indicator
          if (state.isTyping)
            const Padding(
              padding: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              child: Align(
                alignment: Alignment.centerRight,
                child: TypingIndicator(),
              ),
            ),

          // Error message
          if (state.error != null) _buildErrorBanner(state.error!),

          // Message input
          _buildMessageInput(isRTL),
        ],
      ),
    );
  }

  Widget _buildWelcomeView() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const SizedBox(height: 40),
          // AI Avatar
          Container(
            width: 100,
            height: 100,
            decoration: BoxDecoration(
              color: SahoolTheme.primary.withOpacity(0.1),
              shape: BoxShape.circle,
            ),
            child: Icon(
              Icons.psychology,
              size: 60,
              color: SahoolTheme.primary,
            ),
          ),
          const SizedBox(height: 24),
          // Welcome text
          Text(
            'مرحباً بك في المستشار الذكي',
            style: Theme.of(context).textTheme.headlineSmall?.copyWith(
              fontWeight: FontWeight.bold,
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 12),
          Text(
            'أنا هنا لمساعدتك في جميع استفساراتك الزراعية.\n'
            'يمكنني تقديم توصيات حول الري والتسميد ومكافحة الآفات والأمراض.',
            style: Theme.of(context).textTheme.bodyLarge?.copyWith(
              color: Colors.grey[600],
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 32),
          // Features grid
          Wrap(
            spacing: 16,
            runSpacing: 16,
            alignment: WrapAlignment.center,
            children: [
              _buildFeatureChip(Icons.water_drop, 'الري'),
              _buildFeatureChip(Icons.eco, 'التسميد'),
              _buildFeatureChip(Icons.pest_control, 'الآفات'),
              _buildFeatureChip(Icons.healing, 'الأمراض'),
              _buildFeatureChip(Icons.agriculture, 'الحصاد'),
              _buildFeatureChip(Icons.cloud, 'الطقس'),
            ],
          ),
          const SizedBox(height: 32),
          // Diagnosis button
          OutlinedButton.icon(
            onPressed: _pickImageForDiagnosis,
            icon: const Icon(Icons.camera_alt),
            label: const Text('التقط صورة لتشخيص المحصول'),
            style: OutlinedButton.styleFrom(
              padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildFeatureChip(IconData icon, String label) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      decoration: BoxDecoration(
        color: SahoolTheme.primary.withOpacity(0.1),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 18, color: SahoolTheme.primary),
          const SizedBox(width: 8),
          Text(
            label,
            style: TextStyle(
              color: SahoolTheme.primary,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMessagesList(AiAdvisorState state) {
    return ListView.builder(
      controller: _scrollController,
      reverse: true,
      padding: const EdgeInsets.symmetric(vertical: 16),
      itemCount: state.messages.length,
      itemBuilder: (context, index) {
        final message = state.messages[index];
        final showAvatar = index == 0 ||
            state.messages[index - 1].role != message.role;

        return AiChatBubble(
          message: message,
          showAvatar: showAvatar,
          onFeedback: message.isAssistant
              ? (isPositive) => _handleFeedback(message.id, isPositive)
              : null,
          onAdvisoryTap: message.recommendations != null
              ? (advisory) => context.push('/ai-advisor/details/${advisory.id}')
              : null,
        );
      },
    );
  }

  Widget _buildImagePreview() {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      padding: const EdgeInsets.all(8),
      decoration: BoxDecoration(
        color: Colors.grey[100],
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        children: [
          ClipRRect(
            borderRadius: BorderRadius.circular(8),
            child: Image.file(
              _selectedImage!,
              width: 60,
              height: 60,
              fit: BoxFit.cover,
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'صورة للتشخيص',
                  style: TextStyle(fontWeight: FontWeight.w600),
                ),
                Text(
                  'اضغط إرسال لتحليل الصورة',
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.grey[600],
                  ),
                ),
              ],
            ),
          ),
          IconButton(
            icon: const Icon(Icons.close),
            onPressed: () => setState(() => _selectedImage = null),
          ),
        ],
      ),
    );
  }

  Widget _buildErrorBanner(String error) {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.red[50],
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.red[200]!),
      ),
      child: Row(
        children: [
          Icon(Icons.error_outline, color: Colors.red[700], size: 20),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              error,
              style: TextStyle(color: Colors.red[700], fontSize: 14),
            ),
          ),
          IconButton(
            icon: const Icon(Icons.close, size: 18),
            color: Colors.red[700],
            onPressed: () {
              ref.read(aiAdvisorProvider.notifier).clearError();
            },
          ),
        ],
      ),
    );
  }

  Widget _buildMessageInput(bool isRTL) {
    return Container(
      padding: EdgeInsets.only(
        left: 8,
        right: 8,
        top: 8,
        bottom: MediaQuery.of(context).padding.bottom + 8,
      ),
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, -2),
          ),
        ],
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          // Image/Camera button
          IconButton(
            icon: const Icon(Icons.camera_alt_outlined),
            color: SahoolTheme.primary,
            onPressed: _pickImageForDiagnosis,
            tooltip: 'التقط صورة للتشخيص',
          ),

          // Message input field
          Expanded(
            child: Container(
              constraints: const BoxConstraints(maxHeight: 120),
              decoration: BoxDecoration(
                color: Colors.grey[100],
                borderRadius: BorderRadius.circular(24),
              ),
              child: TextField(
                controller: _messageController,
                focusNode: _focusNode,
                maxLines: null,
                textDirection: isRTL ? TextDirection.rtl : TextDirection.ltr,
                decoration: const InputDecoration(
                  hintText: 'اكتب سؤالك هنا...',
                  border: InputBorder.none,
                  contentPadding: EdgeInsets.symmetric(
                    horizontal: 16,
                    vertical: 12,
                  ),
                ),
                onChanged: (text) {
                  setState(() {
                    _isComposing = text.trim().isNotEmpty;
                    _showQuickQuestions = text.isEmpty;
                  });
                },
                onSubmitted: _isComposing ? (_) => _handleSend() : null,
              ),
            ),
          ),

          const SizedBox(width: 8),

          // Send button
          AnimatedContainer(
            duration: const Duration(milliseconds: 200),
            child: Material(
              color: _isComposing || _selectedImage != null
                  ? SahoolTheme.primary
                  : Colors.grey[300],
              borderRadius: BorderRadius.circular(24),
              child: InkWell(
                onTap: _isComposing || _selectedImage != null ? _handleSend : null,
                borderRadius: BorderRadius.circular(24),
                child: Container(
                  padding: const EdgeInsets.all(12),
                  child: Icon(
                    Icons.send,
                    color: _isComposing || _selectedImage != null
                        ? Colors.white
                        : Colors.grey[500],
                    size: 22,
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  void _handleSend() {
    final text = _messageController.text.trim();

    if (_selectedImage != null) {
      // Send diagnosis request with image
      ref.read(aiAdvisorProvider.notifier).diagnose(
        _selectedImage!.path,
        description: text.isNotEmpty ? text : null,
        fieldId: widget.fieldId,
      );
      setState(() => _selectedImage = null);
    } else if (text.isNotEmpty) {
      _sendMessage(text);
    }

    _messageController.clear();
    setState(() {
      _isComposing = false;
      _showQuickQuestions = false;
    });
    _scrollToBottom();
  }

  void _sendMessage(String message) {
    ref.read(aiAdvisorProvider.notifier).updateInputText(message);
    ref.read(aiAdvisorProvider.notifier).sendMessage();
  }

  void _handleQuickQuestion(QuickQuestion question) {
    final locale = Localizations.localeOf(context).languageCode;
    _sendMessage(question.getText(locale));
    setState(() => _showQuickQuestions = false);
  }

  void _handleFeedback(String messageId, bool isPositive) {
    ref.read(aiAdvisorProvider.notifier).submitMessageFeedback(
      messageId,
      isPositive,
    );

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(isPositive ? 'شكراً لتقييمك!' : 'سنعمل على التحسين'),
        duration: const Duration(seconds: 2),
      ),
    );
  }

  Future<void> _pickImageForDiagnosis() async {
    final source = await showModalBottomSheet<ImageSource>(
      context: context,
      builder: (context) => SafeArea(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            ListTile(
              leading: const Icon(Icons.camera_alt),
              title: const Text('التقط صورة'),
              onTap: () => Navigator.pop(context, ImageSource.camera),
            ),
            ListTile(
              leading: const Icon(Icons.photo_library),
              title: const Text('اختر من المعرض'),
              onTap: () => Navigator.pop(context, ImageSource.gallery),
            ),
          ],
        ),
      ),
    );

    if (source != null) {
      final pickedFile = await _imagePicker.pickImage(
        source: source,
        maxWidth: 1024,
        maxHeight: 1024,
        imageQuality: 85,
      );

      if (pickedFile != null) {
        setState(() {
          _selectedImage = File(pickedFile.path);
        });
      }
    }
  }

  void _showContextSheet(BuildContext context) {
    final state = ref.read(aiAdvisorProvider);

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) => DraggableScrollableSheet(
        initialChildSize: 0.5,
        minChildSize: 0.3,
        maxChildSize: 0.9,
        expand: false,
        builder: (context, scrollController) => SingleChildScrollView(
          controller: scrollController,
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Handle
              Center(
                child: Container(
                  width: 40,
                  height: 4,
                  decoration: BoxDecoration(
                    color: Colors.grey[300],
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),
              ),
              const SizedBox(height: 20),
              const Text(
                'معلومات السياق',
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                'البيانات المتاحة للمستشار الذكي',
                style: TextStyle(color: Colors.grey[600]),
              ),
              const SizedBox(height: 20),

              if (state.context != null) ...[
                // Field info
                if (state.context!.hasFieldData) ...[
                  _buildContextSection(
                    icon: Icons.grass,
                    title: 'الحقل',
                    content: state.context!.field!.nameAr ?? state.context!.field!.name,
                  ),
                ],

                // Weather info
                if (state.context!.hasWeatherData) ...[
                  _buildContextSection(
                    icon: Icons.cloud,
                    title: 'الطقس',
                    content: state.context!.weather!.temperatureSummaryAr,
                  ),
                ],

                // Crop info
                if (state.context!.hasCropData) ...[
                  _buildContextSection(
                    icon: Icons.eco,
                    title: 'المحصول',
                    content: '${state.context!.crop!.typeAr} - ${state.context!.crop!.growthStageAr ?? ""}',
                  ),
                ],

                // Soil info
                if (state.context!.hasSoilData) ...[
                  _buildContextSection(
                    icon: Icons.landscape,
                    title: 'التربة',
                    content: 'رطوبة: ${state.context!.soil!.moistureStatusAr}',
                  ),
                ],
              ] else ...[
                Center(
                  child: Column(
                    children: [
                      Icon(Icons.info_outline, size: 48, color: Colors.grey[400]),
                      const SizedBox(height: 16),
                      Text(
                        'لا توجد بيانات سياق متاحة',
                        style: TextStyle(color: Colors.grey[600]),
                      ),
                      const SizedBox(height: 8),
                      const Text(
                        'اختر حقلاً للحصول على توصيات مخصصة',
                        style: TextStyle(fontSize: 12),
                      ),
                    ],
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildContextSection({
    required IconData icon,
    required String title,
    required String content,
  }) {
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.grey[50],
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.grey[200]!),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: SahoolTheme.primary.withOpacity(0.1),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Icon(icon, color: SahoolTheme.primary),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    fontWeight: FontWeight.w600,
                    fontSize: 14,
                  ),
                ),
                Text(
                  content,
                  style: TextStyle(
                    color: Colors.grey[600],
                    fontSize: 13,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  void _handleMenuAction(String action) {
    switch (action) {
      case 'new_chat':
        ref.read(aiAdvisorProvider.notifier).startNewChat();
        break;
      case 'clear_history':
        _showClearHistoryDialog();
        break;
    }
  }

  void _showClearHistoryDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('مسح المحادثة'),
        content: const Text('هل تريد مسح جميع الرسائل في هذه المحادثة؟'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('إلغاء'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              ref.read(aiAdvisorProvider.notifier).clearChatHistory();
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.red,
            ),
            child: const Text('مسح'),
          ),
        ],
      ),
    );
  }

  void _scrollToBottom() {
    if (_scrollController.hasClients) {
      _scrollController.animateTo(
        0,
        duration: const Duration(milliseconds: 300),
        curve: Curves.easeOut,
      );
    }
  }
}
