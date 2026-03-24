import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'SAHOOL - AI Copilot',
  description: 'AI-powered agricultural assistant for intelligent farming recommendations',
};

export default function CopilotLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
