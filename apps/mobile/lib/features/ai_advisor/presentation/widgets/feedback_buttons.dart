/// Feedback Buttons Widget
/// أزرار ردود الفعل
///
/// Allows users to provide feedback on AI advisories
library;

import 'package:flutter/material.dart';
import '../../domain/models/advisory.dart';
import '../../domain/models/advisory_feedback.dart';

class FeedbackButtons extends StatefulWidget {
  final String advisoryId;
  final AdvisoryFeedbackSummary? initialFeedback;
  final Function(AdvisoryFeedback) onFeedbackSubmitted;
  final bool showRating;
  final bool showOutcome;

  const FeedbackButtons({
    super.key,
    required this.advisoryId,
    this.initialFeedback,
    required this.onFeedbackSubmitted,
    this.showRating = true,
    this.showOutcome = false,
  });

  @override
  State<FeedbackButtons> createState() => _FeedbackButtonsState();
}

class _FeedbackButtonsState extends State<FeedbackButtons> {
  bool? _thumbsUp;
  int? _rating;
  bool _submitted = false;

  @override
  void initState() {
    super.initState();
    if (widget.initialFeedback != null) {
      _thumbsUp = widget.initialFeedback!.thumbsUp;
      _rating = widget.initialFeedback!.rating;
      _submitted = widget.initialFeedback!.rating != null ||
          widget.initialFeedback!.thumbsUp != null;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Thumbs up/down
        Row(
          children: [
            _buildThumbButton(true),
            const SizedBox(width: 8),
            _buildThumbButton(false),

            if (_submitted) ...[
              const Spacer(),
              Text(
                'شكراً لتقييمك!',
                style: TextStyle(
                  fontSize: 12,
                  color: Colors.grey[600],
                  fontStyle: FontStyle.italic,
                ),
              ),
            ],
          ],
        ),

        // Star rating (optional)
        if (widget.showRating && _thumbsUp != null) ...[
          const SizedBox(height: 16),
          _buildStarRating(),
        ],

        // Outcome feedback (optional)
        if (widget.showOutcome && _submitted) ...[
          const SizedBox(height: 16),
          _buildOutcomeSection(),
        ],
      ],
    );
  }

  Widget _buildThumbButton(bool isThumbsUp) {
    final isSelected = _thumbsUp == isThumbsUp;
    final color = isThumbsUp ? Colors.green : Colors.red;

    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: () => _submitThumbsFeedback(isThumbsUp),
        borderRadius: BorderRadius.circular(24),
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          decoration: BoxDecoration(
            color: isSelected ? color.withOpacity(0.1) : Colors.grey[100],
            borderRadius: BorderRadius.circular(24),
            border: Border.all(
              color: isSelected ? color.withOpacity(0.5) : Colors.grey[300]!,
              width: isSelected ? 2 : 1,
            ),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(
                isThumbsUp
                    ? (isSelected ? Icons.thumb_up : Icons.thumb_up_outlined)
                    : (isSelected ? Icons.thumb_down : Icons.thumb_down_outlined),
                size: 18,
                color: isSelected ? color : Colors.grey[600],
              ),
              const SizedBox(width: 6),
              Text(
                isThumbsUp ? 'مفيد' : 'غير مفيد',
                style: TextStyle(
                  fontSize: 13,
                  color: isSelected ? color : Colors.grey[700],
                  fontWeight: isSelected ? FontWeight.w600 : FontWeight.normal,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildStarRating() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'قيّم التوصية:',
          style: TextStyle(
            fontSize: 13,
            color: Colors.grey[700],
          ),
        ),
        const SizedBox(height: 8),
        Row(
          mainAxisSize: MainAxisSize.min,
          children: List.generate(5, (index) {
            final starNumber = index + 1;
            final isSelected = _rating != null && starNumber <= _rating!;

            return GestureDetector(
              onTap: () => _submitRatingFeedback(starNumber),
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 4),
                child: Icon(
                  isSelected ? Icons.star : Icons.star_outline,
                  size: 32,
                  color: isSelected ? Colors.amber : Colors.grey[400],
                ),
              ),
            );
          }),
        ),
        if (_rating != null)
          Padding(
            padding: const EdgeInsets.only(top: 8),
            child: Text(
              _getRatingText(_rating!),
              style: TextStyle(
                fontSize: 12,
                color: Colors.grey[600],
              ),
            ),
          ),
      ],
    );
  }

  Widget _buildOutcomeSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'هل نجحت التوصية؟',
          style: TextStyle(
            fontSize: 13,
            fontWeight: FontWeight.w600,
            color: Colors.grey[700],
          ),
        ),
        const SizedBox(height: 12),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: [
            _buildOutcomeChip(OutcomeStatus.success, 'نجحت', Colors.green),
            _buildOutcomeChip(OutcomeStatus.partialSuccess, 'نجاح جزئي', Colors.orange),
            _buildOutcomeChip(OutcomeStatus.failure, 'لم تنجح', Colors.red),
            _buildOutcomeChip(OutcomeStatus.notApplicable, 'لم أطبقها', Colors.grey),
          ],
        ),
      ],
    );
  }

  Widget _buildOutcomeChip(OutcomeStatus status, String label, Color color) {
    return ActionChip(
      label: Text(label),
      labelStyle: TextStyle(
        fontSize: 12,
        color: color,
      ),
      backgroundColor: color.withOpacity(0.1),
      side: BorderSide(color: color.withOpacity(0.3)),
      onPressed: () => _submitOutcomeFeedback(status),
    );
  }

  void _submitThumbsFeedback(bool isThumbsUp) {
    setState(() {
      _thumbsUp = isThumbsUp;
      _submitted = true;
    });

    final feedback = AdvisoryFeedback.thumbs(
      advisoryId: widget.advisoryId,
      userId: '', // Will be filled by repository
      thumbsUp: isThumbsUp,
    );

    widget.onFeedbackSubmitted(feedback);
  }

  void _submitRatingFeedback(int rating) {
    setState(() {
      _rating = rating;
    });

    final feedback = AdvisoryFeedback.rating(
      advisoryId: widget.advisoryId,
      userId: '', // Will be filled by repository
      rating: rating,
    );

    widget.onFeedbackSubmitted(feedback);
  }

  void _submitOutcomeFeedback(OutcomeStatus outcome) {
    final feedback = AdvisoryFeedback.outcome(
      advisoryId: widget.advisoryId,
      userId: '', // Will be filled by repository
      outcome: outcome,
    );

    widget.onFeedbackSubmitted(feedback);
  }

  String _getRatingText(int rating) {
    switch (rating) {
      case 1:
        return 'غير مفيدة على الإطلاق';
      case 2:
        return 'قليلة الفائدة';
      case 3:
        return 'مفيدة إلى حد ما';
      case 4:
        return 'مفيدة جداً';
      case 5:
        return 'ممتازة!';
      default:
        return '';
    }
  }
}

