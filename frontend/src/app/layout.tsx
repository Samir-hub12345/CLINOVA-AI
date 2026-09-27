import type { Metadata } from "next";
import "./globals.css";
import { Providers } from "@/components/providers";
import { APP_NAME, APP_TAGLINE } from "@/lib/constants";

export const metadata: Metadata = {
  title: {
    default: `${APP_NAME} — Multimodal Healthcare Triage Assistant`,
    template: `%s | ${APP_NAME}`,
  },
  description: APP_TAGLINE,
  icons: {
    icon: [
      { url: "/favicon.ico", sizes: "any" },
      { url: "/favicon.png", type: "image/png" },
    ],
    apple: [
      { url: "/apple-touch-icon.png", sizes: "180x180", type: "image/png" },
    ],
  },
  openGraph: {
    title: `${APP_NAME} — Multimodal Healthcare Triage Assistant`,
    description: APP_TAGLINE,
    images: [
      {
        url: "/branding/clinova-ai-logo.png",
        width: 720,
        height: 180,
        alt: "Clinova AI Logo",
      },
    ],
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="scroll-smooth">
      <body className="antialiased flex flex-col min-h-screen">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
