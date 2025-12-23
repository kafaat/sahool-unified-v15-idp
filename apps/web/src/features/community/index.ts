/**
 * Community Feature
 * ميزة المجتمع الزراعي
 *
 * This feature handles:
 * - Community posts and discussions
 * - Farmer groups and forums
 * - Expert advice and consultations
 * - Social interactions (likes, comments, shares)
 * - Knowledge sharing
 */

// Component exports
export { Feed } from './components/Feed';
export { PostCard } from './components/PostCard';
export { CreatePost } from './components/CreatePost';
export { Groups } from './components/Groups';

// Hook exports
export {
  usePosts,
  usePost,
  useTrendingPosts,
  useSavedPosts,
  useMyPosts,
  useCreatePost,
  useUpdatePost,
  useDeletePost,
  useLikePost,
  useSavePost,
  useSharePost,
  useComments,
  useAddComment,
  useLikeComment,
} from './hooks/useCommunity';

// Type exports
export type {
  PostType,
  PostStatus,
  Post,
  Comment,
  Group,
  GroupCategory,
  GroupMember,
  ChatMessage,
  Expert,
  ExpertQuestion,
  CommunityFilters,
  GroupFilters,
  CommunityNotification,
} from './types';

export const COMMUNITY_FEATURE = 'community' as const;
