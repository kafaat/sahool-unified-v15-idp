/// Advisory Feedback Model
/// نموذج ردود الفعل على التوصية
///
/// Represents user feedback on AI advisories
library;

import 'package:flutter/foundation.dart';

/// Feedback type enum
/// نوع ردود الفعل
enum FeedbackType {
  rating,     // تقييم بالنجوم
  thumbs,     // إعجاب/عدم إعجاب
  outcome,    // نتيجة التطبيق
  correction, // تصحيح
}

/// Outcome status enum
/// حالة النتيجة
enum OutcomeStatus {
  success,        // نجاح
  partialSuccess, // نجاح جزئي
  failure,        // فشل
  notApplicable,  // غير قابل للتطبيق
  pending,        // قيد الانتظار
}

/// Advisory Feedback Model
/// نموذج ردود الفعل
@immutable
class AdvisoryFeedback {
  /// Unique feedback ID
  final String id;

  /// Advisory ID this feedback is for
  final String advisoryId;

  /// User ID who provided feedback
  final String userId;

  /// Feedback type
  final FeedbackType type;

  /// Rating (1-5 stars)
  final int? rating;

  /// Thumbs up/down
  final bool? thumbsUp;

  /// Outcome status
  final OutcomeStatus? outcome;

  /// Yield impact percentage (positive or negative)
  final double? yieldImpact;

  /// Cost impact in local currency
  final double? costImpact;

  /// User comment in any language
  final String? comment;

  /// User comment in Arabic
  final String? commentAr;

  /// Correction text (if user provides correct answer)
  final String? correction;

  /// Correction in Arabic
  final String? correctionAr;

  /// Outcome details
  final String? outcomeDetails;

  /// Outcome details in Arabic
  final String? outcomeDetailsAr;

  /// Tags for categorization
  final List<String>? tags;

  /// Timestamp
  final DateTime createdAt;

  /// Additional metadata
  final Map<String, dynamic>? metadata;

  const AdvisoryFeedback({
    required this.id,
    required this.advisoryId,
    required this.userId,
    required this.type,
    this.rating,
    this.thumbsUp,
    this.outcome,
    this.yieldImpact,
    this.costImpact,
    this.comment,
    this.commentAr,
    this.correction,
    this.correctionAr,
    this.outcomeDetails,
    this.outcomeDetailsAr,
    this.tags,
    required this.createdAt,
    this.metadata,
  });

  /// Create rating feedback
  factory AdvisoryFeedback.rating({
    required String advisoryId,
    required String userId,
    required int rating,
    String? comment,
    String? commentAr,
  }) {
    assert(rating >= 1 && rating <= 5, 'Rating must be between 1 and 5');
    return AdvisoryFeedback(
      id: 'fb_${DateTime.now().millisecondsSinceEpoch}',
      advisoryId: advisoryId,
      userId: userId,
      type: FeedbackType.rating,
      rating: rating,
      comment: comment,
      commentAr: commentAr,
      createdAt: DateTime.now(),
    );
  }

  /// Create thumbs up/down feedback
  factory AdvisoryFeedback.thumbs({
    required String advisoryId,
    required String userId,
    required bool thumbsUp,
    String? comment,
    String? commentAr,
  }) {
    return AdvisoryFeedback(
      id: 'fb_${DateTime.now().millisecondsSinceEpoch}',
      advisoryId: advisoryId,
      userId: userId,
      type: FeedbackType.thumbs,
      thumbsUp: thumbsUp,
      comment: comment,
      commentAr: commentAr,
      createdAt: DateTime.now(),
    );
  }

  /// Create outcome feedback
  factory AdvisoryFeedback.outcome({
    required String advisoryId,
    required String userId,
    required OutcomeStatus outcome,
    double? yieldImpact,
    double? costImpact,
    String? outcomeDetails,
    String? outcomeDetailsAr,
  }) {
    return AdvisoryFeedback(
      id: 'fb_${DateTime.now().millisecondsSinceEpoch}',
      advisoryId: advisoryId,
      userId: userId,
      type: FeedbackType.outcome,
      outcome: outcome,
      yieldImpact: yieldImpact,
      costImpact: costImpact,
      outcomeDetails: outcomeDetails,
      outcomeDetailsAr: outcomeDetailsAr,
      createdAt: DateTime.now(),
    );
  }

  /// Create correction feedback
  factory AdvisoryFeedback.correction({
    required String advisoryId,
    required String userId,
    required String correction,
    String? correctionAr,
  }) {
    return AdvisoryFeedback(
      id: 'fb_${DateTime.now().millisecondsSinceEpoch}',
      advisoryId: advisoryId,
      userId: userId,
      type: FeedbackType.correction,
      correction: correction,
      correctionAr: correctionAr,
      createdAt: DateTime.now(),
    );
  }

