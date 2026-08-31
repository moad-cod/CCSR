import type {Metadata} from "next";
import {Providers} from "@/components/providers";
import {geistMono, geistSans} from "./fonts";
import "./globals.css";

export const metadata: Metadata = {
  title: "CCSR",
  description: "Define, run, evaluate, and reproduce computer science research workflows.",
};

export default function RootLayout({children}: {children: React.ReactNode}) {
  return (
    <html lang="en" className={`${geistSans.variable} ${geistMono.variable}`}>
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
