import { Metadata } from 'next';
import RegisterClient from './RegisterClient';

export const metadata: Metadata = {
  title: 'Register | SAHOOL - Smart Agriculture Platform',
  description:
    'إنشاء حساب جديد في منصة سهول الزراعية - Create a new account on SAHOOL Smart Agricultural Platform',
  keywords: ['register', 'signup', 'إنشاء حساب', 'تسجيل', 'sahool', 'agriculture'],
  openGraph: {
    title: 'Register | SAHOOL',
    description: 'Create a new account on SAHOOL Smart Agricultural Platform',
    type: 'website',
  },
};

export default function RegisterPage() {
  return <RegisterClient />;
}
