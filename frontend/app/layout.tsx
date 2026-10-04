import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "TechCV — Evidence-first AI resume builder",
  description: "Build role-ready developer resumes from evidence, not keyword stuffing.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
