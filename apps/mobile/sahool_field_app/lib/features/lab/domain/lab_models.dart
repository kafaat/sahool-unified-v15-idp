/// Lab domain models
/// نماذج مجال المختبر

enum SampleStatus {
  pending,
  inTransit,
  received,
  processing,
  analyzed,
}

class LabSample {
  final String id;
  final String barcode;
  final String type;
  final SampleStatus status;
  final String experimentName;
  final String plotCode;
  final DateTime collectedAt;
  final String collectedBy;
  final Map<String, dynamic>? results;

  LabSample({
    required this.id,
    required this.barcode,
    required this.type,
    required this.status,
    required this.experimentName,
    required this.plotCode,
    required this.collectedAt,
    required this.collectedBy,
    this.results,
  });

  factory LabSample.fromJson(Map<String, dynamic> json) {
    return LabSample(
      id: json['id'] as String,
      barcode: json['barcode'] as String? ?? '',
      type: json['type'] as String? ?? '',
      status: _parseStatus(json['status'] as String?),
      experimentName: json['experimentName'] as String? ?? '',
      plotCode: json['plotCode'] as String? ?? '',
      collectedAt: json['collectedAt'] != null
          ? DateTime.parse(json['collectedAt'] as String)
          : DateTime.now(),
      collectedBy: json['collectedBy'] as String? ?? '',
      results: json['results'] as Map<String, dynamic>?,
    );
  }

  static SampleStatus _parseStatus(String? status) {
    switch (status?.toLowerCase()) {
      case 'intransit':
      case 'in_transit':
        return SampleStatus.inTransit;
      case 'received':
        return SampleStatus.received;
      case 'processing':
        return SampleStatus.processing;
      case 'analyzed':
        return SampleStatus.analyzed;
      default:
        return SampleStatus.pending;
    }
  }
}
