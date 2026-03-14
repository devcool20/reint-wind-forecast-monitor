import type { Metadata } from "next";
import { JetBrains_Mono, Space_Grotesk } from "next/font/google";
import "./globals.css";

const displayFont = Space_Grotesk({
  variable: "--font-display",
  subsets: ["latin"],
});

const monoFont = JetBrains_Mono({
  variable: "--font-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "REint Wind Forecast Monitor",
  description: "Monitor UK wind generation actuals against forecast values by horizon.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${displayFont.variable} ${monoFont.variable} antialiased`}>
        <div className="app-frame">
          <header className="site-header">
            <div className="container">
              <span className="brand-mark" aria-hidden>
                WFM
              </span>
              <div>
                <p className="brand-title">REint Wind Forecast Monitor</p>
                <p className="brand-subtitle">January 2024 horizon-aware comparison</p>
              </div>
            </div>
          </header>
          {children}
          <footer className="site-footer">
            <div className="container">
              <p>Built with Next.js + Recharts frontend and FastAPI backend.</p>
            </div>
          </footer>
        </div>
      </body>
    </html>
  );
}
