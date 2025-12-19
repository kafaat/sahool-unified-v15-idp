import type { Metadata } from 'next'
import '../styles/globals.css'
import { ThemeProvider } from '@/contexts/ThemeContext'
import { ToastProvider } from '@/contexts/ToastContext'
import { ConnectionStatus } from '@/components/ui/ConnectionStatus'
import { ThemeToggle } from '@/components/ui/ThemeToggle'

export const metadata: Metadata = {
  title: 'SAHOOL Dashboard | لوحة التحكم',
  description: 'منصة إدارة المزارع الذكية - SAHOOL Agricultural Platform',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ar" dir="rtl" suppressHydrationWarning>
      <head>
        <link
          href="https://unpkg.com/maplibre-gl@4.1.2/dist/maplibre-gl.css"
          rel="stylesheet"
        />
      </head>
      <body className="min-h-screen" style={{ backgroundColor: 'var(--bg-primary)' }}>
        <ThemeProvider>
          <ToastProvider>
            <div className="flex h-screen">
              {/* Sidebar */}
              <aside className="w-64 shadow-lg flex-shrink-0 relative hidden md:block" style={{ backgroundColor: 'var(--bg-secondary)' }}>
                <div className="p-4 border-b" style={{ borderColor: 'var(--border-color)' }}>
                  <div className="flex items-center justify-between">
                    <div>
                      <h1 className="text-xl font-bold" style={{ color: 'var(--sahool-primary)' }}>
                        🌾 SAHOOL
                      </h1>
                      <p className="text-xs mt-1" style={{ color: 'var(--text-muted)' }}>v15.3 Dashboard</p>
                    </div>
                    <ThemeToggle />
                  </div>
                </div>
                <nav className="p-4">
                  <ul className="space-y-2">
                    <li>
                      <a href="/" className="flex items-center gap-3 p-2 rounded-lg hover:bg-opacity-10" style={{ color: 'var(--text-primary)' }}>
                        <span>🗺️</span>
                        <span>الخريطة</span>
                      </a>
                    </li>
                    <li>
                      <a href="/tasks" className="flex items-center gap-3 p-2 rounded-lg hover:bg-opacity-10" style={{ color: 'var(--text-primary)' }}>
                        <span>📋</span>
                        <span>المهام اليومية</span>
                      </a>
                    </li>
                    <li>
                      <a href="/timeline" className="flex items-center gap-3 p-2 rounded-lg hover:bg-opacity-10" style={{ color: 'var(--text-primary)' }}>
                        <span>📊</span>
                        <span>الأحداث</span>
                      </a>
                    </li>
                    <li>
                      <a href="/fields" className="flex items-center gap-3 p-2 rounded-lg hover:bg-opacity-10" style={{ color: 'var(--text-primary)' }}>
                        <span>🌱</span>
                        <span>الحقول</span>
                      </a>
                    </li>
                    <li>
                      <a href="/weather" className="flex items-center gap-3 p-2 rounded-lg hover:bg-opacity-10" style={{ color: 'var(--text-primary)' }}>
                        <span>🌤️</span>
                        <span>الطقس</span>
                      </a>
                    </li>
                    <li>
                      <a href="/reports" className="flex items-center gap-3 p-2 rounded-lg hover:bg-opacity-10" style={{ color: 'var(--text-primary)' }}>
                        <span>📈</span>
                        <span>التقارير</span>
                      </a>
                    </li>
                  </ul>
                </nav>

                {/* Quick Stats */}
                <div className="absolute bottom-0 left-0 right-0 p-4 border-t" style={{ borderColor: 'var(--border-color)', backgroundColor: 'var(--bg-tertiary)' }}>
                  <div className="grid grid-cols-2 gap-2 text-center text-xs">
                    <div className="p-2 rounded shadow-sm" style={{ backgroundColor: 'var(--bg-secondary)' }}>
                      <div className="font-bold text-lg" style={{ color: 'var(--sahool-primary)' }}>12</div>
                      <div style={{ color: 'var(--text-muted)' }}>مهام اليوم</div>
                    </div>
                    <div className="p-2 rounded shadow-sm" style={{ backgroundColor: 'var(--bg-secondary)' }}>
                      <div className="font-bold text-lg" style={{ color: 'var(--sahool-accent)' }}>3</div>
                      <div style={{ color: 'var(--text-muted)' }}>تنبيهات</div>
                    </div>
                  </div>
                </div>
              </aside>

              {/* Mobile Header */}
              <div className="md:hidden fixed top-0 left-0 right-0 z-50 p-4 flex items-center justify-between" style={{ backgroundColor: 'var(--bg-secondary)', borderBottom: '1px solid var(--border-color)' }}>
                <h1 className="text-lg font-bold" style={{ color: 'var(--sahool-primary)' }}>🌾 SAHOOL</h1>
                <div className="flex items-center gap-2">
                  <ThemeToggle />
                  <button className="p-2 rounded-lg" style={{ backgroundColor: 'var(--bg-tertiary)' }}>
                    <span>☰</span>
                  </button>
                </div>
              </div>

              {/* Main Content */}
              <main className="flex-1 overflow-auto md:mt-0 mt-16">
                {children}
              </main>
            </div>

            {/* Global Components */}
            <ConnectionStatus />
          </ToastProvider>
        </ThemeProvider>
      </body>
    </html>
  )
}
