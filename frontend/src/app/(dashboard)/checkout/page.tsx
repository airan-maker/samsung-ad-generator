"use client";

import { useEffect, useState, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Header } from "@/components/common/Header";
import { LoadingPage } from "@/components/common/Loading";
import {
  ArrowLeft,
  CreditCard,
  Lock,
  Check,
  AlertCircle,
} from "lucide-react";
import { useAuth } from "@/stores/authStore";
import { api } from "@/lib/api";

const plans: Record<string, { name: string; price: number; credits: number }> = {
  basic: { name: "Basic", price: 29000, credits: 30 },
  pro: { name: "Pro", price: 79000, credits: 100 },
  enterprise: { name: "Enterprise", price: 290000, credits: 999 },
};

const creditPackages = [
  { credits: 10, price: 9900, name: "10 크레딧" },
  { credits: 30, price: 24900, name: "30 크레딧" },
  { credits: 50, price: 39900, name: "50 크레딧" },
  { credits: 100, price: 69900, name: "100 크레딧" },
];

function CheckoutContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { user, isAuthenticated } = useAuth();

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Get checkout type and details from URL
  const type = searchParams.get("type") || "subscription";
  const planId = searchParams.get("plan");
  const cycle = searchParams.get("cycle") || "monthly";
  const packageIndex = parseInt(searchParams.get("package") || "0");

  // Calculate order details
  const isCredits = type === "credits";
  let orderName = "";
  let amount = 0;
  let credits = 0;

  if (isCredits) {
    const pkg = creditPackages[packageIndex] || creditPackages[0];
    orderName = pkg.name;
    amount = pkg.price;
    credits = pkg.credits;
  } else if (planId && plans[planId]) {
    const plan = plans[planId];
    orderName = `SaiAD ${plan.name} (${cycle === "yearly" ? "연간" : "월간"})`;
    amount = cycle === "yearly" ? Math.round(plan.price * 12 * 0.8) : plan.price;
    credits = plan.credits;
  }

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat("ko-KR").format(price);
  };

  useEffect(() => {
    if (!isAuthenticated) {
      router.push("/login?callbackUrl=" + encodeURIComponent(window.location.pathname + window.location.search));
    }
  }, [isAuthenticated, router]);

  const handlePayment = async () => {
    setIsLoading(true);
    setError(null);

    try {
      // Create checkout session
      interface CheckoutResponse {
        client_key: string;
        amount: number;
        order_id: string;
        order_name: string;
        success_url: string;
        fail_url: string;
      }

      let checkoutData: CheckoutResponse;
      if (isCredits) {
        checkoutData = await api.post<CheckoutResponse>("/payments/checkout/credits", {
          package_index: packageIndex,
        });
      } else {
        checkoutData = await api.post<CheckoutResponse>("/payments/checkout", {
          plan: planId,
          billing_cycle: cycle,
        });
      }

      // Load Toss Payments SDK
      const tossPayments = await loadTossPayments(checkoutData.client_key);

      // Request payment
      await tossPayments.requestPayment("카드", {
        amount: checkoutData.amount,
        orderId: checkoutData.order_id,
        orderName: checkoutData.order_name,
        customerName: user?.name || "고객",
        customerEmail: user?.email,
        successUrl: checkoutData.success_url,
        failUrl: checkoutData.fail_url,
      });
    } catch (err: any) {
      console.error("Payment error:", err);
      setError(err.message || "결제 중 오류가 발생했습니다.");
    } finally {
      setIsLoading(false);
    }
  };

  if (!planId && !isCredits) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <Card className="w-full max-w-md">
          <CardContent className="p-6 text-center">
            <AlertCircle className="mx-auto h-12 w-12 text-red-500" />
            <h2 className="mt-4 text-xl font-semibold">잘못된 접근입니다</h2>
            <p className="mt-2 text-gray-600">플랜을 선택해주세요.</p>
            <Button
              variant="samsung"
              className="mt-4"
              onClick={() => router.push("/pricing")}
            >
              플랜 보기
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />

      <main className="mx-auto max-w-4xl px-4 py-8 sm:px-6 lg:px-8">
        {/* Back */}
        <button
          onClick={() => router.back()}
          className="mb-6 flex items-center text-sm text-gray-600 hover:text-samsung-blue"
        >
          <ArrowLeft className="mr-2 h-4 w-4" />
          뒤로 가기
        </button>

        <div className="grid gap-8 lg:grid-cols-2">
          {/* Order Summary */}
          <div>
            <Card>
              <CardHeader>
                <CardTitle>주문 요약</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="rounded-lg bg-gray-50 p-4">
                  <h3 className="font-semibold text-gray-900">{orderName}</h3>
                  {!isCredits && (
                    <p className="mt-1 text-sm text-gray-600">
                      월 {credits}회 영상 생성
                    </p>
                  )}
                  {isCredits && (
                    <p className="mt-1 text-sm text-gray-600">
                      {credits} 크레딧 추가
                    </p>
                  )}
                </div>

                <div className="space-y-2 border-t pt-4">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">상품 금액</span>
                    <span>₩{formatPrice(amount)}</span>
                  </div>
                  {cycle === "yearly" && !isCredits && (
                    <div className="flex justify-between text-sm text-green-600">
                      <span>연간 결제 할인 (20%)</span>
                      <span>
                        -₩{formatPrice(Math.round((plans[planId!]?.price || 0) * 12 * 0.2))}
                      </span>
                    </div>
                  )}
                  <div className="flex justify-between border-t pt-2 text-lg font-semibold">
                    <span>총 결제 금액</span>
                    <span className="text-samsung-blue">₩{formatPrice(amount)}</span>
                  </div>
                </div>

                {/* Features */}
                {!isCredits && planId && (
                  <div className="border-t pt-4">
                    <h4 className="text-sm font-medium text-gray-900">포함된 기능</h4>
                    <ul className="mt-2 space-y-2">
                      {[
                        `월 ${credits}회 영상 생성`,
                        "HD 이상 해상도",
                        "워터마크 제거",
                        planId === "pro" && "AI 나레이션",
                        planId === "pro" && "다국어 지원",
                      ]
                        .filter(Boolean)
                        .map((feature, i) => (
                          <li key={i} className="flex items-center gap-2 text-sm text-gray-600">
                            <Check className="h-4 w-4 text-green-500" />
                            {feature}
                          </li>
                        ))}
                    </ul>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Security Notice */}
            <div className="mt-4 flex items-start gap-2 text-sm text-gray-500">
              <Lock className="mt-0.5 h-4 w-4 flex-shrink-0" />
              <p>
                모든 결제 정보는 SSL 암호화되어 안전하게 처리됩니다.
                토스페이먼츠를 통해 안전하게 결제할 수 있습니다.
              </p>
            </div>
          </div>

          {/* Payment Form */}
          <div>
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <CreditCard className="h-5 w-5" />
                  결제 정보
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Billing Info */}
                <div className="space-y-4">
                  <div>
                    <label className="text-sm font-medium text-gray-700">
                      이메일
                    </label>
                    <Input
                      type="email"
                      value={user?.email || ""}
                      disabled
                      className="mt-1 bg-gray-50"
                    />
                    <p className="mt-1 text-xs text-gray-500">
                      영수증이 이 이메일로 발송됩니다
                    </p>
                  </div>
                </div>

                {error && (
                  <div className="rounded-lg bg-red-50 p-3 text-sm text-red-600">
                    {error}
                  </div>
                )}

                {/* Payment Button */}
                <Button
                  variant="samsung"
                  className="w-full"
                  size="lg"
                  onClick={handlePayment}
                  disabled={isLoading}
                >
                  {isLoading ? (
                    "처리 중..."
                  ) : (
                    <>₩{formatPrice(amount)} 결제하기</>
                  )}
                </Button>

                {/* Terms */}
                <p className="text-center text-xs text-gray-500">
                  결제를 진행하면{" "}
                  <a href="/terms" className="text-samsung-blue hover:underline">
                    이용약관
                  </a>
                  과{" "}
                  <a href="/privacy" className="text-samsung-blue hover:underline">
                    개인정보처리방침
                  </a>
                  에 동의하는 것으로 간주됩니다.
                </p>

                {!isCredits && (
                  <p className="text-center text-xs text-gray-500">
                    구독은 {cycle === "yearly" ? "매년" : "매월"} 자동 갱신됩니다.
                    언제든지 취소할 수 있습니다.
                  </p>
                )}
              </CardContent>
            </Card>

            {/* Payment Methods */}
            <div className="mt-4 flex items-center justify-center gap-4">
              <img
                src="/images/payment/visa.svg"
                alt="Visa"
                className="h-6 opacity-50"
              />
              <img
                src="/images/payment/mastercard.svg"
                alt="Mastercard"
                className="h-6 opacity-50"
              />
              <img
                src="/images/payment/toss.svg"
                alt="Toss"
                className="h-6 opacity-50"
              />
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

// Toss Payments SDK loader
declare global {
  interface Window {
    TossPayments: any;
  }
}

async function loadTossPayments(clientKey: string): Promise<any> {
  return new Promise((resolve, reject) => {
    if (window.TossPayments) {
      resolve(window.TossPayments(clientKey));
      return;
    }

    const script = document.createElement("script");
    script.src = "https://js.tosspayments.com/v1/payment";
    script.onload = () => {
      if (window.TossPayments) {
        resolve(window.TossPayments(clientKey));
      } else {
        reject(new Error("Failed to load Toss Payments SDK"));
      }
    };
    script.onerror = () => reject(new Error("Failed to load Toss Payments SDK"));
    document.head.appendChild(script);
  });
}

export default function CheckoutPage() {
  return (
    <Suspense fallback={<LoadingPage />}>
      <CheckoutContent />
    </Suspense>
  );
}