  /// Create from JSON
  factory AdvisoryFeedback.fromJson(Map<String, dynamic> json) {
    return AdvisoryFeedback(
      id: json['id'] as String? ?? '',
      advisoryId: json['advisory_id'] as String? ?? '',
      userId: json['user_id'] as String? ?? '',
      type: _parseFeedbackType(json['type'] as String?),
      rating: json['rating'] as int?,
      thumbsUp: json['thumbs_up'] as bool?,
      outcome: json['outcome'] != null
          ? _parseOutcomeStatus(json['outcome'] as String)
          : null,
      yieldImpact: (json['yield_impact'] as num?)?.toDouble(),
      costImpact: (json['cost_impact'] as num?)?.toDouble(),
      comment: json['comment'] as String?,
      commentAr: json['comment_ar'] as String?,
      correction: json['correction'] as String?,
      correctionAr: json['correction_ar'] as String?,
      outcomeDetails: json['outcome_details'] as String?,
      outcomeDetailsAr: json['outcome_details_ar'] as String?,
      tags: (json['tags'] as List?)?.cast<String>(),
      createdAt: json['created_at'] != null
          ? DateTime.tryParse(json['created_at'] as String) ?? DateTime.now()
          : DateTime.now(),
      metadata: json['metadata'] as Map<String, dynamic>?,
    );
  }

  /// Convert to JSON
  Map<String, dynamic> toJson() => {
    'id': id,
    'advisory_id': advisoryId,
    'user_id': userId,
    'type': type.name,
    'rating': rating,
    'thumbs_up': thumbsUp,
    'outcome': outcome?.name,
    'yield_impact': yieldImpact,
    'cost_impact': costImpact,
    'comment': comment,
    'comment_ar': commentAr,
    'correction': correction,
    'correction_ar': correctionAr,
    'outcome_details': outcomeDetails,
    'outcome_details_ar': outcomeDetailsAr,
    'tags': tags,
    'created_at': createdAt.toIso8601String(),
    'metadata': metadata,
  };

  /// Copy with
  AdvisoryFeedback copyWith({
    String? id,
    String? advisoryId,
    String? userId,
    FeedbackType? type,
    int? rating,
    bool? thumbsUp,
    OutcomeStatus? outcome,
    double? yieldImpact,
    double? costImpact,
    String? comment,
    String? commentAr,
    String? correction,
    String? correctionAr,
    String? outcomeDetails,
    String? outcomeDetailsAr,
    List<String>? tags,
    DateTime? createdAt,
    Map<String, dynamic>? metadata,
  }) {
    return AdvisoryFeedback(
      id: id ?? this.id,
      advisoryId: advisoryId ?? this.advisoryId,
      userId: userId ?? this.userId,
      type: type ?? this.type,
      rating: rating ?? this.rating,
      thumbsUp: thumbsUp ?? this.thumbsUp,
      outcome: outcome ?? this.outcome,
      yieldImpact: yieldImpact ?? this.yieldImpact,
      costImpact: costImpact ?? this.costImpact,
      comment: comment ?? this.comment,
      commentAr: commentAr ?? this.commentAr,
      correction: correction ?? this.correction,
      correctionAr: correctionAr ?? this.correctionAr,
      outcomeDetails: outcomeDetails ?? this.outcomeDetails,
      outcomeDetailsAr: outcomeDetailsAr ?? this.outcomeDetailsAr,
      tags: tags ?? this.tags,
      createdAt: createdAt ?? this.createdAt,
      metadata: metadata ?? this.metadata,
    );
  }

  /// Get feedback type label in Arabic
  String get typeAr {
    switch (type) {
      case FeedbackType.rating:
        return 'تقييم';
      case FeedbackType.thumbs:
        return 'إعجاب';
      case FeedbackType.outcome:
        return 'نتيجة';
      case FeedbackType.correction:
        return 'تصحيح';
    }
  }

  /// Get outcome status label in Arabic
  String? get outcomeAr {
    if (outcome == null) return null;
    switch (outcome!) {
      case OutcomeStatus.success:
        return 'نجاح';
      case OutcomeStatus.partialSuccess:
        return 'نجاح جزئي';
      case OutcomeStatus.failure:
        return 'فشل';
      case OutcomeStatus.notApplicable:
        return 'غير قابل للتطبيق';
      case OutcomeStatus.pending:
        return 'قيد الانتظار';
    }
  }

  /// Check if feedback is positive
  bool get isPositive {
    if (rating != null) return rating! >= 4;
    if (thumbsUp != null) return thumbsUp!;
    if (outcome != null) {
      return outcome == OutcomeStatus.success ||
          outcome == OutcomeStatus.partialSuccess;
    }
    return false;
  }

  /// Get sentiment score (-1 to 1)
  double get sentimentScore {
    if (rating != null) {
      return (rating! - 3) / 2; // Maps 1-5 to -1 to 1
    }
    if (thumbsUp != null) {
      return thumbsUp! ? 1.0 : -1.0;
    }
    if (outcome != null) {
      switch (outcome!) {
        case OutcomeStatus.success:
          return 1.0;
        case OutcomeStatus.partialSuccess:
          return 0.5;
        case OutcomeStatus.failure:
          return -1.0;
        case OutcomeStatus.notApplicable:
        case OutcomeStatus.pending:
          return 0.0;
      }
    }
    return 0.0;
  }

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is AdvisoryFeedback && runtimeType == other.runtimeType && id == other.id;

