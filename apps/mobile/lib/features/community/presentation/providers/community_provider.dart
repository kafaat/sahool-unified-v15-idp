/// Community Feature Providers - Riverpod State Management
/// موفرو ميزة المجتمع - إدارة الحالة بـ Riverpod
///
/// Manages community posts, discussions, and knowledge base content
/// for the farmer community hub.
library;

import 'package:flutter_riverpod/flutter_riverpod.dart';

// =============================================================================
// Models
// نماذج البيانات
// =============================================================================

/// Community post model
/// نموذج منشور المجتمع
class CommunityPost {
  final String id;
  final String authorId;
  final String authorName;
  final String authorRole;
  final String authorRoleAr;
  final String? authorAvatarUrl;
  final String title;
  final String content;
  final List<String> imageUrls;
  final String category;
  final String categoryAr;
  final int likesCount;
  final int commentsCount;
  final bool isLikedByMe;
  final bool isExpertPost;
  final bool hasExpertReply;
  final DateTime createdAt;
  final List<PostComment> comments;

  const CommunityPost({
    required this.id,
    required this.authorId,
    required this.authorName,
    required this.authorRole,
    this.authorRoleAr = '',
    this.authorAvatarUrl,
    required this.title,
    required this.content,
    this.imageUrls = const [],
    this.category = 'general',
    this.categoryAr = 'عام',
    this.likesCount = 0,
    this.commentsCount = 0,
    this.isLikedByMe = false,
    this.isExpertPost = false,
    this.hasExpertReply = false,
    required this.createdAt,
    this.comments = const [],
  });

  CommunityPost copyWith({
    int? likesCount,
    int? commentsCount,
    bool? isLikedByMe,
    bool? hasExpertReply,
    List<PostComment>? comments,
  }) {
    return CommunityPost(
      id: id,
      authorId: authorId,
      authorName: authorName,
      authorRole: authorRole,
      authorRoleAr: authorRoleAr,
      authorAvatarUrl: authorAvatarUrl,
      title: title,
      content: content,
      imageUrls: imageUrls,
      category: category,
      categoryAr: categoryAr,
      likesCount: likesCount ?? this.likesCount,
      commentsCount: commentsCount ?? this.commentsCount,
      isLikedByMe: isLikedByMe ?? this.isLikedByMe,
      isExpertPost: isExpertPost,
      hasExpertReply: hasExpertReply ?? this.hasExpertReply,
      createdAt: createdAt,
      comments: comments ?? this.comments,
    );
  }
}

/// Post comment model
/// نموذج تعليق المنشور
class PostComment {
  final String id;
  final String authorName;
  final bool isExpert;
  final String content;
  final DateTime createdAt;
  final int likes;

  const PostComment({
    required this.id,
    required this.authorName,
    this.isExpert = false,
    required this.content,
    required this.createdAt,
    this.likes = 0,
  });
}

// =============================================================================
// State
// الحالة
// =============================================================================

/// Community feature state
/// حالة ميزة المجتمع
class CommunityState {
  final List<CommunityPost> posts;
  final bool isLoading;
  final String? error;
  final String selectedCategory;

  const CommunityState({
    this.posts = const [],
    this.isLoading = false,
    this.error,
    this.selectedCategory = 'all',
  });

  CommunityState copyWith({
    List<CommunityPost>? posts,
    bool? isLoading,
    String? error,
    String? selectedCategory,
  }) {
    return CommunityState(
      posts: posts ?? this.posts,
      isLoading: isLoading ?? this.isLoading,
      error: error,
      selectedCategory: selectedCategory ?? this.selectedCategory,
    );
  }

  /// Filter posts by selected category
  /// تصفية المنشورات حسب التصنيف المحدد
  List<CommunityPost> get filteredPosts {
    if (selectedCategory == 'all') return posts;
    return posts.where((p) => p.category == selectedCategory).toList();
  }
}

// =============================================================================
// StateNotifier
// مُعلم الحالة
// =============================================================================

/// Community state notifier - manages posts, likes, and comments
/// مُعلم حالة المجتمع - يدير المنشورات والإعجابات والتعليقات
class CommunityNotifier extends StateNotifier<CommunityState> {
  CommunityNotifier() : super(const CommunityState()) {
    loadPosts();
  }

  /// Load community posts from chat-service with offline-first fallback
  /// تحميل منشورات المجتمع من خدمة المحادثة مع دعم وضع عدم الاتصال
  Future<void> loadPosts() async {
    state = state.copyWith(isLoading: true, error: null);

    // TODO: Wire up Dio client via Riverpod provider to call
    // GET /api/v1/community/posts on chat-service (port 8115).
    // Once injected, replace mock data with real API call:
    //   final response = await dio.get('/api/v1/community/posts');
    //   return (response.data['posts'] as List)
    //       .map((json) => CommunityPost.fromJson(json))
    //       .toList();
    //
    // For now, use mock data (offline-first fallback).
    final posts = _getMockPosts();
    state = state.copyWith(posts: posts, isLoading: false);
  }

