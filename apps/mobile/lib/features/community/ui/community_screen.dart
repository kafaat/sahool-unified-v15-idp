<<<<<<< HEAD
import 'package:flutter/material.dart';
import '../../../core/theme/sahool_theme.dart';
import '../../../core/theme/organic_widgets.dart';

/// شاشة مجتمع المزارعين - Sahool Community Hub
/// منصة لتبادل الخبرات والأسئلة بين المزارعين والخبراء
class CommunityScreen extends StatefulWidget {
  const CommunityScreen({super.key});

  @override
  State<CommunityScreen> createState() => _CommunityScreenState();
}

class _CommunityScreenState extends State<CommunityScreen> {
  String _selectedCategory = 'all';
=======
/// Community Screen - Farmer Community Hub
/// شاشة مجتمع المزارعين - منصة تبادل الخبرات
///
/// Features:
/// - Tab bar: Feed | Discussions | Knowledge Base
/// - Post cards with author avatar, text, images, likes
/// - Floating action button to create post
/// - Search bar
/// - Arabic/English bilingual
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/theme/sahool_theme.dart';
import '../../../core/theme/organic_widgets.dart';
import '../presentation/providers/community_provider.dart';
import '../presentation/widgets/post_card.dart';

/// Full community screen with tabbed interface
/// شاشة المجتمع الكاملة مع واجهة مبوبة
class CommunityScreen extends ConsumerStatefulWidget {
  const CommunityScreen({super.key});

