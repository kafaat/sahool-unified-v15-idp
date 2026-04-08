import { auth } from "@/lib/auth";
import { redirect } from "next/navigation";
import Link from "next/link";
import { signOut } from "@/lib/auth";

export default async function DashboardLayout({ children }: { children: React.ReactNode }) {
  const session = await auth();
  if (!session?.user) redirect("/login");

  return (
    <div className="min-h-screen flex flex-col">
      <header className="border-b bg-card px-6 py-3 flex items-center justify-between">
        <Link href="/fields" className="font-semibold text-primary">
          Agri Platform
        </Link>
        <div className="flex items-center gap-4 text-sm">
          <span className="text-muted-foreground">{session.user.email}</span>
          <form
            action={async () => {
              "use server";
              await signOut({ redirectTo: "/login" });
            }}
          >
            <button className="text-muted-foreground hover:text-foreground transition-colors">
              Sign out
            </button>
          </form>
        </div>
      </header>
      <main className="flex-1 container max-w-6xl mx-auto px-6 py-8">{children}</main>
    </div>
  );
}
