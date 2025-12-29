/**
 * Share Post API Route
 * مسار API لمشاركة المنشور
 */

import { NextRequest, NextResponse } from 'next/server';

export async function POST(
  _request: NextRequest,
  { params }: { params: Promise<{ postId: string }> }
) {
  try {
    const { postId } = await params;

    // In a real application, this would increment share count in database
    // For now, just return success

    return NextResponse.json(
      { success: true, postId },
      { status: 200 }
    );
  } catch (error) {
    console.error('Error sharing post:', error);
    return NextResponse.json(
      { error: 'Failed to share post' },
      { status: 500 }
    );
  }
}
