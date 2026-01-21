"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Header } from "@/components/common/Header";
import { Footer } from "@/components/common/Footer";
import {
  Check,
  Sparkles,
  Zap,
  Crown,
  Building2,
} from "lucide-react";
import { useAuth } from "@/stores/authStore";

const plans = [
  {
    id: "free",
    name: "무료",
    description: "AI 광고 영상 체험하기",
    price: 0,
    period: "영구 무료",
    credits: 3,
    icon: Sparkles,
    features: [
      "월 3회 영상 생성",
      "15초 영상",
      "720p 해상도",
      "워터마크 포함",
      "기본 템플릿 3종",
    ],
    limitations: [
      "AI 나레이션 미지원",
      "다국어 미지원",
    ],
    cta: "현재 플랜",
    popular: false,
  },
  {
    id: "basic",
    name: "Basic",
    description: "개인 크리에이터를 위한",
    price: 29000,
    period: "월",
    credits: 30,
    icon: Zap,
    features: [
      "월 30회 영상 생성",
      "30초 영상",
      "1080p 해상도",
      "워터마크 제거",
      "기본 템플릿 전체",
      "이메일 지원",
    ],
    limitations: [
      "AI 나레이션 미지원",
    ],
    cta: "시작하기",
    popular: false,
  },
  {
    id: "pro",
    name: "Pro",
    description: "전문 마케터를 위한",
    price: 79000,
    period: "월",
    credits: 100,
    icon: Crown,
    features: [
      "월 100회 영상 생성",
      "60초 영상",
      "4K 해상도",
      "프리미엄 템플릿 전체",
      "AI 나레이션 (한/영/중)",
      "다국어 스크립트",
      "A/B 테스트 (3버전)",
      "우선 지원",
    ],
    limitations: [],
    cta: "시작하기",
    popular: true,
  },
  {
    id: "enterprise",
    name: "Enterprise",
    description: "기업 고객을 위한",
    price: 290000,
    period: "월",
    credits: 999,
    icon: Building2,
    features: [
      "무제한 영상 생성",
      "120초 영상",
      "4K+ 해상도",
      "모든 템플릿 + 맞춤 제작",
      "전용 계정 관리자",
      "API 접근",
      "팀 협업 (무제한)",
      "맞춤 브랜딩",
      "SLA 보장",
    ],
    limitations: [],
    cta: "문의하기",
    popular: false,
  },
];

const creditPackages = [
  { credits: 10, price: 9900, name: "10 크레딧" },
  { credits: 30, price: 24900, name: "30 크레딧", discount: "17%" },
  { credits: 50, price: 39900, name: "50 크레딧", discount: "20%" },
  { credits: 100, price: 69900, name: "100 크레딧", discount: "30%" },
];

