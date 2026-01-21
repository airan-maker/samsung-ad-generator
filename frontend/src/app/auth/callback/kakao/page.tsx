"use client";

import { Suspense, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { LoadingPage } from "@/components/common/Loading";
import { api } from "@/lib/api";

function KakaoCallbackContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const handleCallback = async () => {
      const code = searchParams.get("code");
      const state = searchParams.get("state"); // callback URL
      const errorParam = searchParams.get("error");

      if (errorParam) {
        setError("카카오 로그인이 취소되었습니다.");
        setTimeout(() => router.push("/login"), 2000);
        return;
      }

      if (!code) {
        setError("인증 코드가 없습니다.");
        setTimeout(() => router.push("/login"), 2000);
        return;
      }

      try {
        const redirectUri = `${window.location.origin}/auth/callback/kakao`;
        const response = await api.loginWithKakao(code, redirectUri);

        // Store user info in localStorage or state management
        if (typeof window !== "undefined") {
          localStorage.setItem("user", JSON.stringify(response.user));
        }

        // Redirect to callback URL or default
        router.push(state || "/create");
      } catch (err: unknown) {
        console.error("Kakao login error:", err);
        const errorMessage = err instanceof Error ? err.message : "로그인 중 오류가 발생했습니다.";
        setError(errorMessage);
        setTimeout(() => router.push("/login"), 3000);
      }
    };

    handleCallback();
  }, [searchParams, router]);

  if (error) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center">
        <div className="rounded-lg bg-red-50 p-6 text-center">
          <p className="text-red-600">{error}</p>
          <p className="mt-2 text-sm text-gray-500">로그인 페이지로 이동합니다...</p>
        </div>
      </div>
    );
  }

  return <LoadingPage />;
}

export default function KakaoCallbackPage() {
  return (
    <Suspense fallback={<LoadingPage />}>
      <KakaoCallbackContent />
    </Suspense>
  );
}
