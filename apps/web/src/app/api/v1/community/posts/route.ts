/**
 * Community Posts API Route
 * مسار API لمنشورات المجتمع
 */

import { NextRequest, NextResponse } from 'next/server';
import type { Post } from '@/features/community/types';

function isAuthenticated(request: NextRequest): boolean {
  // For development/testing, allow requests without auth
  if (process.env.NODE_ENV === 'development' || process.env.NODE_ENV === 'test') {
    return true;
  }
  const authHeader = request.headers.get('authorization');
  return !!authHeader && authHeader.startsWith('Bearer ');
}

// Mock community posts data for development and testing
const mockPosts: Post[] = [
  {
    id: '1',
    userId: 'user-1',
    userName: 'Ahmed Ali',
    userNameAr: 'أحمد علي',
    userBadge: 'verified',
    type: 'question',
    title: 'How to improve wheat yield?',
    titleAr: 'كيف أحسن إنتاجية القمح؟',
    content: 'I am looking for advice on improving my wheat crop yield. Any suggestions?',
    contentAr: 'أبحث عن نصائح لتحسين إنتاجية محصول القمح. هل من اقتراحات؟',
    status: 'active',
    images: [],
    tags: ['wheat', 'productivity'],
    tagsAr: ['قمح', 'إنتاجية'],
    location: {
      city: 'Riyadh',
      cityAr: 'الرياض',
      region: 'Central',
      regionAr: 'الوسطى',
    },
    likes: 15,
    comments: 8,
    shares: 3,
    views: 124,
    isLiked: false,
    isSaved: false,
    createdAt: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(), // 2 hours ago
    updatedAt: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
  },
  {
    id: '2',
    userId: 'user-2',
    userName: 'Fatima Hassan',
    userNameAr: 'فاطمة حسن',
    userBadge: 'expert',
    type: 'tip',
    title: 'Best practices for drip irrigation',
    titleAr: 'أفضل الممارسات للري بالتنقيط',
    content: 'Here are some tips for efficient drip irrigation system maintenance.',
    contentAr: 'إليكم بعض النصائح للحفاظ على نظام الري بالتنقيط بكفاءة.',
    status: 'active',
    images: [],
    tags: ['irrigation', 'water-management'],
    tagsAr: ['ري', 'إدارة_المياه'],
    location: {
      city: 'Jeddah',
      cityAr: 'جدة',
      region: 'Western',
      regionAr: 'الغربية',
    },
    likes: 42,
    comments: 12,
    shares: 18,
    views: 356,
    isLiked: false,
    isSaved: false,
    createdAt: new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString(), // 5 hours ago
    updatedAt: new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString(),
  },
  {
    id: '3',
    userId: 'user-3',
    userName: 'Mohammed Ibrahim',
    userNameAr: 'محمد إبراهيم',
    userBadge: 'farmer',
    type: 'experience',
    title: 'My experience with organic farming',
    titleAr: 'تجربتي مع الزراعة العضوية',
    content: 'After 3 years of transitioning to organic farming, here is what I learned.',
    contentAr: 'بعد 3 سنوات من التحول للزراعة العضوية، إليكم ما تعلمته.',
    status: 'active',
    images: [],
    tags: ['organic', 'sustainable'],
    tagsAr: ['عضوي', 'مستدام'],
    location: {
      city: 'Dammam',
      cityAr: 'الدمام',
      region: 'Eastern',
      regionAr: 'الشرقية',
    },
    likes: 67,
    comments: 23,
    shares: 31,
    views: 542,
    isLiked: false,
    isSaved: false,
    createdAt: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(), // 1 day ago
    updatedAt: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
  },
  {
    id: '4',
    userId: 'user-4',
    userName: 'Omar Khalid',
    userNameAr: 'عمر خالد',
    userBadge: 'moderator',
    type: 'discussion',
    title: 'Discussion: Future of smart farming in Saudi Arabia',
    titleAr: 'نقاش: مستقبل الزراعة الذكية في السعودية',
    content: 'What are your thoughts on the adoption of smart farming technologies?',
    contentAr: 'ما رأيكم في تبني تقنيات الزراعة الذكية؟',
    status: 'active',
    images: [],
    tags: ['smart-farming', 'technology'],
    tagsAr: ['زراعة_ذكية', 'تقنية'],
    location: {
      city: 'Medina',
      cityAr: 'المدينة المنورة',
      region: 'Western',
      regionAr: 'الغربية',
    },
    likes: 89,
    comments: 45,
    shares: 22,
    views: 789,
    isLiked: false,
    isSaved: false,
    createdAt: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(), // 2 days ago
    updatedAt: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
  },
  {
    id: '5',
    userId: 'user-5',
    userName: 'Aisha Abdullah',
    userNameAr: 'عائشة عبدالله',
    userBadge: 'verified',
    type: 'update',
    title: 'Harvest season update',
    titleAr: 'تحديث موسم الحصاد',
    content: 'Just finished harvesting this season. Great results!',
    contentAr: 'انتهيت للتو من الحصاد هذا الموسم. نتائج رائعة!',
    status: 'active',
    images: [],
    tags: ['harvest', 'success'],
    tagsAr: ['حصاد', 'نجاح'],
    location: {
      city: 'Tabuk',
      cityAr: 'تبوك',
      region: 'Northern',
      regionAr: 'الشمالية',
    },
    likes: 156,
    comments: 34,
    shares: 12,
    views: 1024,
    isLiked: false,
    isSaved: false,
    createdAt: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(), // 3 days ago
    updatedAt: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
  },
];

