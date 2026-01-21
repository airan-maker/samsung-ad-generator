"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export default function SignupPage() {
  // Redirect to login with social auth
  // Since we only support social login, signup is the same flow

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <Link href="/" className="mb-4 inline-block text-3xl font-bold text-samsung-blue">
            SaiAd
          </Link>
          <CardTitle className="text-2xl">회원가입</CardTitle>
          <CardDescription>
            소셜 계정으로 간편하게 가입하세요
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Google Signup */}
          <Link href="/login">
            <Button
              variant="outline"
              className="w-full justify-center gap-3 py-6"
            >
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
              Google로 가입하기
            </Button>
          </Link>

          {/* Kakao Signup */}
          <Link href="/login">
            <Button
              className="w-full justify-center gap-3 py-6"
              style={{ backgroundColor: "#FEE500", color: "#000000" }}
            >
              <svg className="h-5 w-5" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 3C6.477 3 2 6.463 2 10.691c0 2.742 1.827 5.15 4.575 6.513-.202.758-.729 2.747-.835 3.169-.13.521.191.514.402.374.166-.11 2.649-1.8 3.727-2.533.702.103 1.427.158 2.167.158 5.523 0 10-3.463 10-7.691S17.523 3 12 3z" />
              </svg>
              카카오로 가입하기
            </Button>
          </Link>

          <div className="mt-6 space-y-4 rounded-lg bg-gray-50 p-4">
            <h3 className="font-medium text-gray-900">가입하면 이런 혜택이!</h3>
            <ul className="space-y-2 text-sm text-gray-600">
              <li className="flex items-center gap-2">
                <span className="text-samsung-blue">✓</span>
                매월 무료 영상 3개 생성
              </li>
              <li className="flex items-center gap-2">
                <span className="text-samsung-blue">✓</span>
                12개 프로 템플릿 무료 이용
              </li>
              <li className="flex items-center gap-2">
                <span className="text-samsung-blue">✓</span>
                AI 스크립트 자동 생성
              </li>
            </ul>
          </div>

          <p className="text-center text-sm text-gray-600">
            이미 계정이 있으신가요?{" "}
            <Link href="/login" className="font-medium text-samsung-blue hover:underline">
              로그인
            </Link>
          </p>

          <p className="text-center text-xs text-gray-500">
            가입 시{" "}
            <Link href="/terms" className="underline">
              이용약관
            </Link>{" "}
            및{" "}
            <Link href="/privacy" className="underline">
              개인정보처리방침
            </Link>
            에 동의하게 됩니다.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
