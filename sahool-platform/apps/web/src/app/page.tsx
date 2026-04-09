import { redirect } from "next/navigation";
import { cookies } from "next/headers";
import { jwtVerify } from "jose";

export default async function HomePage() {
  const cookieStore = await cookies();
  const token = cookieStore.get("access_token")?.value;
  const secret = process.env.JWT_SECRET_KEY;

  if (token && secret) {
    try {
      await jwtVerify(token, new TextEncoder().encode(secret));
      redirect("/dashboard");
    } catch {
      // fall through to login
    }
  }

  redirect("/login");
}
