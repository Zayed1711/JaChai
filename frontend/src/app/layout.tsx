import type { Metadata, Viewport } from "next";
import localFont from "next/font/local";
import "./globals.css";

const geistSans = localFont({
  src: "./fonts/GeistVF.woff",
  variable: "--font-geist-sans",
  weight: "100 900",
});
const geistMono = localFont({
  src: "./fonts/GeistMonoVF.woff",
  variable: "--font-geist-mono",
  weight: "100 900",
});

export const metadata: Metadata = {
  title: "JaChai (যাচাই) — Bangladeshi Price Index - যা চাই করুন যাচাই",
  description: "The Best Price for Your Next Purchase. Deterministic price comparison for Bangladesh.",
  manifest: "/manifest.json",
  appleWebApp: {
    capable: true,
    statusBarStyle: "black-translucent",
    title: "JaChai",
  },
};

export const viewport: Viewport = {
  themeColor: "#0A0B0E",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <head>
        <link rel="apple-touch-icon" href="/icons/icon-192x192.png" />
      </head>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased min-h-screen bg-[#0A0B0E] text-white selection:bg-[#10B981] selection:text-black overflow-x-hidden`}
      >
        {children}
        <script
          dangerouslySetInnerHTML={{
            __html: `
              if (typeof window !== 'undefined') {
                if ('serviceWorker' in navigator) {
                  navigator.serviceWorker.getRegistrations().then(function(registrations) {
                    for (let registration of registrations) {
                      registration.unregister();
                    }
                  });
                }
                if ('caches' in window) {
                  caches.keys().then(function(names) {
                    for (let name of names) caches.delete(name);
                  });
                }
              }
            `,
          }}
        />
      </body>
    </html>
  );
}
