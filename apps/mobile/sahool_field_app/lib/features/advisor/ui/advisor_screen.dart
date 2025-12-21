import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../core/theme/sahool_theme.dart';

/// AI Advisor Chat Screen - المستشار الذكي
/// واجهة محادثة بسيطة مع دعم الصوت والكاميرا
class AdvisorScreen extends StatefulWidget {
  const AdvisorScreen({super.key});

  @override
  State<AdvisorScreen> createState() => _AdvisorScreenState();
}

class _AdvisorScreenState extends State<AdvisorScreen> {
  final _messageController = TextEditingController();
  final _scrollController = ScrollController();
  bool _isRecording = false;
  bool _isTyping = false;

  final List<_ChatMessage> _messages = [
    _ChatMessage(
      text: 'مرحباً! أنا المستشار الزراعي الذكي.\nكيف يمكنني مساعدتك اليوم؟',
      isUser: false,
      time: DateTime.now().subtract(const Duration(minutes: 5)),
    ),
  ];

  @override
  void dispose() {
    _messageController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  void _sendMessage(String text) {
    if (text.trim().isEmpty) return;

    setState(() {
      _messages.add(_ChatMessage(
        text: text,
        isUser: true,
        time: DateTime.now(),
      ));
      _messageController.clear();
      _isTyping = true;
    });

    _scrollToBottom();

    // Simulate AI response
    Future.delayed(const Duration(seconds: 2), () {
      if (mounted) {
        setState(() {
          _isTyping = false;
          _messages.add(_ChatMessage(
            text: _generateResponse(text),
            isUser: false,
            time: DateTime.now(),
            hasAction: text.contains('آفة') || text.contains('مرض'),
          ));
        });
        _scrollToBottom();
      }
    });
  }

  String _generateResponse(String query) {
    if (query.contains('ري') || query.contains('مياه')) {
      return 'بناءً على بيانات رطوبة التربة الحالية (35%) وتوقعات الطقس، أنصح بالري غداً صباحاً لمدة ساعتين.\n\nدرجة الحرارة المتوقعة: 28°C\nنسبة الرطوبة: 45%';
    }
    if (query.contains('سماد') || query.contains('تسميد')) {
      return 'يحتاج حقل القمح إلى تسميد نيتروجيني. أنصح بإضافة:\n\n• يوريا: 50 كجم/هكتار\n• الوقت الأفضل: الصباح الباكر\n\nهل تريد إضافة هذه المهمة إلى قائمتك؟';
    }
    if (query.contains('آفة') || query.contains('مرض') || query.contains('حشرة')) {
      return '🔬 بناءً على وصفك، قد يكون هذا:\n\n**صدأ القمح**\nالاحتمالية: 85%\n\n**العلاج المقترح:**\n• رش مبيد فطري (مانكوزيب)\n• الجرعة: 2.5 كجم/هكتار\n\n⚠️ يُنصح بالتصوير للتأكد';
    }
    return 'شكراً لسؤالك. يمكنني مساعدتك في:\n\n• توصيات الري والتسميد\n• تشخيص الآفات والأمراض\n• متابعة صحة المحاصيل\n\nما الذي تحتاج مساعدة فيه؟';
  }

  void _scrollToBottom() {
    Future.delayed(const Duration(milliseconds: 100), () {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: SahoolColors.background,
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.pop(),
        ),
        title: Row(
          children: [
            Container(
              width: 40,
              height: 40,
              decoration: BoxDecoration(
                gradient: SahoolColors.primaryGradient,
                shape: BoxShape.circle,
              ),
              child: const Icon(Icons.psychology, color: Colors.white, size: 24),
            ),
            const SizedBox(width: 12),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text('المستشار الذكي', style: TextStyle(fontSize: 16)),
                Text(
                  _isTyping ? 'يكتب...' : 'متصل',
                  style: TextStyle(
                    fontSize: 12,
                    color: _isTyping ? Colors.orange : SahoolColors.success,
                  ),
                ),
              ],
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.camera_alt),
            onPressed: () => context.push('/scanner'),
            tooltip: 'تصوير',
          ),
        ],
      ),
      body: Column(
        children: [
          // Quick suggestions
          _buildQuickSuggestions(),

          // Messages
          Expanded(
            child: ListView.builder(
              controller: _scrollController,
              padding: const EdgeInsets.all(16),
              itemCount: _messages.length + (_isTyping ? 1 : 0),
              itemBuilder: (context, index) {
                if (_isTyping && index == _messages.length) {
                  return _buildTypingIndicator();
                }
                return _ChatBubble(message: _messages[index]);
              },
            ),
          ),

          // Input
          _buildInputArea(),
        ],
      ),
    );
  }

  Widget _buildQuickSuggestions() {
    final suggestions = [
      'متى أروي الحقل؟',
      'الحقل يحتاج تسميد؟',
      'رأيت آفة غريبة',
    ];

    return Container(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: SingleChildScrollView(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 16),
        child: Row(
          children: suggestions.map((suggestion) {
            return Padding(
              padding: const EdgeInsets.only(left: 8),
              child: ActionChip(
                label: Text(suggestion),
                onPressed: () => _sendMessage(suggestion),
                backgroundColor: Colors.white,
                side: BorderSide(color: SahoolColors.primary.withOpacity(0.3)),
              ),
            );
          }).toList(),
        ),
      ),
    );
  }

  Widget _buildTypingIndicator() {
    return Align(
      alignment: Alignment.centerRight,
      child: Container(
        margin: const EdgeInsets.only(bottom: 8),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(20),
          boxShadow: SahoolShadows.small,
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            _buildDot(0),
            const SizedBox(width: 4),
            _buildDot(1),
            const SizedBox(width: 4),
            _buildDot(2),
          ],
        ),
      ),
    );
  }

  Widget _buildDot(int index) {
    return TweenAnimationBuilder<double>(
      tween: Tween(begin: 0, end: 1),
      duration: Duration(milliseconds: 600 + (index * 200)),
      builder: (context, value, child) {
        return Container(
          width: 8,
          height: 8,
          decoration: BoxDecoration(
            color: SahoolColors.primary.withOpacity(0.3 + (value * 0.7)),
            shape: BoxShape.circle,
          ),
        );
      },
    );
  }

  Widget _buildInputArea() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, -5),
          ),
        ],
      ),
      child: SafeArea(
        child: Row(
          children: [
            // Voice button
            GestureDetector(
              onLongPressStart: (_) => setState(() => _isRecording = true),
              onLongPressEnd: (_) {
                setState(() => _isRecording = false);
                _sendMessage('🎤 رسالة صوتية');
              },
              child: AnimatedContainer(
                duration: const Duration(milliseconds: 200),
                width: 48,
                height: 48,
                decoration: BoxDecoration(
                  color: _isRecording ? SahoolColors.danger : SahoolColors.primary.withOpacity(0.1),
                  shape: BoxShape.circle,
                ),
                child: Icon(
                  Icons.mic,
                  color: _isRecording ? Colors.white : SahoolColors.primary,
                ),
              ),
            ),
            const SizedBox(width: 12),
            // Text input
            Expanded(
              child: TextField(
                controller: _messageController,
                decoration: InputDecoration(
                  hintText: 'اكتب رسالتك...',
                  filled: true,
                  fillColor: Colors.grey[100],
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(24),
                    borderSide: BorderSide.none,
                  ),
                  contentPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
                ),
                onSubmitted: _sendMessage,
              ),
            ),
            const SizedBox(width: 12),
            // Send button
            Container(
              width: 48,
              height: 48,
              decoration: BoxDecoration(
                gradient: SahoolColors.primaryGradient,
                shape: BoxShape.circle,
                boxShadow: SahoolShadows.colored(SahoolColors.primary),
              ),
              child: IconButton(
                icon: const Icon(Icons.send, color: Colors.white),
                onPressed: () => _sendMessage(_messageController.text),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _ChatMessage {
  final String text;
  final bool isUser;
  final DateTime time;
  final bool hasAction;

  _ChatMessage({
    required this.text,
    required this.isUser,
    required this.time,
    this.hasAction = false,
  });
}

class _ChatBubble extends StatelessWidget {
  final _ChatMessage message;

  const _ChatBubble({required this.message});

  @override
  Widget build(BuildContext context) {
    return Align(
      alignment: message.isUser ? Alignment.centerLeft : Alignment.centerRight,
      child: Container(
        margin: const EdgeInsets.only(bottom: 12),
        constraints: BoxConstraints(
          maxWidth: MediaQuery.of(context).size.width * 0.75,
        ),
        child: Column(
          crossAxisAlignment: message.isUser ? CrossAxisAlignment.start : CrossAxisAlignment.end,
          children: [
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: message.isUser ? SahoolColors.primary : Colors.white,
                borderRadius: BorderRadius.only(
                  topLeft: const Radius.circular(20),
                  topRight: const Radius.circular(20),
                  bottomLeft: Radius.circular(message.isUser ? 4 : 20),
                  bottomRight: Radius.circular(message.isUser ? 20 : 4),
                ),
                boxShadow: SahoolShadows.small,
              ),
              child: Text(
                message.text,
                style: TextStyle(
                  color: message.isUser ? Colors.white : SahoolColors.textDark,
                  fontSize: 15,
                ),
              ),
            ),
            if (message.hasAction) ...[
              const SizedBox(height: 8),
              OutlinedButton.icon(
                onPressed: () {},
                icon: const Icon(Icons.add_task, size: 18),
                label: const Text('إضافة كمهمة'),
                style: OutlinedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                ),
              ),
            ],
            const SizedBox(height: 4),
            Text(
              _formatTime(message.time),
              style: TextStyle(
                color: Colors.grey[400],
                fontSize: 11,
              ),
            ),
          ],
        ),
      ),
    );
  }

  String _formatTime(DateTime time) {
    return '${time.hour}:${time.minute.toString().padLeft(2, '0')}';
  }
}
