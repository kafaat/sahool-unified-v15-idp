/**
 * Community Feature - Type Definitions
 * تعريفات الأنواع لميزة المجتمع الزراعي
 */

// Post types
export type PostType =
  | "question"
  | "tip"
  | "experience"
  | "discussion"
  | "update";
export type PostStatus = "active" | "resolved" | "closed";

// User post
export interface Post {
  id: string;
  userId: string;
  userName: string;
  userNameAr: string;
  userAvatar?: string;
  userBadge?: "farmer" | "expert" | "verified" | "moderator";
  type: PostType;
  title: string;
  titleAr: string;
  content: string;
  contentAr: string;
  status: PostStatus;
  images?: string[];
  tags?: string[];
  tagsAr?: string[];
  location?: {
    city: string;
    cityAr: string;
    region: string;
    regionAr: string;
  };
  likes: number;
  comments: number;
  shares: number;
  views: number;
  isLiked: boolean;
  isSaved: boolean;
  createdAt: string;
  updatedAt: string;
}

// Comment on a post
export interface Comment {
  id: string;
  postId: string;
  userId: string;
  userName: string;
  userNameAr: string;
  userAvatar?: string;
  userBadge?: "farmer" | "expert" | "verified" | "moderator";
  content: string;
  contentAr: string;
  likes: number;
  isLiked: boolean;
  isExpertAnswer: boolean;
  isBestAnswer: boolean;
  createdAt: string;
  updatedAt: string;
  replies?: Comment[];
}

// Community group
export interface Group {
  id: string;
  name: string;
  nameAr: string;
  description: string;
  descriptionAr: string;
  image?: string;
  coverImage?: string;
  category: GroupCategory;
  privacy: "public" | "private";
  memberCount: number;
  postCount: number;
  isJoined: boolean;
  isModerator: boolean;
  createdBy: string;
  createdAt: string;
  tags?: string[];
  tagsAr?: string[];
}

export type GroupCategory =
  | "crops"
  | "livestock"
  | "irrigation"
  | "pests"
  | "organic"
  | "technology"
  | "marketing"
  | "general";

// Group member
export interface GroupMember {
  id: string;
  userId: string;
  userName: string;
  userNameAr: string;
  userAvatar?: string;
  role: "owner" | "moderator" | "member";
  joinedAt: string;
  lastActive?: string;
  contributions: number;
}

// Chat message
export interface ChatMessage {
  id: string;
  groupId: string;
  userId: string;
  userName: string;
  userNameAr: string;
  userAvatar?: string;
  content: string;
  contentAr: string;
  type: "text" | "image" | "file" | "voice";
  fileUrl?: string;
  fileName?: string;
  replyTo?: {
    messageId: string;
    userName: string;
    preview: string;
  };
  isRead: boolean;
  createdAt: string;
}

// Expert
export interface Expert {
  id: string;
  name: string;
  nameAr: string;
  avatar?: string;
  title: string;
  titleAr: string;
  specialization: string[];
  specializationAr: string[];
  bio: string;
  bioAr: string;
  rating: number;
  totalAnswers: number;
  verifiedAnswers: number;
  availability: "available" | "busy" | "offline";
  responseTime: number; // average in hours
}

// Expert advice question
export interface ExpertQuestion {
  id: string;
  userId: string;
  userName: string;
  userNameAr: string;
  expertId?: string;
  expertName?: string;
  category: string;
  categoryAr: string;
  question: string;
  questionAr: string;
  images?: string[];
  status: "pending" | "answered" | "closed";
  priority: "low" | "medium" | "high" | "urgent";
  answer?: {
    content: string;
    contentAr: string;
    answeredBy: string;
    answeredByAr: string;
    answeredAt: string;
    helpful: number;
    notHelpful: number;
  };
  createdAt: string;
  updatedAt: string;
}

// Filters
export interface CommunityFilters {
  type?: PostType;
  status?: PostStatus;
  tags?: string[];
  location?: string;
  sortBy?: "recent" | "popular" | "trending";
  search?: string;
}

export interface GroupFilters {
  category?: GroupCategory;
  privacy?: "public" | "private";
  joined?: boolean;
  sortBy?: "popular" | "recent" | "active";
  search?: string;
}

// Notifications
export interface CommunityNotification {
  id: string;
  type: "like" | "comment" | "reply" | "mention" | "follow" | "group_invite";
  title: string;
  titleAr: string;
  message: string;
  messageAr: string;
  fromUser: {
    id: string;
    name: string;
    nameAr: string;
    avatar?: string;
  };
  relatedTo?: {
    type: "post" | "comment" | "group";
    id: string;
    title?: string;
  };
  isRead: boolean;
  createdAt: string;
}