export default function PricingPage() {
  const router = useRouter();
  const { user, isAuthenticated } = useAuth();
  const [billingCycle, setBillingCycle] = useState<"monthly" | "yearly">("monthly");
  const [isLoading, setIsLoading] = useState<string | null>(null);

  const currentPlan = user?.plan || "free";

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat("ko-KR").format(price);
  };

  const getYearlyPrice = (monthlyPrice: number) => {
    return Math.round(monthlyPrice * 12 * 0.8);
  };

  const handleSelectPlan = async (planId: string) => {
    if (!isAuthenticated) {
      router.push(`/login?callbackUrl=/pricing&plan=${planId}`);
      return;
    }

    if (planId === "free" || planId === currentPlan) {
      return;
    }

    if (planId === "enterprise") {
      window.location.href = "mailto:enterprise@saiad.io?subject=Enterprise 플랜 문의";
      return;
    }

    setIsLoading(planId);

    try {
      // Navigate to checkout page
      router.push(`/checkout?plan=${planId}&cycle=${billingCycle}`);
    } catch (error) {
      console.error("Error:", error);
    } finally {
      setIsLoading(null);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />

      <main className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-900">
            당신에게 맞는 플랜을 선택하세요
          </h1>
          <p className="mt-4 text-xl text-gray-600">
            모든 플랜은 14일 무료 체험을 제공합니다
          </p>
        </div>

        {/* Billing Toggle */}
        <div className="mt-10 flex justify-center">
          <div className="inline-flex rounded-lg bg-gray-100 p-1">
            <button
              onClick={() => setBillingCycle("monthly")}
              className={cn(
                "rounded-md px-4 py-2 text-sm font-medium transition-colors",
                billingCycle === "monthly"
                  ? "bg-white text-gray-900 shadow"
                  : "text-gray-600 hover:text-gray-900"
              )}
            >
              월간 결제
            </button>
            <button
              onClick={() => setBillingCycle("yearly")}
              className={cn(
                "rounded-md px-4 py-2 text-sm font-medium transition-colors",
                billingCycle === "yearly"
                  ? "bg-white text-gray-900 shadow"
                  : "text-gray-600 hover:text-gray-900"
              )}
            >
              연간 결제
              <Badge className="ml-2 bg-green-100 text-green-700">20% 할인</Badge>
            </button>
          </div>
        </div>

        {/* Plans Grid */}
        <div className="mt-12 grid gap-6 lg:grid-cols-4">
          {plans.map((plan) => {
            const Icon = plan.icon;
            const isCurrentPlan = currentPlan === plan.id;
            const displayPrice =
              billingCycle === "yearly" && plan.price > 0
                ? getYearlyPrice(plan.price)
                : plan.price;

            return (
              <Card
                key={plan.id}
                className={cn(
                  "relative flex flex-col transition-all hover:shadow-lg",
                  plan.popular && "border-samsung-blue ring-2 ring-samsung-blue",
                  isCurrentPlan && "bg-blue-50"
                )}
              >
                {plan.popular && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                    <Badge className="bg-samsung-blue text-white">
                      가장 인기
                    </Badge>
                  </div>
                )}

                <CardHeader className="pb-4">
                  <div className="flex items-center gap-3">
                    <div
                      className={cn(
                        "flex h-10 w-10 items-center justify-center rounded-lg",
                        plan.popular
                          ? "bg-samsung-blue text-white"
                          : "bg-gray-100 text-gray-600"
                      )}
                    >
                      <Icon className="h-5 w-5" />
                    </div>
                    <div>
                      <CardTitle className="text-xl">{plan.name}</CardTitle>
                      <p className="text-sm text-gray-500">{plan.description}</p>
                    </div>
                  </div>
                </CardHeader>

                <CardContent className="flex flex-1 flex-col">
                  {/* Price */}
                  <div className="mb-6">
                    {plan.price === 0 ? (
                      <div className="text-3xl font-bold text-gray-900">무료</div>
                    ) : (
                      <>
                        <div className="flex items-baseline gap-1">
                          <span className="text-3xl font-bold text-gray-900">
                            ₩{formatPrice(displayPrice)}
                          </span>
                          <span className="text-gray-500">
                            /{billingCycle === "yearly" ? "년" : "월"}
                          </span>
                        </div>
                        {billingCycle === "yearly" && plan.price > 0 && (
                          <p className="mt-1 text-sm text-gray-500">
                            월 ₩{formatPrice(Math.round(displayPrice / 12))} (20% 할인)
                          </p>
                        )}
                      </>
                    )}
                    <p className="mt-2 text-sm text-samsung-blue font-medium">
                      월 {plan.credits}회 영상 생성
                    </p>
                  </div>

                  {/* Features */}
                  <ul className="mb-6 flex-1 space-y-3">
                    {plan.features.map((feature, index) => (
                      <li key={index} className="flex items-start gap-2 text-sm">
                        <Check className="mt-0.5 h-4 w-4 flex-shrink-0 text-green-500" />
                        <span className="text-gray-700">{feature}</span>
                      </li>
                    ))}
                    {plan.limitations.map((limitation, index) => (
                      <li
                        key={`limit-${index}`}
                        className="flex items-start gap-2 text-sm text-gray-400"
                      >
                        <span className="mt-0.5 h-4 w-4 flex-shrink-0 text-center">
                          -
                        </span>
                        <span>{limitation}</span>
                      </li>
                    ))}
                  </ul>

                  {/* CTA Button */}
                  <Button
                    variant={plan.popular ? "samsung" : "outline"}
                    className="w-full"
                    disabled={isCurrentPlan || isLoading === plan.id}
                    onClick={() => handleSelectPlan(plan.id)}
                  >
                    {isLoading === plan.id
                      ? "처리 중..."
                      : isCurrentPlan
                      ? "현재 플랜"
                      : plan.cta}
                  </Button>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* Credit Packages */}
        <div className="mt-20">
          <div className="text-center">
            <h2 className="text-2xl font-bold text-gray-900">
              크레딧 추가 구매
            </h2>
            <p className="mt-2 text-gray-600">
              구독 없이 필요할 때만 크레딧을 구매하세요
            </p>
          </div>

          <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {creditPackages.map((pkg, index) => (
              <Card
                key={index}
                className="cursor-pointer transition-all hover:border-samsung-blue hover:shadow-md"
                onClick={() => {
                  if (isAuthenticated) {
                    router.push(`/checkout?type=credits&package=${index}`);
                  } else {
                    router.push(`/login?callbackUrl=/pricing`);
                  }
                }}
              >
                <CardContent className="p-6 text-center">
                  <div className="text-3xl font-bold text-gray-900">
                    {pkg.credits}
                  </div>
                  <div className="mt-1 text-sm text-gray-500">크레딧</div>
                  <div className="mt-4 flex items-center justify-center gap-2">
                    <span className="text-xl font-semibold">
                      ₩{formatPrice(pkg.price)}
                    </span>
                    {pkg.discount && (
                      <Badge variant="secondary" className="bg-green-100 text-green-700">
                        {pkg.discount} 할인
                      </Badge>
                    )}
                  </div>
                  <div className="mt-1 text-xs text-gray-400">
                    크레딧당 ₩{formatPrice(Math.round(pkg.price / pkg.credits))}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* FAQ */}
        <div className="mt-20">
          <h2 className="text-center text-2xl font-bold text-gray-900">
            자주 묻는 질문
          </h2>

          <div className="mt-8 grid gap-6 lg:grid-cols-2">
            {[
              {
                q: "크레딧은 어떻게 사용되나요?",
                a: "영상 1개를 생성할 때마다 1 크레딧이 차감됩니다. 사용하지 않은 크레딧은 다음 달로 이월되지 않습니다.",
              },
              {
                q: "플랜을 변경할 수 있나요?",
                a: "언제든지 플랜을 업그레이드하거나 다운그레이드할 수 있습니다. 업그레이드 시 즉시 적용되며, 다운그레이드는 다음 결제일부터 적용됩니다.",
              },
              {
                q: "환불이 가능한가요?",
                a: "결제 후 7일 이내에 크레딧을 사용하지 않은 경우 전액 환불이 가능합니다. 크레딧을 일부라도 사용한 경우 환불이 불가합니다.",
              },
              {
                q: "Enterprise 플랜은 어떻게 신청하나요?",
                a: "Enterprise 플랜은 맞춤 견적이 필요합니다. '문의하기' 버튼을 클릭하여 담당자에게 연락해 주세요.",
              },
            ].map((faq, index) => (
              <Card key={index}>
                <CardContent className="p-6">
                  <h3 className="font-semibold text-gray-900">{faq.q}</h3>
                  <p className="mt-2 text-gray-600">{faq.a}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}
