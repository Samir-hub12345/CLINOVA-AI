import type { Metadata } from "next";
import "./globals.css";
import { Header } from "@/components/common/header";
import { Footer } from "@/components/common/footer";
import { SafetyBanner } from "@/components/common/safety-banner";

export const metadata: Metadata = {
  metadataBase: new URL(process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000"),
  title: "CLINOVA AI — Continuous Care Intelligence",
  description:
    "Continuous care intelligence, facility feasibility, and clinical orchestration platform for institutional health systems.",
  icons: {
    icon: [
      { url: "/favicon.ico", sizes: "any" },
      { url: "/favicon.png", type: "image/png" },
    ],
    apple: [{ url: "/apple-touch-icon.png", sizes: "180x180", type: "image/png" }],
  },
  openGraph: {
    title: "CLINOVA AI — Continuous Care Intelligence",
    description: "From Isolated Triage to Continuous Care Intelligence",
    images: [{ url: "/branding/clinova-ai-logo.png", width: 720, height: 180, alt: "Clinova AI" }],
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full bg-slate-50 text-slate-900 antialiased">
      <body className="flex min-h-full flex-col font-sans">
        <SafetyBanner />
        <Header />
        <main className="flex-1">{children}</main>
        <Footer />
      </body>
    </html>
  );
}
