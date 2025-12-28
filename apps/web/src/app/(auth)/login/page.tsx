import { Metadata } from 'next';
import LoginClient from './LoginClient';

export const metadata: Metadata = {
  title: 'Login | SAHOOL - Smart Agriculture Platform',
  description: 'تسجيل الدخول إلى منصة سهول الزراعية - Login to SAHOOL Smart Agricultural Platform',
  keywords: ['login', 'تسجيل الدخول', 'sahool', 'agriculture'],
  openGraph: {
    title: 'Login | SAHOOL',
    description: 'Login to SAHOOL Smart Agricultural Platform',
    type: 'website',
  },
};

export default function LoginPage() {
  return <LoginClient />;
}
