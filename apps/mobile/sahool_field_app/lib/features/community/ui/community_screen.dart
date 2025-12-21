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

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: SahoolColors.warmCream,
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
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => _showCreatePost(context),
        backgroundColor: SahoolColors.harvestGold,
        icon: const Icon(Icons.edit, color: Colors.white),
        label: const Text(
          "اسأل المجتمع",
          style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
        ),
      ),
    );
  }

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
          ),
        ],
      ),
    );
  }

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
      ),
    );
  }

  void _showSearch(BuildContext context) {
    showSearch(
      context: context,
      delegate: _CommunitySearchDelegate(),
    );
  }

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
              "الإشعارات",
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            _NotificationItem(
              icon: Icons.comment,
              title: "رد جديد على سؤالك",
              subtitle: "المهندس سالم رد على سؤال البقع الصفراء",
              time: "منذ 5 دقائق",
              isNew: true,
            ),
            _NotificationItem(
              icon: Icons.thumb_up,
              title: "إعجاب جديد",
              subtitle: "15 شخص أعجبوا بمنشورك",
              time: "منذ ساعة",
              isNew: true,
            ),
            _NotificationItem(
              icon: Icons.person_add,
              title: "متابع جديد",
              subtitle: "محمد الفلاح بدأ متابعتك",
              time: "أمس",
              isNew: false,
            ),
          ],
        ),
      ),
    );
  }

  void _showPostDetails(BuildContext context) {
    // Navigate to post details
  }

  void _showComments(BuildContext context) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => Container(
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
                  const Text(
                    "التعليقات",
                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                ],
              ),
            ),
            Expanded(
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
              ),
            ),
          ],
        ),
      ),
    );
  }

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
                        colors: [SahoolColors.forestGreen, SahoolColors.harvestGold],
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
                    ? const Icon(Icons.add, color: SahoolColors.forestGreen, size: 28)
                    : const Icon(Icons.person, color: SahoolColors.forestGreen, size: 28),
              ),
            ),
            const SizedBox(height: 6),
            SizedBox(
              width: 70,
              child: Text(
                name,
                style: const TextStyle(fontSize: 11),
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
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: OrganicCard(
        color: isExpertPost ? SahoolColors.forestGreen.withOpacity(0.05) : null,
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
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
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _InteractionButton extends StatelessWidget {
  final IconData icon;
  final String label;
  final VoidCallback onTap;

  const _InteractionButton({
    required this.icon,
    required this.label,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
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
            Text(label, style: const TextStyle(fontSize: 13)),
          ],
        ),
      ),
    );
  }
}

class _CommunitySearchDelegate extends SearchDelegate<String> {
  @override
  String get searchFieldLabel => 'ابحث في المجتمع...';

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
      child: Text('نتائج البحث عن: $query'),
    );
  }

  @override
  Widget buildSuggestions(BuildContext context) {
    final suggestions = [
      'أمراض الطماطم',
      'ري بالتنقيط',
      'سماد NPK',
      'مكافحة الآفات',
      'البيوت المحمية',
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