  /// Create a new community post
  /// إنشاء منشور جديد في المجتمع
  Future<void> createPost({
    required String title,
    required String content,
    String category = 'general',
    List<String> imageUrls = const [],
  }) async {
    final newPost = CommunityPost(
      id: 'post_${DateTime.now().millisecondsSinceEpoch}',
      authorId: 'current_user',
      authorName: 'أنا',
      authorRole: 'Farmer',
      authorRoleAr: 'مزارع',
      title: title,
      content: content,
      category: category,
      categoryAr: _categoryToAr(category),
      imageUrls: imageUrls,
      createdAt: DateTime.now(),
    );

    state = state.copyWith(posts: [newPost, ...state.posts]);
  }

  /// Toggle like on a post
  /// تبديل الإعجاب على منشور
  void likePost(String postId) {
    final updatedPosts = state.posts.map((post) {
      if (post.id == postId) {
        final isLiked = !post.isLikedByMe;
        return post.copyWith(
          isLikedByMe: isLiked,
          likesCount: isLiked ? post.likesCount + 1 : post.likesCount - 1,
        );
      }
      return post;
    }).toList();

    state = state.copyWith(posts: updatedPosts);
  }

  /// Add a comment to a post
  /// إضافة تعليق على منشور
  void addComment(String postId, String commentText) {
    final updatedPosts = state.posts.map((post) {
      if (post.id == postId) {
        final newComment = PostComment(
          id: 'comment_${DateTime.now().millisecondsSinceEpoch}',
          authorName: 'أنا',
          content: commentText,
          createdAt: DateTime.now(),
        );
        return post.copyWith(
          comments: [...post.comments, newComment],
          commentsCount: post.commentsCount + 1,
        );
      }
      return post;
    }).toList();

    state = state.copyWith(posts: updatedPosts);
  }

  /// Set category filter
  /// تعيين فلتر التصنيف
  void setCategory(String category) {
    state = state.copyWith(selectedCategory: category);
  }

  String _categoryToAr(String category) {
    switch (category) {
      case 'diseases':
        return 'امراض النبات';
      case 'irrigation':
        return 'الري والتسميد';
      case 'marketing':
        return 'تسويق';
      case 'equipment':
        return 'معدات';
      default:
        return 'عام';
    }
  }

  List<CommunityPost> _getMockPosts() {
    return [
      CommunityPost(
        id: 'post_1',
        authorId: 'user_1',
        authorName: 'حسن العمري',
        authorRole: 'Farmer',
        authorRoleAr: 'مزارع',
        title: 'ظهور بقع صفراء على اوراق الطماطم',
        content: 'لاحظت هذه البقع اليوم صباحا في البيت المحمي رقم 3. هل هذا نقص عناصر ام مرض فطري؟',
        category: 'diseases',
        categoryAr: 'امراض النبات',
        likesCount: 12,
        commentsCount: 5,
        hasExpertReply: true,
        createdAt: DateTime.now().subtract(const Duration(hours: 2)),
      ),
      CommunityPost(
        id: 'post_2',
        authorId: 'expert_1',
        authorName: 'المهندس سالم',
        authorRole: 'Certified Expert',
        authorRoleAr: 'خبير زراعي معتمد',
        title: 'تنبيه هام لمزارعي القمح',
        content:
            'بسبب انخفاض درجات الحرارة المتوقع الليلة، يرجى تاخير رية الصباح حتى الساعة 9 لتقليل اثر الصقيع. درجة الحرارة المتوقعة: 2 مئوية',
        category: 'irrigation',
        categoryAr: 'الري والتسميد',
        isExpertPost: true,
        likesCount: 156,
        commentsCount: 24,
        createdAt: DateTime.now().subtract(const Duration(hours: 5)),
      ),
      CommunityPost(
        id: 'post_3',
        authorId: 'user_2',
        authorName: 'محمد الفلاح',
        authorRole: 'Farmer',
        authorRoleAr: 'مزارع',
        title: 'افضل سماد للبطاطس',
        content:
            'ما هو افضل مركب NPK لمرحلة التدرن؟ اريد زيادة حجم الدرنات. المحصول عمره 60 يوم.',
        category: 'irrigation',
        categoryAr: 'الري والتسميد',
        likesCount: 3,
        commentsCount: 8,
        createdAt: DateTime.now().subtract(const Duration(days: 1)),
      ),
      CommunityPost(
        id: 'post_4',
        authorId: 'expert_2',
        authorName: 'فاطمة احمد',
        authorRole: 'Agricultural Engineer',
        authorRoleAr: 'مهندسة زراعية',
        title: 'نصائح للري بالتنقيط في الصيف',
        content:
            'مع ارتفاع درجات الحرارة، اليكم بعض النصائح لتحسين كفاءة الري:\n- زيادة عدد الريات مع تقليل الكمية\n- الري في الصباح الباكر او المساء\n- فحص الفلاتر اسبوعيا',
        category: 'irrigation',
        categoryAr: 'الري والتسميد',
        isExpertPost: true,
        likesCount: 231,
        commentsCount: 42,
        createdAt: DateTime.now().subtract(const Duration(days: 1)),
      ),
    ];
  }
}

// =============================================================================
// Providers
// الموفرون
// =============================================================================

/// Main community state provider
/// الموفر الرئيسي لحالة المجتمع
final communityProvider =
    StateNotifierProvider.autoDispose<CommunityNotifier, CommunityState>((ref) {
  return CommunityNotifier();
});
