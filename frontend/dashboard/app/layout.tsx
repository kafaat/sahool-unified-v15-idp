import type { Metadata } from 'next'
import '../styles/globals.css'

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
    <html lang="ar" dir="rtl">
      <head>
        <link
          href="https://unpkg.com/maplibre-gl@4.1.2/dist/maplibre-gl.css"
          rel="stylesheet"
        />
      </head>
      <body className="bg-gray-50 min-h-screen">
        <div className="flex h-screen">
          {/* Sidebar */}
          <aside className="w-64 bg-white shadow-lg flex-shrink-0">
            <div className="p-4 border-b">
              <h1 className="text-xl font-bold text-sahool-primary">
                🌾 SAHOOL
              </h1>
              <p className="text-xs text-gray-500 mt-1">v15.3 Dashboard</p>
            </div>
            <nav className="p-4">
              <ul className="space-y-2">
                <li>
                  <a href="/" className="flex items-center gap-3 p-2 rounded-lg hover:bg-gray-100 text-gray-700">
                    <span>🗺️</span>
                    <span>الخريطة</span>
                  </a>
                </li>
                <li>
                  <a href="/tasks" className="flex items-center gap-3 p-2 rounded-lg hover:bg-gray-100 text-gray-700">
                    <span>📋</span>
                    <span>المهام اليومية</span>
                  </a>
                </li>
                <li>
                  <a href="/timeline" className="flex items-center gap-3 p-2 rounded-lg hover:bg-gray-100 text-gray-700">
                    <span>📊</span>
                    <span>الأحداث</span>
                  </a>
                </li>
                <li>
                  <a href="/fields" className="flex items-center gap-3 p-2 rounded-lg hover:bg-gray-100 text-gray-700">
                    <span>🌱</span>
                    <span>الحقول</span>
                  </a>
                </li>
              </ul>
            </nav>

            {/* Quick Stats */}
            <div className="absolute bottom-0 left-0 right-0 p-4 border-t bg-gray-50">
              <div className="grid grid-cols-2 gap-2 text-center text-xs">
                <div className="bg-white p-2 rounded shadow-sm">
                  <div className="font-bold text-sahool-primary text-lg">12</div>
                  <div className="text-gray-500">مهام اليوم</div>
                </div>
                <div className="bg-white p-2 rounded shadow-sm">
                  <div className="font-bold text-sahool-accent text-lg">3</div>
                  <div className="text-gray-500">تنبيهات</div>
                </div>
              </div>
            </div>
          </aside>

          {/* Main Content */}
          <main className="flex-1 overflow-auto">
            {children}
          </main>
        </div>
      </body>
    </html>
  )
}