  @override
  int get hashCode => id.hashCode;

  @override
  String toString() => 'AdvisoryFeedback($id: $type for $advisoryId)';
}

/// Feedback Summary for aggregated statistics
/// ملخص إحصائيات ردود الفعل
@immutable
class FeedbackSummary {
  /// Total feedback count
  final int totalFeedback;

  /// Average rating (1-5)
  final double averageRating;

  /// Rating count
  final int ratingCount;

  /// Thumbs up count
  final int thumbsUpCount;

  /// Thumbs down count
  final int thumbsDownCount;

  /// Success rate (percentage)
  final double successRate;

  /// Outcome counts by status
  final Map<OutcomeStatus, int> outcomeCounts;

  /// Feedback by type
  final Map<FeedbackType, int> feedbackByType;

  const FeedbackSummary({
    required this.totalFeedback,
    required this.averageRating,
    required this.ratingCount,
    required this.thumbsUpCount,
    required this.thumbsDownCount,
    required this.successRate,
    required this.outcomeCounts,
    required this.feedbackByType,
  });

  factory FeedbackSummary.fromJson(Map<String, dynamic> json) {
    return FeedbackSummary(
      totalFeedback: json['total_feedback'] as int? ?? 0,
      averageRating: (json['average_rating'] as num?)?.toDouble() ?? 0.0,
      ratingCount: json['rating_count'] as int? ?? 0,
      thumbsUpCount: json['thumbs_up_count'] as int? ?? 0,
      thumbsDownCount: json['thumbs_down_count'] as int? ?? 0,
      successRate: (json['success_rate'] as num?)?.toDouble() ?? 0.0,
      outcomeCounts: _parseOutcomeCounts(json['outcome_counts']),
      feedbackByType: _parseFeedbackByType(json['feedback_by_type']),
    );
  }

  Map<String, dynamic> toJson() => {
    'total_feedback': totalFeedback,
    'average_rating': averageRating,
    'rating_count': ratingCount,
    'thumbs_up_count': thumbsUpCount,
    'thumbs_down_count': thumbsDownCount,
    'success_rate': successRate,
    'outcome_counts': outcomeCounts.map((k, v) => MapEntry(k.name, v)),
    'feedback_by_type': feedbackByType.map((k, v) => MapEntry(k.name, v)),
  };

  /// Get thumbs up percentage
  double get thumbsUpPercentage {
    final total = thumbsUpCount + thumbsDownCount;
    if (total == 0) return 0.0;
    return (thumbsUpCount / total) * 100;
  }

  /// Get rating stars display
  String get ratingStars {
    final fullStars = averageRating.floor();
    final hasHalfStar = (averageRating - fullStars) >= 0.5;
    final emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0);

    return '${'*' * fullStars}${hasHalfStar ? '+' : ''}${'-' * emptyStars}';
  }

  /// Create empty summary
  factory FeedbackSummary.empty() {
    return const FeedbackSummary(
      totalFeedback: 0,
      averageRating: 0.0,
      ratingCount: 0,
      thumbsUpCount: 0,
      thumbsDownCount: 0,
      successRate: 0.0,
      outcomeCounts: {},
      feedbackByType: {},
    );
  }
}

// Helper functions

FeedbackType _parseFeedbackType(String? type) {
  switch (type?.toLowerCase()) {
    case 'rating':
      return FeedbackType.rating;
    case 'thumbs':
      return FeedbackType.thumbs;
    case 'outcome':
      return FeedbackType.outcome;
    case 'correction':
      return FeedbackType.correction;
    default:
      return FeedbackType.rating;
  }
}

OutcomeStatus _parseOutcomeStatus(String status) {
  switch (status.toLowerCase()) {
    case 'success':
      return OutcomeStatus.success;
    case 'partial_success':
    case 'partialsuccess':
      return OutcomeStatus.partialSuccess;
    case 'failure':
      return OutcomeStatus.failure;
    case 'not_applicable':
    case 'notapplicable':
      return OutcomeStatus.notApplicable;
    case 'pending':
    default:
      return OutcomeStatus.pending;
  }
}

Map<OutcomeStatus, int> _parseOutcomeCounts(dynamic data) {
  if (data == null || data is! Map) return {};

  final result = <OutcomeStatus, int>{};
  for (final entry in (data).entries) {
    try {
      final status = _parseOutcomeStatus(entry.key.toString());
      result[status] = entry.value as int? ?? 0;
    } catch (e) {
      // Skip invalid entries
    }
  }
  return result;
}

Map<FeedbackType, int> _parseFeedbackByType(dynamic data) {
  if (data == null || data is! Map) return {};

  final result = <FeedbackType, int>{};
  for (final entry in (data).entries) {
    try {
      final type = _parseFeedbackType(entry.key.toString());
      result[type] = entry.value as int? ?? 0;
    } catch (e) {
      // Skip invalid entries
    }
  }
  return result;
}
