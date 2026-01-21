import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Providers } from "./providers";
import { Toaster } from "sonner";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-sans",
});

export const metadata: Metadata = {
  title: "SaiAd - 삼성 제품 AI 광고 영상 생성기",
  description:
    "AI로 5분 만에 프로급 삼성 제품 광고를 만들어보세요. 스마트폰, TV, 가전 제품 영상을 자동으로 생성합니다.",
  keywords: ["삼성", "광고", "AI", "영상 생성", "마케팅", "자동화"],
  authors: [{ name: "SaiAd Team" }],
  openGraph: {
    title: "SaiAd - 삼성 제품 AI 광고 영상 생성기",
    description: "AI로 5분 만에 프로급 삼성 제품 광고를 만들어보세요.",
    url: "https://saiad.io",
    siteName: "SaiAd",
    locale: "ko_KR",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko" suppressHydrationWarning>
      <body className={`${inter.variable} font-sans antialiased`}>
        <Providers>{children}</Providers>
        <Toaster position="top-right" richColors />
      </body>
    </html>
  );
}
