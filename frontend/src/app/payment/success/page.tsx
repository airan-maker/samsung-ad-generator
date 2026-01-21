"use client";

import { useEffect, useState, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { LoadingPage } from "@/components/common/Loading";
import { CheckCircle, AlertCircle, Loader2 } from "lucide-react";
import { api } from "@/lib/api";
import { useAuthStore } from "@/stores/authStore";

function PaymentSuccessContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { refreshUser } = useAuthStore();

  const [status, setStatus] = useState<"loading" | "success" | "error">("loading");
  const [error, setError] = useState<string | null>(null);
  const [receiptUrl, setReceiptUrl] = useState<string | null>(null);

  useEffect(() => {
    const confirmPayment = async () => {
      const paymentKey = searchParams.get("paymentKey");
      const orderId = searchParams.get("orderId");
      const amount = searchParams.get("amount");

      if (!paymentKey || !orderId || !amount) {
        setStatus("error");
        setError("결제 정보가 누락되었습니다.");
        return;
      }

      try {
        const result = await api.post("/payments/confirm", {
          payment_key: paymentKey,
          order_id: orderId,
          amount: parseInt(amount),
        });

        if (result.success) {
          setStatus("success");
          setReceiptUrl(result.receipt_url);
          // Refresh user data to update credits/plan
          await refreshUser();
        } else {
          setStatus("error");
          setError(result.error || "결제 확인 중 오류가 발생했습니다.");
        }
      } catch (err: any) {
        setStatus("error");
        setError(err.response?.data?.detail || "결제 확인 중 오류가 발생했습니다.");
      }
    };

    confirmPayment();
  }, [searchParams, refreshUser]);

  if (status === "loading") {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-50">
        <Card className="w-full max-w-md">
          <CardContent className="p-8 text-center">
            <Loader2 className="mx-auto h-12 w-12 animate-spin text-samsung-blue" />
            <h2 className="mt-4 text-xl font-semibold text-gray-900">
              결제 확인 중...
            </h2>
            <p className="mt-2 text-gray-600">잠시만 기다려주세요.</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (status === "error") {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-50">
        <Card className="w-full max-w-md">
          <CardContent className="p-8 text-center">
            <AlertCircle className="mx-auto h-12 w-12 text-red-500" />
            <h2 className="mt-4 text-xl font-semibold text-gray-900">
              결제 실패
            </h2>
            <p className="mt-2 text-gray-600">{error}</p>
            <div className="mt-6 flex flex-col gap-2">
              <Button
                variant="samsung"
                onClick={() => router.push("/pricing")}
              >
                다시 시도하기
              </Button>
              <Button
                variant="outline"
                onClick={() => router.push("/create")}
              >
                홈으로 가기
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50">
      <Card className="w-full max-w-md">
        <CardContent className="p-8 text-center">
          <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-green-100">
            <CheckCircle className="h-10 w-10 text-green-600" />
          </div>
          <h2 className="mt-4 text-2xl font-bold text-gray-900">
            결제가 완료되었습니다!
          </h2>
          <p className="mt-2 text-gray-600">
            이제 더 많은 영상을 생성할 수 있습니다.
          </p>

          {receiptUrl && (
            <a
              href={receiptUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="mt-4 inline-block text-sm text-samsung-blue hover:underline"
            >
              영수증 보기
            </a>
          )}

          <div className="mt-8 flex flex-col gap-3">
            <Link href="/create">
              <Button variant="samsung" className="w-full">
                영상 만들기
              </Button>
            </Link>
            <Link href="/projects">
              <Button variant="outline" className="w-full">
                내 프로젝트 보기
              </Button>
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

export default function PaymentSuccessPage() {
  return (
    <Suspense fallback={<LoadingPage />}>
      <PaymentSuccessContent />
    </Suspense>
  );
}
