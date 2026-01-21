"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { LoadingSpinner } from "@/components/common/Loading";

export default function LoginPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const callbackUrl = searchParams.get("callbackUrl") || "/create";

  const [isLoading, setIsLoading] = useState<"google" | "kakao" | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleGoogleLogin = async () => {
    setIsLoading("google");
    setError(null);

    try {
      // Get Google OAuth URL from environment
      const clientId = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID;
      const redirectUri = `${window.location.origin}/auth/callback/google`;

      const googleAuthUrl = new URL("https://accounts.google.com/o/oauth2/v2/auth");
      googleAuthUrl.searchParams.set("client_id", clientId || "");
      googleAuthUrl.searchParams.set("redirect_uri", redirectUri);
      googleAuthUrl.searchParams.set("response_type", "code");
      googleAuthUrl.searchParams.set("scope", "openid email profile");
      googleAuthUrl.searchParams.set("state", callbackUrl);
      googleAuthUrl.searchParams.set("prompt", "select_account");

      window.location.href = googleAuthUrl.toString();
    } catch (err) {
      setError("Google 로그인 중 오류가 발생했습니다.");
      setIsLoading(null);
    }
  };

  const handleKakaoLogin = async () => {
    setIsLoading("kakao");
    setError(null);

    try {
      const clientId = process.env.NEXT_PUBLIC_KAKAO_CLIENT_ID;
      const redirectUri = `${window.location.origin}/auth/callback/kakao`;

      const kakaoAuthUrl = new URL("https://kauth.kakao.com/oauth/authorize");
      kakaoAuthUrl.searchParams.set("client_id", clientId || "");
      kakaoAuthUrl.searchParams.set("redirect_uri", redirectUri);
      kakaoAuthUrl.searchParams.set("response_type", "code");
      kakaoAuthUrl.searchParams.set("state", callbackUrl);

      window.location.href = kakaoAuthUrl.toString();
    } catch (err) {
      setError("Kakao 로그인 중 오류가 발생했습니다.");
      setIsLoading(null);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <Link href="/" className="mb-4 inline-block text-3xl font-bold text-samsung-blue">
            SaiAd
          </Link>
          <CardTitle className="text-2xl">로그인</CardTitle>
          <CardDescription>
            소셜 계정으로 간편하게 로그인하세요
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {error && (
            <div className="rounded-lg bg-red-50 p-3 text-center text-sm text-red-600">
              {error}
            </div>
          )}

          {/* Google Login */}
          <Button
            variant="outline"
            className="w-full justify-center gap-3 py-6"
            onClick={handleGoogleLogin}
            disabled={isLoading !== null}
          >
            {isLoading === "google" ? (
              <LoadingSpinner />
            ) : (
              <svg className="h-5 w-5" viewBox="0 0 24 24">
                <path
                  d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                  fill="#4285F4"
                />
                <path
                  d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                  fill="#34A853"
                />
                <path
                  d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                  fill="#FBBC05"
                />
                <path
                  d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                  fill="#EA4335"
                />
              </svg>
            )}
            Google로 로그인
          </Button>

          {/* Kakao Login */}
          <Button
            className="w-full justify-center gap-3 py-6"
            style={{ backgroundColor: "#FEE500", color: "#000000" }}
            onClick={handleKakaoLogin}
            disabled={isLoading !== null}
          >
            {isLoading === "kakao" ? (
              <LoadingSpinner className="text-black" />
            ) : (
              <svg className="h-5 w-5" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 3C6.477 3 2 6.463 2 10.691c0 2.742 1.827 5.15 4.575 6.513-.202.758-.729 2.747-.835 3.169-.13.521.191.514.402.374.166-.11 2.649-1.8 3.727-2.533.702.103 1.427.158 2.167.158 5.523 0 10-3.463 10-7.691S17.523 3 12 3z" />
              </svg>
            )}
            카카오로 로그인
          </Button>

          <div className="relative my-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-200" />
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="bg-white px-4 text-gray-500">또는</span>
            </div>
          </div>

          <p className="text-center text-sm text-gray-600">
            계정이 없으신가요?{" "}
            <Link href="/signup" className="font-medium text-samsung-blue hover:underline">
              회원가입
            </Link>
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
