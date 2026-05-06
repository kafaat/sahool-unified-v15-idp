export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-sahool-green-50 via-white to-sahool-brown-50 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900">
      {children}
    </div>
  );
}