  @override
  ConsumerState<CommunityScreen> createState() => _CommunityScreenState();
}

class _CommunityScreenState extends ConsumerState<CommunityScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }
>>>>>>> 32fd5d55beabbbf36de4006c89fcda63cab80473

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: SahoolColors.warmCream,
<<<<<<< HEAD
      appBar: AppBar(
        title: const Text("مجتمع المزارعين"),
        backgroundColor: Colors.white,
        foregroundColor: SahoolColors.forestGreen,
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.search),
            onPressed: () => _showSearch(context),
          ),
          Stack(
            children: [
              IconButton(
                icon: const Icon(Icons.notifications_none),
                onPressed: () => _showNotifications(context),
              ),
              Positioned(
                right: 8,
                top: 8,
                child: Container(
                  width: 8,
                  height: 8,
                  decoration: const BoxDecoration(
                    color: SahoolColors.danger,
                    shape: BoxShape.circle,
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () async {
          await Future.delayed(const Duration(seconds: 1));
        },
        color: SahoolColors.forestGreen,
        child: ListView(
          padding: const EdgeInsets.all(20),
          children: [
            // 1. شريط القصص/الحالات (Stories)
            _buildStoriesSection(),

            const SizedBox(height: 24),

            // 2. فلتر التصنيفات
            _buildCategoryFilters(),

            const SizedBox(height: 24),

            // 3. المنشورات (Posts Feed)
            _PostCard(
              authorName: "حسن العمري",
              authorRole: "مزارع",
              authorImage: "assets/avatars/farmer1.png",
              timeAgo: "منذ ساعتين",
              title: "ظهور بقع صفراء على أوراق الطماطم",
              content:
                  "لاحظت هذه البقع اليوم صباحاً في البيت المحمي رقم 3. هل هذا نقص عناصر أم مرض فطري؟",
              hasImage: true,
              commentsCount: 5,
              likesCount: 12,
              hasExpertReply: true,
              onTap: () => _showPostDetails(context),
              onComment: () => _showComments(context),
            ),

            const SizedBox(height: 16),

            _PostCard(
              authorName: "المهندس سالم",
              authorRole: "خبير زراعي معتمد",
              authorImage: "assets/avatars/expert1.png",
              timeAgo: "منذ 5 ساعات",
              title: "تنبيه هام لمزارعي القمح",
              content:
                  "بسبب انخفاض درجات الحرارة المتوقع الليلة، يرجى تأخير رية الصباح حتى الساعة 9 لتقليل أثر الصقيع. درجة الحرارة المتوقعة: 2°C",
              isExpertPost: true,
              commentsCount: 24,
              likesCount: 156,
              onTap: () => _showPostDetails(context),
              onComment: () => _showComments(context),
            ),

            const SizedBox(height: 16),

            _PostCard(
              authorName: "محمد الفلاح",
              authorRole: "مزارع",
              authorImage: "assets/avatars/farmer2.png",
              timeAgo: "أمس",
              title: "أفضل سماد للبطاطس",
              content:
                  "ما هو أفضل مركب NPK لمرحلة التدرن؟ أريد زيادة حجم الدرنات. المحصول عمره 60 يوم.",
              commentsCount: 8,
              likesCount: 3,
              onTap: () => _showPostDetails(context),
              onComment: () => _showComments(context),
            ),

            const SizedBox(height: 16),

            _PostCard(
              authorName: "فاطمة أحمد",
              authorRole: "مهندسة زراعية",
              authorImage: "assets/avatars/expert2.png",
              timeAgo: "أمس",
              title: "نصائح للري بالتنقيط في الصيف",
              content:
                  "مع ارتفاع درجات الحرارة، إليكم بعض النصائح لتحسين كفاءة الري:\n• زيادة عدد الريات مع تقليل الكمية\n• الري في الصباح الباكر أو المساء\n• فحص الفلاتر أسبوعياً",
              isExpertPost: true,
              commentsCount: 42,
              likesCount: 231,
              onTap: () => _showPostDetails(context),
              onComment: () => _showComments(context),
            ),

            const SizedBox(height: 100), // Space for FAB
          ],
        ),
      ),
=======
      appBar: _buildAppBar(),
      body: TabBarView(
        controller: _tabController,
        children: [
          _FeedTab(),
          _DiscussionsTab(),
          _KnowledgeBaseTab(),
        ],
      ),
>>>>>>> 32fd5d55beabbbf36de4006c89fcda63cab80473
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => _showCreatePost(context),
        backgroundColor: SahoolColors.harvestGold,
        icon: const Icon(Icons.edit, color: Colors.white),
        label: const Text(
<<<<<<< HEAD
          "اسأل المجتمع",
=======
          'Ask Community | اسال المجتمع',
>>>>>>> 32fd5d55beabbbf36de4006c89fcda63cab80473
          style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
        ),
      ),
    );
  }

<<<<<<< HEAD
  Widget _buildStoriesSection() {
    return SizedBox(
      height: 100,
      child: ListView(
        scrollDirection: Axis.horizontal,
        children: [
          _StoryItem(
            isAdd: true,
            name: "إضافة",
            onTap: () => _showCreateStory(context),
          ),
          _StoryItem(
            name: "المهندس علي",
            hasNewStory: true,
            onTap: () => _viewStory(context, "المهندس علي"),
          ),
          _StoryItem(
            name: "مزرعة الوفاء",
            hasNewStory: true,
            onTap: () => _viewStory(context, "مزرعة الوفاء"),
          ),
          _StoryItem(
            name: "سعيد محمد",
            hasNewStory: false,
            onTap: () => _viewStory(context, "سعيد محمد"),
          ),
          _StoryItem(
            name: "تعاونية صعدة",
            hasNewStory: true,
            onTap: () => _viewStory(context, "تعاونية صعدة"),
          ),
          _StoryItem(
            name: "خبير الآفات",
            hasNewStory: false,
            onTap: () => _viewStory(context, "خبير الآفات"),
=======
  PreferredSizeWidget _buildAppBar() {
    return AppBar(
      title: const Text('Farmer Community | مجتمع المزارعين'),
      backgroundColor: Colors.white,
      foregroundColor: SahoolColors.forestGreen,
      elevation: 0,
      actions: [
        IconButton(
          icon: const Icon(Icons.search),
          onPressed: () => _showSearch(context),
          tooltip: 'Search | بحث',
        ),
        Stack(
          children: [
            IconButton(
              icon: const Icon(Icons.notifications_none),
              onPressed: () => _showNotifications(context),
              tooltip: 'Notifications | الاشعارات',
            ),
            Positioned(
              right: 8,
              top: 8,
              child: Container(
                width: 8,
                height: 8,
                decoration: const BoxDecoration(
                  color: SahoolColors.danger,
                  shape: BoxShape.circle,
                ),
              ),
            ),
          ],
        ),
      ],
      bottom: TabBar(
        controller: _tabController,
        labelColor: SahoolColors.forestGreen,
        unselectedLabelColor: Colors.grey,
        indicatorColor: SahoolColors.forestGreen,
        indicatorWeight: 3,
        tabs: const [
          Tab(
            icon: Icon(Icons.dynamic_feed, size: 20),
            text: 'Feed | المنشورات',
          ),
          Tab(
            icon: Icon(Icons.forum, size: 20),
            text: 'Discussions | النقاشات',
          ),
          Tab(
            icon: Icon(Icons.library_books, size: 20),
            text: 'Knowledge | المعرفة',
>>>>>>> 32fd5d55beabbbf36de4006c89fcda63cab80473
          ),
        ],
      ),
    );
  }

<<<<<<< HEAD
  Widget _buildCategoryFilters() {
    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: Row(
        children: [
          _CategoryChip(
            label: "الكل",
            icon: Icons.apps,
            isSelected: _selectedCategory == 'all',
            onTap: () => setState(() => _selectedCategory = 'all'),
          ),
          const SizedBox(width: 8),
          _CategoryChip(
            label: "أمراض النبات",
            icon: Icons.bug_report,
            isSelected: _selectedCategory == 'diseases',
            onTap: () => setState(() => _selectedCategory = 'diseases'),
          ),
          const SizedBox(width: 8),
          _CategoryChip(
            label: "الري والتسميد",
            icon: Icons.water_drop,
            isSelected: _selectedCategory == 'irrigation',
            onTap: () => setState(() => _selectedCategory = 'irrigation'),
          ),
          const SizedBox(width: 8),
          _CategoryChip(
            label: "تسويق",
            icon: Icons.store,
            isSelected: _selectedCategory == 'marketing',
            onTap: () => setState(() => _selectedCategory = 'marketing'),
          ),
          const SizedBox(width: 8),
          _CategoryChip(
            label: "معدات",
            icon: Icons.agriculture,
            isSelected: _selectedCategory == 'equipment',
            onTap: () => setState(() => _selectedCategory = 'equipment'),
          ),
        ],
=======
  // ===========================================================================
  // Create Post Bottom Sheet
  // نافذة إنشاء منشور جديد
  // ===========================================================================

  void _showCreatePost(BuildContext context) {
    final titleController = TextEditingController();
    final contentController = TextEditingController();

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => Container(
        height: MediaQuery.of(context).size.height * 0.85,
        decoration: const BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
        ),
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                TextButton(
                  onPressed: () => Navigator.pop(context),
                  child: const Text('Cancel | الغاء'),
                ),
                const Text(
                  'New Post | سؤال جديد',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
                TextButton(
                  onPressed: () {
                    if (titleController.text.isNotEmpty) {
                      ref.read(communityProvider.notifier).createPost(
                            title: titleController.text,
                            content: contentController.text,
                          );
                      Navigator.pop(context);
                    }
                  },
                  child: const Text(
                    'Post | نشر',
                    style: TextStyle(
                      color: SahoolColors.forestGreen,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 24),
            TextField(
              controller: titleController,
              decoration: InputDecoration(
                hintText: 'Post title | عنوان السؤال',
                filled: true,
                fillColor: Colors.grey[100],
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: BorderSide.none,
                ),
              ),
              style: const TextStyle(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            Expanded(
              child: TextField(
                controller: contentController,
                maxLines: null,
                expands: true,
                decoration: InputDecoration(
                  hintText:
                      'Write your question details...\nاكتب تفاصيل سؤالك هنا...',
                  filled: true,
                  fillColor: Colors.grey[100],
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: BorderSide.none,
                  ),
                  alignLabelWithHint: true,
                ),
              ),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                _AttachButton(
                  icon: Icons.camera_alt,
                  label: 'Photo | صورة',
                  onTap: () {},
                ),
                const SizedBox(width: 12),
                _AttachButton(
                  icon: Icons.location_on,
                  label: 'Field | الحقل',
                  onTap: () {},
                ),
                const SizedBox(width: 12),
                _AttachButton(
                  icon: Icons.tag,
                  label: 'Tag | تصنيف',
                  onTap: () {},
                ),
              ],
            ),
          ],
        ),
>>>>>>> 32fd5d55beabbbf36de4006c89fcda63cab80473
      ),
    );
  }

<<<<<<< HEAD
=======
  // ===========================================================================
  // Search
  // البحث
  // ===========================================================================

>>>>>>> 32fd5d55beabbbf36de4006c89fcda63cab80473
  void _showSearch(BuildContext context) {
    showSearch(
      context: context,
      delegate: _CommunitySearchDelegate(),
    );
  }

<<<<<<< HEAD
=======
  // ===========================================================================
  // Notifications
  // الاشعارات
  // ===========================================================================

>>>>>>> 32fd5d55beabbbf36de4006c89fcda63cab80473
  void _showNotifications(BuildContext context) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => Container(
        height: MediaQuery.of(context).size.height * 0.6,
        decoration: const BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
        ),
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
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
            const SizedBox(height: 24),
            const Text(
<<<<<<< HEAD
              "الإشعارات",
=======
              'Notifications | الاشعارات',
>>>>>>> 32fd5d55beabbbf36de4006c89fcda63cab80473
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            _NotificationItem(
              icon: Icons.comment,
<<<<<<< HEAD
              title: "رد جديد على سؤالك",
              subtitle: "المهندس سالم رد على سؤال البقع الصفراء",
              time: "منذ 5 دقائق",
=======
              title: 'New reply | رد جديد على سؤالك',
              subtitle: 'المهندس سالم رد على سؤال البقع الصفراء',
              time: '5 min | منذ 5 دقائق',
>>>>>>> 32fd5d55beabbbf36de4006c89fcda63cab80473
              isNew: true,
            ),
            _NotificationItem(
              icon: Icons.thumb_up,
<<<<<<< HEAD
              title: "إعجاب جديد",
              subtitle: "15 شخص أعجبوا بمنشورك",
              time: "منذ ساعة",
=======
              title: 'New likes | اعجاب جديد',
              subtitle: '15 people liked your post | 15 شخص اعجبوا بمنشورك',
              time: '1h | منذ ساعة',
>>>>>>> 32fd5d55beabbbf36de4006c89fcda63cab80473
              isNew: true,
            ),
            _NotificationItem(
              icon: Icons.person_add,
<<<<<<< HEAD
              title: "متابع جديد",
              subtitle: "محمد الفلاح بدأ متابعتك",
              time: "أمس",
=======
              title: 'New follower | متابع جديد',
              subtitle: 'محمد الفلاح بدا متابعتك',
              time: 'Yesterday | امس',
>>>>>>> 32fd5d55beabbbf36de4006c89fcda63cab80473
              isNew: false,
            ),
          ],
        ),
      ),
    );
  }
<<<<<<< HEAD

  void _showPostDetails(BuildContext context) {
    // Navigate to post details
  }

  void _showComments(BuildContext context) {
=======
}

// =============================================================================
// Feed Tab - المنشورات
// =============================================================================

class _FeedTab extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final communityState = ref.watch(communityProvider);

    if (communityState.isLoading) {
      return const Center(
        child: CircularProgressIndicator(color: SahoolColors.forestGreen),
      );
    }

    if (communityState.error != null) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.error_outline, size: 48, color: SahoolColors.danger),
            const SizedBox(height: 16),
            Text(
              'Error loading posts\nخطا في تحميل المنشورات',
              textAlign: TextAlign.center,
              style: TextStyle(color: Colors.grey[600]),
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: () => ref.read(communityProvider.notifier).loadPosts(),
              child: const Text('Retry | اعادة المحاولة'),
            ),
          ],
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: () => ref.read(communityProvider.notifier).loadPosts(),
      color: SahoolColors.forestGreen,
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // Stories section
          _buildStoriesSection(context),
          const SizedBox(height: 16),

          // Category filters
          _buildCategoryFilters(ref, communityState.selectedCategory),
          const SizedBox(height: 16),

          // Posts
          ...communityState.filteredPosts.map((post) => Padding(
                padding: const EdgeInsets.only(bottom: 16),
                child: PostCard(
                  post: post,
                  onLike: () =>
                      ref.read(communityProvider.notifier).likePost(post.id),
                  onComment: () => _showComments(context, ref, post),
                  onTap: () {},
                ),
              )),

          const SizedBox(height: 80), // Space for FAB
        ],
      ),
    );
  }

  Widget _buildStoriesSection(BuildContext context) {
    return SizedBox(
      height: 100,
      child: ListView(
        scrollDirection: Axis.horizontal,
        children: [
          _StoryItem(
            isAdd: true,
            name: 'Add | اضافة',
            onTap: () {},
          ),
          _StoryItem(
            name: 'Eng. Ali | م. علي',
            hasNewStory: true,
            onTap: () {},
          ),
          _StoryItem(
            name: 'Al-Wafa Farm | مزرعة الوفاء',
            hasNewStory: true,
            onTap: () {},
          ),
          _StoryItem(
            name: 'Saeed | سعيد',
            hasNewStory: false,
            onTap: () {},
          ),
          _StoryItem(
            name: 'Saada Co-op | تعاونية صعدة',
            hasNewStory: true,
            onTap: () {},
          ),
        ],
      ),
    );
  }

  Widget _buildCategoryFilters(WidgetRef ref, String selected) {
    final categories = [
      ('all', Icons.apps, 'All | الكل'),
      ('diseases', Icons.bug_report, 'Diseases | امراض'),
      ('irrigation', Icons.water_drop, 'Irrigation | الري'),
      ('marketing', Icons.store, 'Marketing | تسويق'),
      ('equipment', Icons.agriculture, 'Equipment | معدات'),
    ];

    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: Row(
        children: categories.map((cat) {
          final isSelected = selected == cat.$1;
          return Padding(
            padding: const EdgeInsets.only(left: 8),
            child: GestureDetector(
              onTap: () =>
                  ref.read(communityProvider.notifier).setCategory(cat.$1),
              child: Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                decoration: BoxDecoration(
                  color:
                      isSelected ? SahoolColors.forestGreen : Colors.white,
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(
                    color: isSelected
                        ? SahoolColors.forestGreen
                        : Colors.grey.withOpacity(0.3),
                  ),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(
                      cat.$2,
                      size: 16,
                      color: isSelected ? Colors.white : Colors.grey,
                    ),
                    const SizedBox(width: 6),
                    Text(
                      cat.$3,
                      style: TextStyle(
                        color: isSelected ? Colors.white : Colors.grey[700],
                        fontWeight:
                            isSelected ? FontWeight.bold : FontWeight.normal,
                        fontSize: 12,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          );
        }).toList(),
      ),
    );
  }

  void _showComments(
      BuildContext context, WidgetRef ref, CommunityPost post) {
    final commentController = TextEditingController();

>>>>>>> 32fd5d55beabbbf36de4006c89fcda63cab80473
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
<<<<<<< HEAD
      builder: (context) => Container(
=======
      builder: (sheetContext) => Container(
>>>>>>> 32fd5d55beabbbf36de4006c89fcda63cab80473
        height: MediaQuery.of(context).size.height * 0.75,
        decoration: const BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
        ),
        child: Column(
          children: [
            Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                children: [
                  Container(
                    width: 40,
                    height: 4,
                    decoration: BoxDecoration(
                      color: Colors.grey[300],
                      borderRadius: BorderRadius.circular(2),
                    ),
                  ),
                  const SizedBox(height: 16),
<<<<<<< HEAD
                  const Text(
                    "التعليقات",
                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
=======
                  Text(
                    'Comments (${post.commentsCount}) | التعليقات',
                    style: const TextStyle(
                        fontSize: 18, fontWeight: FontWeight.bold),
>>>>>>> 32fd5d55beabbbf36de4006c89fcda63cab80473
                  ),
                ],
              ),
            ),
            Expanded(
<<<<<<< HEAD
              child: ListView(
                padding: const EdgeInsets.symmetric(horizontal: 16),
                children: [
                  _CommentItem(
                    author: "المهندس سالم",
                    isExpert: true,
                    content:
                        "هذه أعراض نقص المغنيسيوم. أنصح برش سماد ورقي يحتوي على 2% مغنيسيوم.",
                    time: "منذ ساعة",
                    likes: 8,
                  ),
                  _CommentItem(
                    author: "أحمد محمد",
                    isExpert: false,
                    content: "حصل معي نفس الشيء الموسم الماضي. نصيحة المهندس صحيحة.",
                    time: "منذ 30 دقيقة",
                    likes: 2,
                  ),
                ],
              ),
=======
              child: post.comments.isEmpty
                  ? Center(
                      child: Text(
                        'No comments yet\nلا توجد تعليقات بعد',
                        textAlign: TextAlign.center,
                        style: TextStyle(color: Colors.grey[400]),
                      ),
                    )
                  : ListView.builder(
                      padding: const EdgeInsets.symmetric(horizontal: 16),
                      itemCount: post.comments.length,
                      itemBuilder: (ctx, index) {
                        final comment = post.comments[index];
                        return Container(
                          margin: const EdgeInsets.only(bottom: 12),
                          padding: const EdgeInsets.all(12),
                          decoration: BoxDecoration(
                            color: comment.isExpert
                                ? SahoolColors.forestGreen.withOpacity(0.05)
                                : Colors.grey[50],
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Row(
                                children: [
                                  Text(
                                    comment.authorName,
                                    style: const TextStyle(
                                        fontWeight: FontWeight.bold,
                                        fontSize: 13),
                                  ),
                                  if (comment.isExpert) ...[
                                    const SizedBox(width: 4),
                                    const Icon(Icons.verified,
                                        size: 14, color: Colors.blue),
                                  ],
                                ],
                              ),
                              const SizedBox(height: 6),
                              Text(comment.content,
                                  style: const TextStyle(height: 1.4)),
                            ],
                          ),
                        );
                      },
                    ),
>>>>>>> 32fd5d55beabbbf36de4006c89fcda63cab80473
            ),
            Container(
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
<<<<<<< HEAD
              child: Row(
                children: [
                  Expanded(
                    child: TextField(
                      decoration: InputDecoration(
                        hintText: "اكتب تعليقاً...",
                        filled: true,
                        fillColor: Colors.grey[100],
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(24),
                          borderSide: BorderSide.none,
                        ),
                        contentPadding: const EdgeInsets.symmetric(
                          horizontal: 16,
                          vertical: 12,
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(width: 12),
                  CircleAvatar(
                    backgroundColor: SahoolColors.forestGreen,
                    child: IconButton(
                      icon: const Icon(Icons.send, color: Colors.white, size: 20),
                      onPressed: () {},
                    ),
                  ),
                ],
=======
              child: SafeArea(
                child: Row(
                  children: [
                    Expanded(
                      child: TextField(
                        controller: commentController,
                        decoration: InputDecoration(
                          hintText: 'Write a comment... | اكتب تعليقا...',
                          filled: true,
                          fillColor: Colors.grey[100],
                          border: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(24),
                            borderSide: BorderSide.none,
                          ),
                          contentPadding: const EdgeInsets.symmetric(
                            horizontal: 16,
                            vertical: 12,
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(width: 12),
                    CircleAvatar(
                      backgroundColor: SahoolColors.forestGreen,
                      child: IconButton(
                        icon: const Icon(Icons.send,
                            color: Colors.white, size: 20),
                        onPressed: () {
                          if (commentController.text.trim().isNotEmpty) {
                            ref
                                .read(communityProvider.notifier)
                                .addComment(post.id, commentController.text);
                            commentController.clear();
                          }
                        },
                      ),
                    ),
                  ],
                ),
>>>>>>> 32fd5d55beabbbf36de4006c89fcda63cab80473
              ),
            ),
          ],
        ),
      ),
    );
  }
<<<<<<< HEAD

  void _showCreatePost(BuildContext context) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => Container(
        height: MediaQuery.of(context).size.height * 0.85,
        decoration: const BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
        ),
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                TextButton(
                  onPressed: () => Navigator.pop(context),
                  child: const Text("إلغاء"),
                ),
                const Text(
                  "سؤال جديد",
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
                TextButton(
                  onPressed: () => Navigator.pop(context),
                  child: const Text(
                    "نشر",
                    style: TextStyle(
                      color: SahoolColors.forestGreen,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 24),
            TextField(
              decoration: InputDecoration(
                hintText: "عنوان السؤال",
                filled: true,
                fillColor: Colors.grey[100],
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: BorderSide.none,
                ),
              ),
              style: const TextStyle(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            Expanded(
              child: TextField(
                maxLines: null,
                expands: true,
                decoration: InputDecoration(
                  hintText: "اكتب تفاصيل سؤالك هنا...\n\nمثال: ما هي أعراض نقص البوتاسيوم في الطماطم؟",
                  filled: true,
                  fillColor: Colors.grey[100],
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: BorderSide.none,
                  ),
                  alignLabelWithHint: true,
                ),
              ),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                _AttachButton(
                  icon: Icons.camera_alt,
                  label: "صورة",
                  onTap: () {},
                ),
                const SizedBox(width: 12),
                _AttachButton(
                  icon: Icons.location_on,
                  label: "الحقل",
                  onTap: () {},
                ),
                const SizedBox(width: 12),
                _AttachButton(
                  icon: Icons.tag,
                  label: "تصنيف",
                  onTap: () {},
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  void _showCreateStory(BuildContext context) {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text("سيتم فتح الكاميرا لإضافة قصة"),
        behavior: SnackBarBehavior.floating,
      ),
    );
  }

  void _viewStory(BuildContext context, String name) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text("عرض قصة $name"),
        behavior: SnackBarBehavior.floating,
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Helper Widgets
// ═══════════════════════════════════════════════════════════════════════════
=======
}

// =============================================================================
// Discussions Tab - النقاشات
// =============================================================================

class _DiscussionsTab extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        _DiscussionTile(
          title: 'Wheat Irrigation Best Practices | افضل ممارسات ري القمح',
          participants: 24,
          lastMessage: 'Eng. Salem shared a new watering schedule',
          lastMessageAr: 'م. سالم شارك جدول ري جديد',
          time: '10 min ago | منذ 10 دقائق',
          isActive: true,
        ),
        _DiscussionTile(
          title:
              'Tomato Disease Prevention | الوقاية من امراض الطماطم',
          participants: 18,
          lastMessage: 'New images added for identification',
          lastMessageAr: 'تم اضافة صور جديدة للتعرف',
          time: '1h ago | منذ ساعة',
          isActive: true,
        ),
        _DiscussionTile(
          title: 'Market Prices Discussion | اسعار السوق',
          participants: 45,
          lastMessage: 'Wheat prices updated for this week',
          lastMessageAr: 'تم تحديث اسعار القمح لهذا الاسبوع',
          time: '3h ago | منذ 3 ساعات',
          isActive: false,
        ),
        _DiscussionTile(
          title: 'Organic Farming Tips | نصائح الزراعة العضوية',
          participants: 12,
          lastMessage: 'Natural pest control methods shared',
          lastMessageAr: 'تمت مشاركة طرق مكافحة طبيعية',
          time: 'Yesterday | امس',
          isActive: false,
        ),
      ],
    );
  }
}

// =============================================================================
// Knowledge Base Tab - قاعدة المعرفة
// =============================================================================

class _KnowledgeBaseTab extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        const Padding(
          padding: EdgeInsets.only(bottom: 16),
          child: Text(
            'Agricultural Knowledge | المعرفة الزراعية',
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
          ),
        ),
        _KnowledgeCard(
          icon: Icons.bug_report,
          title: 'Pest & Disease Guide | دليل الآفات والامراض',
          subtitle: '42 articles | 42 مقال',
          color: SahoolColors.danger,
        ),
        _KnowledgeCard(
          icon: Icons.water_drop,
          title: 'Irrigation Best Practices | افضل ممارسات الري',
          subtitle: '28 articles | 28 مقال',
          color: SahoolColors.info,
        ),
        _KnowledgeCard(
          icon: Icons.eco,
          title: 'Fertilizer Guide | دليل التسميد',
          subtitle: '35 articles | 35 مقال',
          color: SahoolColors.success,
        ),
        _KnowledgeCard(
          icon: Icons.wb_sunny,
          title: 'Seasonal Calendar | التقويم الزراعي',
          subtitle: '12 guides | 12 دليل',
          color: SahoolColors.harvestGold,
        ),
        _KnowledgeCard(
          icon: Icons.agriculture,
          title: 'Equipment Guides | ادلة المعدات',
          subtitle: '18 articles | 18 مقال',
          color: SahoolColors.earthBrown,
        ),
      ],
    );
  }
}

// =============================================================================
// Helper Widgets
// عناصر مساعدة
// =============================================================================
>>>>>>> 32fd5d55beabbbf36de4006c89fcda63cab80473

class _StoryItem extends StatelessWidget {
  final bool isAdd;
  final String name;
  final bool hasNewStory;
  final VoidCallback onTap;

  const _StoryItem({
    this.isAdd = false,
    required this.name,
    this.hasNewStory = false,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        margin: const EdgeInsets.only(left: 16),
        child: Column(
          children: [
            Container(
              width: 68,
              height: 68,
              padding: const EdgeInsets.all(3),
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                gradient: hasNewStory || isAdd
                    ? const LinearGradient(
<<<<<<< HEAD
                        colors: [SahoolColors.forestGreen, SahoolColors.harvestGold],
=======
                        colors: [
                          SahoolColors.forestGreen,
                          SahoolColors.harvestGold
                        ],
>>>>>>> 32fd5d55beabbbf36de4006c89fcda63cab80473
                        begin: Alignment.topLeft,
                        end: Alignment.bottomRight,
                      )
                    : null,
                border: !hasNewStory && !isAdd
                    ? Border.all(color: Colors.grey[300]!, width: 2)
                    : null,
              ),
              child: Container(
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: isAdd ? Colors.white : SahoolColors.paleOlive,
                  border: Border.all(color: Colors.white, width: 2),
                ),
                child: isAdd
<<<<<<< HEAD
                    ? const Icon(Icons.add, color: SahoolColors.forestGreen, size: 28)
                    : const Icon(Icons.person, color: SahoolColors.forestGreen, size: 28),
=======
                    ? const Icon(Icons.add,
                        color: SahoolColors.forestGreen, size: 28)
                    : const Icon(Icons.person,
                        color: SahoolColors.forestGreen, size: 28),
>>>>>>> 32fd5d55beabbbf36de4006c89fcda63cab80473
              ),
            ),
            const SizedBox(height: 6),
            SizedBox(
              width: 70,
              child: Text(
                name,
<<<<<<< HEAD
                style: const TextStyle(fontSize: 11),
=======
                style: const TextStyle(fontSize: 10),
>>>>>>> 32fd5d55beabbbf36de4006c89fcda63cab80473
                textAlign: TextAlign.center,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

<<<<<<< HEAD
class _CategoryChip extends StatelessWidget {
  final String label;
  final IconData icon;
  final bool isSelected;
  final VoidCallback onTap;

  const _CategoryChip({
    required this.label,
    required this.icon,
    required this.isSelected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
        decoration: BoxDecoration(
          color: isSelected ? SahoolColors.forestGreen : Colors.white,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(
            color: isSelected ? SahoolColors.forestGreen : Colors.grey.withOpacity(0.3),
          ),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              icon,
              size: 16,
              color: isSelected ? Colors.white : Colors.grey,
            ),
            const SizedBox(width: 6),
            Text(
              label,
              style: TextStyle(
                color: isSelected ? Colors.white : Colors.grey[700],
                fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                fontSize: 13,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _PostCard extends StatelessWidget {
  final String authorName;
  final String authorRole;
  final String authorImage;
  final String timeAgo;
  final String title;
  final String content;
  final bool hasImage;
  final int commentsCount;
  final int likesCount;
  final bool isExpertPost;
  final bool hasExpertReply;
  final VoidCallback onTap;
  final VoidCallback onComment;

  const _PostCard({
    required this.authorName,
    required this.authorRole,
    required this.authorImage,
    required this.timeAgo,
    required this.title,
    required this.content,
    this.hasImage = false,
    required this.commentsCount,
    required this.likesCount,
    this.isExpertPost = false,
    this.hasExpertReply = false,
    required this.onTap,
    required this.onComment,
=======
class _DiscussionTile extends StatelessWidget {
  final String title;
  final int participants;
  final String lastMessage;
  final String lastMessageAr;
  final String time;
  final bool isActive;

  const _DiscussionTile({
    required this.title,
    required this.participants,
    required this.lastMessage,
    required this.lastMessageAr,
    required this.time,
    this.isActive = false,
>>>>>>> 32fd5d55beabbbf36de4006c89fcda63cab80473
  });

  @override
  Widget build(BuildContext context) {
<<<<<<< HEAD
    return GestureDetector(
      onTap: onTap,
      child: OrganicCard(
        color: isExpertPost ? SahoolColors.forestGreen.withOpacity(0.05) : null,
=======
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      child: OrganicCard(
>>>>>>> 32fd5d55beabbbf36de4006c89fcda63cab80473
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
<<<<<<< HEAD
            // Header
            Row(
              children: [
                CircleAvatar(
                  radius: 22,
                  backgroundColor: SahoolColors.paleOlive,
                  child: const Icon(Icons.person, color: SahoolColors.forestGreen),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Text(
                            authorName,
                            style: const TextStyle(fontWeight: FontWeight.bold),
                          ),
                          if (isExpertPost) ...[
                            const SizedBox(width: 4),
                            const Icon(Icons.verified, size: 16, color: Colors.blue),
                          ],
                        ],
                      ),
                      Text(
                        "$authorRole • $timeAgo",
                        style: const TextStyle(fontSize: 11, color: Colors.grey),
                      ),
                    ],
                  ),
                ),
                if (hasExpertReply)
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: SahoolColors.forestGreen.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: const Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(
                          Icons.check_circle,
                          size: 12,
                          color: SahoolColors.forestGreen,
                        ),
                        SizedBox(width: 4),
                        Text(
                          "مجاب",
                          style: TextStyle(
                            fontSize: 10,
                            color: SahoolColors.forestGreen,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                  ),
                PopupMenuButton(
                  icon: const Icon(Icons.more_vert, color: Colors.grey),
                  itemBuilder: (context) => [
                    const PopupMenuItem(value: 'save', child: Text('حفظ')),
                    const PopupMenuItem(value: 'report', child: Text('إبلاغ')),
                    const PopupMenuItem(value: 'share', child: Text('مشاركة')),
                  ],
                ),
              ],
            ),

            const SizedBox(height: 12),

            // Content
            Text(
              title,
              style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
            ),
            const SizedBox(height: 6),
            Text(
              content,
              style: TextStyle(color: Colors.grey[800], height: 1.5),
            ),

            if (hasImage) ...[
              const SizedBox(height: 12),
              Container(
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
              ),
            ],

            const Divider(height: 24),

            // Interaction buttons
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _InteractionButton(
                  icon: Icons.thumb_up_alt_outlined,
                  label: "$likesCount",
                  onTap: () {},
                ),
                _InteractionButton(
                  icon: Icons.chat_bubble_outline,
                  label: "$commentsCount",
                  onTap: onComment,
                ),
                _InteractionButton(
                  icon: Icons.share_outlined,
                  label: "مشاركة",
                  onTap: () {},
                ),
                _InteractionButton(
                  icon: Icons.bookmark_border,
                  label: "حفظ",
                  onTap: () {},
=======
            Row(
              children: [
                if (isActive)
                  Container(
                    width: 8,
                    height: 8,
                    margin: const EdgeInsets.only(left: 8),
                    decoration: const BoxDecoration(
                      color: SahoolColors.success,
                      shape: BoxShape.circle,
                    ),
                  ),
                Expanded(
                  child: Text(
                    title,
                    style: const TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 14,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              '$lastMessage\n$lastMessageAr',
              style: TextStyle(fontSize: 12, color: Colors.grey[600]),
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
            ),
            const SizedBox(height: 8),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Row(
                  children: [
                    const Icon(Icons.people, size: 14, color: Colors.grey),
                    const SizedBox(width: 4),
                    Text(
                      '$participants members | عضو',
                      style:
                          const TextStyle(fontSize: 11, color: Colors.grey),
                    ),
                  ],
                ),
                Text(
                  time,
                  style: const TextStyle(fontSize: 11, color: Colors.grey),
>>>>>>> 32fd5d55beabbbf36de4006c89fcda63cab80473
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

<<<<<<< HEAD
class _InteractionButton extends StatelessWidget {
  final IconData icon;
  final String label;
  final VoidCallback onTap;

  const _InteractionButton({
    required this.icon,
    required this.label,
    required this.onTap,
=======
class _KnowledgeCard extends StatelessWidget {
  final IconData icon;
  final String title;
  final String subtitle;
  final Color color;

  const _KnowledgeCard({
    required this.icon,
    required this.title,
    required this.subtitle,
    required this.color,
>>>>>>> 32fd5d55beabbbf36de4006c89fcda63cab80473
  });

  @override
  Widget build(BuildContext context) {
<<<<<<< HEAD
    return GestureDetector(
      onTap: onTap,
      child: Row(
        children: [
          Icon(icon, size: 20, color: Colors.grey[600]),
          const SizedBox(width: 6),
          Text(
            label,
            style: TextStyle(color: Colors.grey[600], fontSize: 13),
          ),
        ],
=======
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      child: OrganicCard(
        onTap: () {},
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            Container(
              width: 48,
              height: 48,
              decoration: BoxDecoration(
                color: color.withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(icon, color: color),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: const TextStyle(
                        fontWeight: FontWeight.bold, fontSize: 14),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    subtitle,
                    style: TextStyle(fontSize: 12, color: Colors.grey[600]),
                  ),
                ],
              ),
            ),
            const Icon(Icons.chevron_right, color: Colors.grey),
          ],
        ),
>>>>>>> 32fd5d55beabbbf36de4006c89fcda63cab80473
      ),
    );
  }
}

class _NotificationItem extends StatelessWidget {
  final IconData icon;
  final String title;
  final String subtitle;
  final String time;
  final bool isNew;

  const _NotificationItem({
    required this.icon,
    required this.title,
    required this.subtitle,
    required this.time,
    required this.isNew,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 12),
      decoration: BoxDecoration(
        border: Border(
          bottom: BorderSide(color: Colors.grey[200]!),
        ),
      ),
      child: Row(
        children: [
          Container(
            width: 44,
            height: 44,
            decoration: BoxDecoration(
              color: isNew
                  ? SahoolColors.forestGreen.withOpacity(0.1)
                  : Colors.grey[100],
              borderRadius: BorderRadius.circular(12),
            ),
            child: Icon(
              icon,
              color: isNew ? SahoolColors.forestGreen : Colors.grey,
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: TextStyle(
                    fontWeight: isNew ? FontWeight.bold : FontWeight.normal,
                  ),
                ),
                Text(
                  subtitle,
                  style: const TextStyle(fontSize: 12, color: Colors.grey),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
              ],
            ),
          ),
          Text(
            time,
<<<<<<< HEAD
            style: const TextStyle(fontSize: 11, color: Colors.grey),
          ),
        ],
      ),
    );
  }
}

class _CommentItem extends StatelessWidget {
  final String author;
  final bool isExpert;
  final String content;
  final String time;
  final int likes;

  const _CommentItem({
    required this.author,
    required this.isExpert,
    required this.content,
    required this.time,
    required this.likes,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: isExpert
            ? SahoolColors.forestGreen.withOpacity(0.05)
            : Colors.grey[50],
        borderRadius: BorderRadius.circular(12),
        border: isExpert
            ? Border.all(color: SahoolColors.forestGreen.withOpacity(0.2))
            : null,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              CircleAvatar(
                radius: 16,
                backgroundColor: SahoolColors.paleOlive,
                child: const Icon(
                  Icons.person,
                  size: 18,
                  color: SahoolColors.forestGreen,
                ),
              ),
              const SizedBox(width: 8),
              Text(
                author,
                style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13),
              ),
              if (isExpert) ...[
                const SizedBox(width: 4),
                const Icon(Icons.verified, size: 14, color: Colors.blue),
              ],
              const Spacer(),
              Text(
                time,
                style: const TextStyle(fontSize: 11, color: Colors.grey),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(content, style: const TextStyle(height: 1.4)),
          const SizedBox(height: 8),
          Row(
            children: [
              GestureDetector(
                onTap: () {},
                child: Row(
                  children: [
                    const Icon(Icons.thumb_up_alt_outlined, size: 16, color: Colors.grey),
                    const SizedBox(width: 4),
                    Text("$likes", style: const TextStyle(fontSize: 12, color: Colors.grey)),
                  ],
                ),
              ),
              const SizedBox(width: 16),
              GestureDetector(
                onTap: () {},
                child: const Text(
                  "رد",
                  style: TextStyle(fontSize: 12, color: SahoolColors.forestGreen),
                ),
              ),
            ],
=======
            style: const TextStyle(fontSize: 10, color: Colors.grey),
>>>>>>> 32fd5d55beabbbf36de4006c89fcda63cab80473
          ),
        ],
      ),
    );
  }
}

class _AttachButton extends StatelessWidget {
  final IconData icon;
  final String label;
  final VoidCallback onTap;

  const _AttachButton({
    required this.icon,
    required this.label,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
        decoration: BoxDecoration(
          color: Colors.grey[100],
          borderRadius: BorderRadius.circular(20),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, size: 18, color: SahoolColors.forestGreen),
            const SizedBox(width: 6),
<<<<<<< HEAD
            Text(label, style: const TextStyle(fontSize: 13)),
=======
            Text(label, style: const TextStyle(fontSize: 12)),
>>>>>>> 32fd5d55beabbbf36de4006c89fcda63cab80473
          ],
        ),
      ),
    );
  }
}

class _CommunitySearchDelegate extends SearchDelegate<String> {
  @override
<<<<<<< HEAD
  String get searchFieldLabel => 'ابحث في المجتمع...';
=======
  String get searchFieldLabel => 'Search community... | ابحث في المجتمع...';
>>>>>>> 32fd5d55beabbbf36de4006c89fcda63cab80473

  @override
  List<Widget> buildActions(BuildContext context) {
    return [
      IconButton(
        icon: const Icon(Icons.clear),
        onPressed: () => query = '',
      ),
    ];
  }

  @override
  Widget buildLeading(BuildContext context) {
    return IconButton(
      icon: const Icon(Icons.arrow_back),
      onPressed: () => close(context, ''),
    );
  }

  @override
  Widget buildResults(BuildContext context) {
    return Center(
<<<<<<< HEAD
      child: Text('نتائج البحث عن: $query'),
=======
      child: Text('Results for: $query\nنتائج البحث عن: $query'),
>>>>>>> 32fd5d55beabbbf36de4006c89fcda63cab80473
    );
  }

  @override
  Widget buildSuggestions(BuildContext context) {
    final suggestions = [
<<<<<<< HEAD
      'أمراض الطماطم',
      'ري بالتنقيط',
      'سماد NPK',
      'مكافحة الآفات',
      'البيوت المحمية',
=======
      'Tomato diseases | امراض الطماطم',
      'Drip irrigation | ري بالتنقيط',
      'NPK fertilizer | سماد NPK',
      'Pest control | مكافحة الآفات',
      'Greenhouse | البيوت المحمية',
>>>>>>> 32fd5d55beabbbf36de4006c89fcda63cab80473
    ];

    return ListView.builder(
      itemCount: suggestions.length,
      itemBuilder: (context, index) {
        return ListTile(
          leading: const Icon(Icons.search),
          title: Text(suggestions[index]),
          onTap: () {
            query = suggestions[index];
            showResults(context);
          },
        );
      },
    );
  }
}
