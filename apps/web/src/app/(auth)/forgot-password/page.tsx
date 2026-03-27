import type { Metadata } from 'next';
import ForgotPasswordClient from './ForgotPasswordClient';

export const metadata: Metadata = {
  title: 'Forgot Password | SAHOOL',
  description: 'Reset your SAHOOL Smart Agriculture Platform account password',
  keywords: ['forgot password', 'نسيت كلمة المرور', 'reset', 'sahool'],
  openGraph: {
    title: 'Forgot Password | SAHOOL',
    description: 'Reset your SAHOOL account password',
    type: 'website',
  },
};

export default function ForgotPasswordPage() {
  return <ForgotPasswordClient />;
}