/**
 * GET /api/v1/community/posts
 * Fetch community posts with optional filters
 */
export async function GET(request: NextRequest) {
  console.log('API Route: GET /api/v1/community/posts called');

  try {
    const { searchParams } = new URL(request.url);
    console.log('Search params:', Object.fromEntries(searchParams.entries()));

    // Get query parameters
    const type = searchParams.get('type');
    const status = searchParams.get('status');
    const sortBy = searchParams.get('sort_by') || 'recent';
    const search = searchParams.get('search');
    const tags = searchParams.get('tags')?.split(',');
    const location = searchParams.get('location');

    // Filter posts
    let filteredPosts = [...mockPosts];

    // Filter by type
    if (type && type !== 'all') {
      filteredPosts = filteredPosts.filter((post) => post.type === type);
    }

    // Filter by status
    if (status) {
      filteredPosts = filteredPosts.filter((post) => post.status === status);
    }

    // Filter by search query
    if (search) {
      const searchLower = search.toLowerCase();
      filteredPosts = filteredPosts.filter(
        (post) =>
          post.titleAr.toLowerCase().includes(searchLower) ||
          post.title.toLowerCase().includes(searchLower) ||
          post.contentAr.toLowerCase().includes(searchLower) ||
          post.content.toLowerCase().includes(searchLower)
      );
    }

    // Filter by tags
    if (tags && tags.length > 0) {
      filteredPosts = filteredPosts.filter((post) =>
        tags.some((tag) => post.tags?.includes(tag) || post.tagsAr?.includes(tag))
      );
    }

    // Filter by location
    if (location) {
      filteredPosts = filteredPosts.filter(
        (post) =>
          post.location?.city === location ||
          post.location?.cityAr === location ||
          post.location?.region === location ||
          post.location?.regionAr === location
      );
    }

    // Sort posts
    switch (sortBy) {
      case 'popular':
        filteredPosts.sort((a, b) => b.likes - a.likes);
        break;
      case 'trending':
        // Simple trending algorithm: recent posts with high engagement
        filteredPosts.sort((a, b) => {
          const aScore = (a.likes + a.comments * 2 + a.shares * 3) / Math.max(1, Math.floor((Date.now() - new Date(a.createdAt).getTime()) / (1000 * 60 * 60 * 24)));
          const bScore = (b.likes + b.comments * 2 + b.shares * 3) / Math.max(1, Math.floor((Date.now() - new Date(b.createdAt).getTime()) / (1000 * 60 * 60 * 24)));
          return bScore - aScore;
        });
        break;
      case 'recent':
      default:
        filteredPosts.sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime());
        break;
    }

    console.log(`Returning ${filteredPosts.length} posts`);

    return NextResponse.json(filteredPosts, {
      status: 200,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  } catch (error) {
    console.error('Error fetching community posts:', error);
    return NextResponse.json(
      { error: 'Failed to fetch posts' },
      { status: 500 }
    );
  }
}

/**
 * POST /api/v1/community/posts
 * Create a new community post
 */
export async function POST(request: NextRequest) {
  if (!isAuthenticated(request)) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  try {
    const body = await request.json();

    // In a real application, this would save to database
    const newPost: Post = {
      id: `${mockPosts.length + 1}`,
      userId: 'current-user',
      userName: 'Current User',
      userNameAr: 'المستخدم الحالي',
      userBadge: 'farmer',
      type: body.type || 'discussion',
      title: body.title || '',
      titleAr: body.titleAr || '',
      content: body.content || '',
      contentAr: body.contentAr || '',
      status: 'active',
      images: body.images || [],
      tags: body.tags || [],
      tagsAr: body.tagsAr || [],
      location: body.location,
      likes: 0,
      comments: 0,
      shares: 0,
      views: 0,
      isLiked: false,
      isSaved: false,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };

    mockPosts.unshift(newPost);

    return NextResponse.json(newPost, {
      status: 201,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  } catch (error) {
    console.error('Error creating post:', error);
    return NextResponse.json(
      { error: 'Failed to create post' },
      { status: 500 }
    );
  }
}
