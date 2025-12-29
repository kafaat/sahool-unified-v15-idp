/**
 * Like Post API Route
 * مسار API للإعجاب بالمنشور
 */

import { NextRequest, NextResponse } from 'next/server';

export async function POST(
  _request: NextRequest,
  { params }: { params: Promise<{ postId: string }> }
) {
  try {
    const { postId } = await params;

    // In a real application, this would toggle like status in database
    // For now, just return success

    return NextResponse.json(
      { success: true, postId },
      { status: 200 }
    );
  } catch (error) {
    console.error('Error liking post:', error);
    return NextResponse.json(
      { error: 'Failed to like post' },
      { status: 500 }
    );
  }
}
