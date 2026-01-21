"use client";

import { Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { LoadingPage } from "@/components/common/Loading";
import { XCircle, HelpCircle } from "lucide-react";

function PaymentFailContent() {
  const router = useRouter();
  const searchParams = useSearchParams();

  const errorCode = searchParams.get("code");
  const errorMessage = searchParams.get("message");
  const orderId = searchParams.get("orderId");

  // Common error messages
  const errorMessages: Record<string, string> = {
    PAY_PROCESS_CANCELED: "결제가 취소되었습니다.",
    PAY_PROCESS_ABORTED: "결제 진행 중 오류가 발생했습니다.",
    REJECT_CARD_COMPANY: "카드사에서 결제를 거절했습니다.",
    INVALID_CARD_EXPIRATION: "카드 유효기간이 올바르지 않습니다.",
    INVALID_STOPPED_CARD: "정지된 카드입니다.",
    EXCEED_MAX_DAILY_PAYMENT_COUNT: "일일 결제 한도를 초과했습니다.",
    EXCEED_MAX_PAYMENT_AMOUNT: "결제 금액 한도를 초과했습니다.",
    NOT_SUPPORTED_INSTALLMENT_PLAN_CARD_OR_MERCHANT: "할부 결제가 지원되지 않습니다.",
  };

  const displayMessage = errorCode && errorMessages[errorCode]
    ? errorMessages[errorCode]
    : errorMessage || "결제 중 오류가 발생했습니다.";

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50">
      <Card className="w-full max-w-md">
        <CardContent className="p-8 text-center">
          <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-red-100">
            <XCircle className="h-10 w-10 text-red-600" />
          </div>
          <h2 className="mt-4 text-2xl font-bold text-gray-900">
            결제에 실패했습니다
          </h2>
          <p className="mt-2 text-gray-600">{displayMessage}</p>

          {errorCode && (
            <p className="mt-2 text-sm text-gray-400">
              오류 코드: {errorCode}
            </p>
          )}

          <div className="mt-8 flex flex-col gap-3">
            <Button
              variant="samsung"
              className="w-full"
              onClick={() => router.back()}
            >
              다시 시도하기
            </Button>
            <Link href="/pricing">
              <Button variant="outline" className="w-full">
                플랜 페이지로 돌아가기
              </Button>
            </Link>
          </div>

          {/* Help */}
          <div className="mt-8 rounded-lg bg-gray-50 p-4">
            <div className="flex items-start gap-3 text-left">
              <HelpCircle className="mt-0.5 h-5 w-5 flex-shrink-0 text-gray-400" />
              <div>
                <p className="text-sm font-medium text-gray-700">
                  결제에 문제가 있으신가요?
                </p>
                <p className="mt-1 text-sm text-gray-500">
                  다른 결제 수단을 사용하시거나, 카드사에 문의해 주세요.
                  계속 문제가 발생하면{" "}
                  <a
                    href="mailto:support@saiad.io"
                    className="text-samsung-blue hover:underline"
                  >
                    고객센터
                  </a>
                  로 연락해 주세요.
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

export default function PaymentFailPage() {
  return (
    <Suspense fallback={<LoadingPage />}>
      <PaymentFailContent />
    </Suspense>
  );
}
