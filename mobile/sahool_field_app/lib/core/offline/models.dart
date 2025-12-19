/// SAHOOL Offline Command Models
/// نماذج الأوامر للعمل بدون اتصال

class OfflineCommand {
  final String id;
  final String type;
  final Map<String, dynamic> payload;
  final DateTime createdAt;
  final int retryCount;

  OfflineCommand({
    required this.id,
    required this.type,
    required this.payload,
    required this.createdAt,
    this.retryCount = 0,
  });

  OfflineCommand copyWith({int? retryCount}) {
    return OfflineCommand(
      id: id,
      type: type,
      payload: payload,
      createdAt: createdAt,
      retryCount: retryCount ?? this.retryCount,
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'type': type,
        'payload': payload,
        'createdAt': createdAt.toIso8601String(),
        'retryCount': retryCount,
      };

  factory OfflineCommand.fromJson(Map<String, dynamic> json) {
    return OfflineCommand(
      id: json['id'],
      type: json['type'],
      payload: Map<String, dynamic>.from(json['payload']),
      createdAt: DateTime.parse(json['createdAt']),
      retryCount: json['retryCount'] ?? 0,
    );
  }

  @override
  String toString() {
    return 'OfflineCommand(id: $id, type: $type, retryCount: $retryCount)';
  }
}

/// نتيجة المزامنة
class SyncResult {
  final int synced;
  final int failed;
  final int remaining;

  SyncResult({
    required this.synced,
    required this.failed,
    required this.remaining,
  });

  bool get hasFailures => failed > 0;
  bool get isComplete => remaining == 0;

  @override
  String toString() {
    return 'SyncResult(synced: $synced, failed: $failed, remaining: $remaining)';
  }
}
