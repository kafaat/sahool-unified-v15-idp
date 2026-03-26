/**
 * Community Page - Mock Data (Development Fallback)
 * بيانات وهمية ثابتة للتطوير - صفحة إدارة المجتمع
 *
 * This file is separated from the page component to allow tree-shaking
 * in production builds. Mock data is only loaded as a fallback when the
 * API is unavailable during development.
 */

export interface Post {
  id: string;
  author: string;
  authorAr: string;
  content: string;
  contentAr: string;
  category: string;
  categoryAr: string;
  likes: number;
  comments: number;
  reports: number;
  status: 'active' | 'flagged' | 'hidden' | 'pending';
  createdAt: string;
}

export const MOCK_POSTS: Post[] = [
  {
    id: '1',
    author: 'Ahmed Farmer',
    authorAr: 'أحمد المزارع',
    content: 'Tips for wheat irrigation in winter',
    contentAr: 'نصائح لري القمح في الشتاء - يجب مراعاة درجة الحرارة والرطوبة',
    category: 'tips',
    categoryAr: 'نصائح',
    likes: 45,
    comments: 12,
    reports: 0,
    status: 'active',
    createdAt: '2026-01-25T08:00:00',
  },
  {
    id: '2',
    author: 'Mohammed Expert',
    authorAr: 'محمد الخبير',
    content: 'New pest control methods',
    contentAr: 'طرق جديدة لمكافحة الآفات باستخدام المبيدات العضوية',
    category: 'education',
    categoryAr: 'تعليم',
    likes: 89,
    comments: 34,
    reports: 0,
    status: 'active',
    createdAt: '2026-01-24T14:30:00',
  },
  {
    id: '3',
    author: 'Ali Seller',
    authorAr: 'علي البائع',
    content: 'Selling fertilizer cheap',
    contentAr: 'أسمدة للبيع بسعر رخيص جداً - تواصل معي',
    category: 'marketplace',
    categoryAr: 'سوق',
    likes: 5,
    comments: 2,
    reports: 8,
    status: 'flagged',
    createdAt: '2026-01-23T10:00:00',
  },
  {
    id: '4',
    author: 'Khaled New',
    authorAr: 'خالد الجديد',
    content: 'Question about tomato diseases',
    contentAr: 'سؤال عن أمراض الطماطم - ما هو هذا المرض؟',
    category: 'questions',
    categoryAr: 'أسئلة',
    likes: 12,
    comments: 8,
    reports: 0,
    status: 'pending',
    createdAt: '2026-01-25T09:15:00',
  },
  {
    id: '5',
    author: 'Spam User',
    authorAr: 'مستخدم مخالف',
    content: 'External links spam',
    contentAr: 'روابط خارجية مشبوهة - احذروا من هذا الموقع',
    category: 'other',
    categoryAr: 'أخرى',
    likes: 0,
    comments: 0,
    reports: 15,
    status: 'hidden',
    createdAt: '2026-01-22T16:45:00',
  },
];
