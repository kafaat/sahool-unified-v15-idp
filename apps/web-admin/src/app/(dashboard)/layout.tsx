import Link from "next/link";
import { auth, signOut } from "@/lib/auth";
import { redirect } from "next/navigation";

const NAV = [
  { href: "/", label: "Dashboard" },
  { href: "/users", label: "Users" },
  { href: "/fields", label: "Fields" },
  { href: "/usage", label: "API Usage" },
  { href: "/audit", label: "Audit Log" },
];

export default async function AdminLayout({ children }: { children: React.ReactNode }) {
  const session = await auth();
  if (!session?.user || session.user.role !== "admin") redirect("/login");

  return (
    <div className="min-h-screen flex">
      {/* Sidebar */}
      <aside className="w-52 shrink-0 border-r bg-card flex flex-col">
        <div className="px-5 py-4 border-b">
          <span className="font-bold text-primary text-sm">Agri Admin</span>
        </div>
        <nav className="flex-1 px-3 py-4 space-y-1">
          {NAV.map((item) => (
            <Link key={item.href} href={item.href}
              className="block px-3 py-2 rounded-md text-sm hover:bg-muted transition-colors">
              {item.label}
            </Link>
          ))}
        </nav>
        <div className="px-5 py-4 border-t">
          <p className="text-xs text-muted-foreground mb-2 truncate">{session.user.email}</p>
          <form action={async () => { "use server"; await signOut({ redirectTo: "/login" }); }}>
            <button className="text-xs text-muted-foreground hover:text-foreground transition-colors">
              Sign out
            </button>
          </form>
        </div>
      </aside>

      {/* Main */}
      <main className="flex-1 overflow-auto">
        <div className="max-w-6xl mx-auto px-8 py-8">{children}</div>
      </main>
    </div>
  );
}
