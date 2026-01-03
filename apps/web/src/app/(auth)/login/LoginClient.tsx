'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Mail, Lock } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { useAuth } from '@/stores/auth.store';
import { useToast } from '@/components/ui/toast';

export default function LoginClient() {
  const router = useRouter();
  const { login } = useAuth();
  const { showToast } = useToast();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      await login(email, password);
      showToast({
        type: 'success',
        messageAr: 'تم تسجيل الدخول بنجاح',
        message: 'Login successful',
      });
      router.push('/dashboard');
    } catch (error) {
      const errorMessage = error instanceof Error && 'response' in error &&
        typeof error.response === 'object' && error.response !== null &&
        'data' in error.response && typeof error.response.data === 'object' &&
        error.response.data !== null && 'message' in error.response.data ?
        (error.response.data as { message: string }).message : 'Invalid credentials';

      showToast({
        type: 'error',
        messageAr: 'فشل تسجيل الدخول',
        message: errorMessage,
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-sahool-green-50 to-white p-4">
      <Card className="w-full max-w-md" variant="elevated">
        <CardHeader className="text-center">
          <div className="mx-auto w-16 h-16 bg-sahool-green-100 rounded-full flex items-center justify-center mb-4">
            <div className="w-12 h-12 bg-sahool-green-600 rounded-full" />
          </div>
          <CardTitle className="text-2xl">
            <div>تسجيل الدخول إلى سهول</div>
            <div className="text-base text-gray-600 mt-1">Login to SAHOOL</div>
          </CardTitle>
          <CardDescription>
            <div className="text-gray-600">منصة الإدارة الزراعية المتكاملة</div>
            <div className="text-xs text-gray-500">Integrated Agricultural Management Platform</div>
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              type="email"
              label="Email"
              labelAr="البريد الإلكتروني"
              placeholder="example@sahool.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              leftIcon={<Mail className="w-4 h-4" />}
              required
              autoComplete="email"
            />
            <Input
              type="password"
              label="Password"
              labelAr="كلمة المرور"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              leftIcon={<Lock className="w-4 h-4" />}
              required
              autoComplete="current-password"
            />
            <Button type="submit" fullWidth isLoading={isLoading} size="lg">
              <span className="font-semibold">تسجيل الدخول</span>
              <span className="mx-2">•</span>
              <span className="text-sm">Login</span>
            </Button>
          </form>
          <div className="mt-6 text-center">
            <a
              href="#"
              className="text-sm text-sahool-green-600 hover:text-sahool-green-700 font-medium"
            >
              نسيت كلمة المرور؟ • Forgot Password?
            </a>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