/// Simple thumbs feedback widget for chat bubbles
class QuickFeedback extends StatefulWidget {
  final String messageId;
  final Function(bool isPositive)? onFeedback;

  const QuickFeedback({
    super.key,
    required this.messageId,
    this.onFeedback,
  });

  @override
  State<QuickFeedback> createState() => _QuickFeedbackState();
}

class _QuickFeedbackState extends State<QuickFeedback> {
  bool? _selectedFeedback;

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        _buildIconButton(
          icon: _selectedFeedback == true
              ? Icons.thumb_up
              : Icons.thumb_up_outlined,
          isSelected: _selectedFeedback == true,
          isPositive: true,
        ),
        const SizedBox(width: 4),
        _buildIconButton(
          icon: _selectedFeedback == false
              ? Icons.thumb_down
              : Icons.thumb_down_outlined,
          isSelected: _selectedFeedback == false,
          isPositive: false,
        ),
      ],
    );
  }

  Widget _buildIconButton({
    required IconData icon,
    required bool isSelected,
    required bool isPositive,
  }) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: () {
          setState(() {
            _selectedFeedback = isPositive;
          });
          widget.onFeedback?.call(isPositive);
        },
        borderRadius: BorderRadius.circular(16),
        child: Container(
          padding: const EdgeInsets.all(6),
          decoration: BoxDecoration(
            color: isSelected
                ? (isPositive ? Colors.green : Colors.red).withOpacity(0.1)
                : Colors.grey[200],
            borderRadius: BorderRadius.circular(16),
          ),
          child: Icon(
            icon,
            size: 14,
            color: isSelected
                ? (isPositive ? Colors.green : Colors.red)
                : Colors.grey[600],
          ),
        ),
      ),
    );
  }
}

/// Feedback summary display widget
class FeedbackSummaryWidget extends StatelessWidget {
  final AdvisoryFeedbackSummary feedback;

  const FeedbackSummaryWidget({
    super.key,
    required this.feedback,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.grey[50],
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        children: [
          if (feedback.rating != null)
            _buildRatingDisplay(feedback.rating!),
          if (feedback.thumbsUp != null && feedback.rating == null)
            _buildThumbsDisplay(feedback.thumbsUp!),
          if (feedback.comment != null) ...[
            const SizedBox(width: 12),
            Expanded(
              child: Text(
                feedback.comment!,
                style: TextStyle(
                  fontSize: 12,
                  color: Colors.grey[600],
                  fontStyle: FontStyle.italic,
                ),
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildRatingDisplay(int rating) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: List.generate(5, (index) {
        return Icon(
          index < rating ? Icons.star : Icons.star_outline,
          size: 16,
          color: index < rating ? Colors.amber : Colors.grey[300],
        );
      }),
    );
  }

  Widget _buildThumbsDisplay(bool thumbsUp) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(
          thumbsUp ? Icons.thumb_up : Icons.thumb_down,
          size: 16,
          color: thumbsUp ? Colors.green : Colors.red,
        ),
        const SizedBox(width: 4),
        Text(
          thumbsUp ? 'مفيد' : 'غير مفيد',
          style: TextStyle(
            fontSize: 12,
            color: thumbsUp ? Colors.green : Colors.red,
            fontWeight: FontWeight.w500,
          ),
        ),
      ],
    );
  }
}
