/// Community Post Card Widget
/// بطاقة منشور المجتمع
///
/// Displays a community post with author info, content,
/// optional image grid, and like/comment/share action bar.
library;

import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter/material.dart';
import '../../../../core/theme/sahool_theme.dart';
import '../../../../core/theme/organic_widgets.dart';
import '../providers/community_provider.dart';

/// Post card with author info, text content, image grid,
/// and like/comment/share action bar
/// بطاقة المنشور مع معلومات المؤلف والمحتوى والتفاعلات
class PostCard extends StatelessWidget {
  final CommunityPost post;
  final VoidCallback? onTap;
  final VoidCallback? onLike;
  final VoidCallback? onComment;
  final VoidCallback? onShare;

  const PostCard({
    super.key,
    required this.post,
    this.onTap,
    this.onLike,
    this.onComment,
    this.onShare,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: OrganicCard(
        color: post.isExpertPost
            ? SahoolColors.forestGreen.withOpacity(0.05)
            : null,
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildHeader(context),
            const SizedBox(height: 12),
            _buildContent(),
            if (post.imageUrls.isNotEmpty) ...[
              const SizedBox(height: 12),
              _buildImageGrid(),
            ],
            const Divider(height: 24),
            _buildActionBar(),
          ],
        ),
      ),
    );
  }

  /// Author header with avatar, name, role, and time ago
  /// رأس المؤلف مع الصورة والاسم والدور والوقت
  Widget _buildHeader(BuildContext context) {
    return Row(
      children: [
        CircleAvatar(
          radius: 22,
          backgroundColor: SahoolColors.paleOlive,
          backgroundImage: post.authorAvatarUrl != null
              ? CachedNetworkImageProvider(post.authorAvatarUrl!)
              : null,
          child: post.authorAvatarUrl == null
              ? const Icon(Icons.person, color: SahoolColors.forestGreen)
              : null,
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Flexible(
                    child: Text(
                      post.authorName,
                      style: const TextStyle(fontWeight: FontWeight.bold),
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  if (post.isExpertPost) ...[
                    const SizedBox(width: 4),
                    const Icon(Icons.verified, size: 16, color: Colors.blue),
                  ],
                ],
              ),
              Text(
                '${post.authorRoleAr} - ${_formatTimeAgo(post.createdAt)}',
                style: const TextStyle(fontSize: 11, color: Colors.grey),
              ),
            ],
          ),
        ),
        if (post.hasExpertReply) _buildExpertBadge(),
        PopupMenuButton<String>(
          icon: const Icon(Icons.more_vert, color: Colors.grey),
          itemBuilder: (context) => const [
            PopupMenuItem(value: 'save', child: Text('حفظ')),
            PopupMenuItem(value: 'report', child: Text('ابلاغ')),
            PopupMenuItem(value: 'share', child: Text('مشاركة')),
          ],
        ),
      ],
    );
  }

  /// Expert reply badge
  /// شارة رد الخبير
  Widget _buildExpertBadge() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: SahoolColors.forestGreen.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
      ),
      child: const Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(Icons.check_circle, size: 12, color: SahoolColors.forestGreen),
          SizedBox(width: 4),
          Text(
            'مجاب',
            style: TextStyle(
              fontSize: 10,
              color: SahoolColors.forestGreen,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }

  /// Post title and content text
  /// عنوان ومحتوى المنشور
  Widget _buildContent() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          post.title,
          style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
        ),
        const SizedBox(height: 6),
        Text(
          post.content,
          style: TextStyle(color: Colors.grey[800], height: 1.5),
          maxLines: 5,
          overflow: TextOverflow.ellipsis,
        ),
      ],
    );
  }

  /// Image grid for post attachments
  /// شبكة الصور للمرفقات
  Widget _buildImageGrid() {
    return Container(
      height: 180,
      decoration: BoxDecoration(
        color: SahoolColors.paleOlive,
        borderRadius: BorderRadius.circular(16),
      ),
      child: const Center(
        child: Icon(
          Icons.image,
          size: 48,
          color: SahoolColors.sageGreen,
        ),
      ),
    );
  }

  /// Like, comment, share, and save action bar
  /// شريط التفاعل: اعجاب، تعليق، مشاركة، حفظ
  Widget _buildActionBar() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceAround,
      children: [
        _ActionButton(
          icon: post.isLikedByMe
              ? Icons.thumb_up_alt
              : Icons.thumb_up_alt_outlined,
          label: '${post.likesCount}',
          isActive: post.isLikedByMe,
          onTap: onLike ?? () {},
        ),
        _ActionButton(
          icon: Icons.chat_bubble_outline,
          label: '${post.commentsCount}',
          onTap: onComment ?? () {},
        ),
        _ActionButton(
          icon: Icons.share_outlined,
          label: 'Share | مشاركة',
          onTap: onShare ?? () {},
        ),
        _ActionButton(
          icon: Icons.bookmark_border,
          label: 'Save | حفظ',
          onTap: () {},
        ),
      ],
    );
  }

  /// Format a DateTime to a human-readable "time ago" string
  /// تنسيق الوقت المنقضي منذ النشر
  String _formatTimeAgo(DateTime dateTime) {
    final difference = DateTime.now().difference(dateTime);

    if (difference.inMinutes < 1) {
      return 'الان';
    } else if (difference.inMinutes < 60) {
      return 'منذ ${difference.inMinutes} دقيقة';
    } else if (difference.inHours < 24) {
      return 'منذ ${difference.inHours} ساعة';
    } else if (difference.inDays < 7) {
      return difference.inDays == 1 ? 'امس' : 'منذ ${difference.inDays} ايام';
    } else {
      return 'منذ ${difference.inDays ~/ 7} اسبوع';
    }
  }
}

/// Individual action button for the post action bar
/// زر تفاعل فردي لشريط تفاعل المنشور
class _ActionButton extends StatelessWidget {
  final IconData icon;
  final String label;
  final VoidCallback onTap;
  final bool isActive;

  const _ActionButton({
    required this.icon,
    required this.label,
    required this.onTap,
    this.isActive = false,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Row(
        children: [
          Icon(
            icon,
            size: 20,
            color: isActive ? SahoolColors.forestGreen : Colors.grey[600],
          ),
          const SizedBox(width: 6),
          Text(
            label,
            style: TextStyle(
              color: isActive ? SahoolColors.forestGreen : Colors.grey[600],
              fontSize: 12,
            ),
          ),
        ],
      ),
    );
  }
}
