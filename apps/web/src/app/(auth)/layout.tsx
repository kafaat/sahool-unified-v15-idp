export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-sahool-green-50 via-white to-sahool-brown-50">
      {children}
    </div>
  );
}
