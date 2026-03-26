import { Metadata } from "next";
import ResetPasswordClient from "./ResetPasswordClient";

export const metadata: Metadata = {
  title: "Reset Password | SAHOOL",
  description: "Set a new password for your SAHOOL Smart Agriculture Platform account",
  keywords: ["reset password", "إعادة تعيين كلمة المرور", "new password", "sahool"],
  openGraph: {
    title: "Reset Password | SAHOOL",
    description: "Set a new password for your SAHOOL account",
    type: "website",
  },
};

export default function ResetPasswordPage() {
  return <ResetPasswordClient />;
}
