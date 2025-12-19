/// SAHOOL Offline Queue
/// قائمة انتظار الأوامر بدون اتصال

import 'models.dart';

class OfflineQueue {
  final List<OfflineCommand> _commands = [];
  static const int maxRetries = 3;

  List<OfflineCommand> get pending => List.unmodifiable(_commands);
  int get length => _commands.length;
  bool get isEmpty => _commands.isEmpty;
  bool get isNotEmpty => _commands.isNotEmpty;

  void enqueue(OfflineCommand command) {
    _commands.add(command);
  }

  void remove(String id) {
    _commands.removeWhere((c) => c.id == id);
  }

  void incrementRetry(String id) {
    final index = _commands.indexWhere((c) => c.id == id);
    if (index != -1) {
      final cmd = _commands[index];
      if (cmd.retryCount >= maxRetries) {
        _commands.removeAt(index);
      } else {
        _commands[index] = cmd.copyWith(retryCount: cmd.retryCount + 1);
      }
    }
  }

  void clear() {
    _commands.clear();
  }

  OfflineCommand? peek() {
    return _commands.isNotEmpty ? _commands.first : null;
  }

  OfflineCommand? dequeue() {
    if (_commands.isEmpty) return null;
    return _commands.removeAt(0);
  }

  List<Map<String, dynamic>> toJson() {
    return _commands.map((c) => c.toJson()).toList();
  }

  void loadFromJson(List<dynamic> jsonList) {
    _commands.clear();
    for (final json in jsonList) {
      _commands.add(OfflineCommand.fromJson(Map<String, dynamic>.from(json)));
    }
  }
}
