import { Metadata } from "next";
import VerifyOTPClient from "./VerifyOTPClient";

export const metadata: Metadata = {
  title: "Verify OTP | SAHOOL",
  description: "Verify your one-time password to access your SAHOOL Smart Agriculture Platform account",
  keywords: ["verify otp", "التحقق", "one-time password", "sahool"],
  openGraph: {
    title: "Verify OTP | SAHOOL",
    description: "Verify your one-time password for SAHOOL account access",
    type: "website",
  },
};

export default function VerifyOTPPage() {
  return <VerifyOTPClient />;
}
