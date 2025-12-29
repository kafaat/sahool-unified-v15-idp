/**
 * Post Comments API Route
 * مسار API لتعليقات المنشور
 */

import { NextRequest, NextResponse } from 'next/server';
import type { Comment } from '@/features/community/types';

// Mock comments data
const mockComments: Record<string, Comment[]> = {
  '1': [
    {
      id: 'comment-1',
      postId: '1',
      userId: 'user-10',
      userName: 'Sarah Ahmad',
      userNameAr: 'سارة أحمد',
      userBadge: 'expert',
      content: 'Try using better quality seeds and ensure proper irrigation.',
      contentAr: 'جرب استخدام بذور بجودة أفضل وتأكد من الري المناسب.',
      likes: 5,
      isLiked: false,
      isExpertAnswer: true,
      isBestAnswer: false,
      createdAt: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString(),
      updatedAt: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString(),
    },
    {
      id: 'comment-2',
      postId: '1',
      userId: 'user-11',
      userName: 'Khalid Salem',
      userNameAr: 'خالد سالم',
      userBadge: 'farmer',
      content: 'I increased my yield by 30% using organic fertilizers.',
      contentAr: 'زادت إنتاجيتي بنسبة 30٪ باستخدام الأسمدة العضوية.',
      likes: 3,
      isLiked: false,
      isExpertAnswer: false,
      isBestAnswer: false,
      createdAt: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
      updatedAt: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
    },
  ],
  '2': [
    {
      id: 'comment-3',
      postId: '2',
      userId: 'user-12',
      userName: 'Hassan Ali',
      userNameAr: 'حسن علي',
      userBadge: 'verified',
      content: 'Great tips! I have been using drip irrigation for years.',
      contentAr: 'نصائح رائعة! أستخدم الري بالتنقيط منذ سنوات.',
      likes: 8,
      isLiked: false,
      isExpertAnswer: false,
      isBestAnswer: false,
      createdAt: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
      updatedAt: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
    },
  ],
  '3': [],
  '4': [],
  '5': [],
};

/**
 * GET /api/v1/community/posts/[postId]/comments
 * Fetch comments for a specific post
 */
export async function GET(
  _request: NextRequest,
  { params }: { params: Promise<{ postId: string }> }
) {
  try {
    const { postId } = await params;

    const comments = mockComments[postId] || [];

    return NextResponse.json(comments, {
      status: 200,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  } catch (error) {
    console.error('Error fetching comments:', error);
    return NextResponse.json(
      { error: 'Failed to fetch comments' },
      { status: 500 }
    );
  }
}

/**
 * POST /api/v1/community/posts/[postId]/comments
 * Add a new comment to a post
 */
export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ postId: string }> }
) {
  try {
    const { postId } = await params;
    const body = await request.json();

    const newComment: Comment = {
      id: `comment-${Date.now()}`,
      postId,
      userId: 'current-user',
      userName: 'Current User',
      userNameAr: 'المستخدم الحالي',
      userBadge: 'farmer',
      content: body.content || '',
      contentAr: body.contentAr || body.content || '',
      likes: 0,
      isLiked: false,
      isExpertAnswer: false,
      isBestAnswer: false,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };

    if (!mockComments[postId]) {
      mockComments[postId] = [];
    }
    mockComments[postId].push(newComment);

    return NextResponse.json(newComment, {
      status: 201,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  } catch (error) {
    console.error('Error adding comment:', error);
    return NextResponse.json(
      { error: 'Failed to add comment' },
      { status: 500 }
    );
  }
}
