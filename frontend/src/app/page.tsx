import Link from "next/link";
import { ArrowRight, Sparkles, Zap, Palette, Download } from "lucide-react";

export default function Home() {
  return (
    <main className="min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-samsung-blue via-samsung-blue to-blue-900 text-white">
        <div className="absolute inset-0 bg-[url('/grid.svg')] opacity-10" />
        <div className="relative mx-auto max-w-7xl px-4 py-24 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-4xl font-bold tracking-tight sm:text-6xl lg:text-7xl">
              삼성 제품 광고,
              <br />
              <span className="text-samsung-blue-light">5분이면 충분합니다</span>
            </h1>
            <p className="mx-auto mt-6 max-w-2xl text-lg text-gray-200 sm:text-xl">
              AI가 만드는 프로급 광고 영상. 제품을 선택하고, 템플릿을 고르면
              <br />
              나머지는 AI가 알아서 해드립니다.
            </p>
            <div className="mt-10 flex items-center justify-center gap-4">
              <Link
                href="/create"
                className="inline-flex items-center gap-2 rounded-full bg-white px-8 py-4 text-lg font-semibold text-samsung-blue transition-all hover:bg-gray-100 hover:scale-105"
              >
                무료로 시작하기
                <ArrowRight className="h-5 w-5" />
              </Link>
              <Link
                href="/examples"
                className="inline-flex items-center gap-2 rounded-full border-2 border-white/30 px-8 py-4 text-lg font-semibold text-white transition-all hover:bg-white/10"
              >
                예시 보기
              </Link>
            </div>
          </div>

          {/* Demo Video Placeholder */}
          <div className="mx-auto mt-16 max-w-4xl">
            <div className="aspect-video rounded-2xl bg-black/20 backdrop-blur-sm border border-white/10 flex items-center justify-center">
              <div className="text-center">
                <Sparkles className="mx-auto h-16 w-16 text-white/50" />
                <p className="mt-4 text-white/70">데모 영상</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-24 bg-gray-50">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h2 className="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
              왜 SaiAd인가요?
            </h2>
            <p className="mt-4 text-lg text-gray-600">
              삼성 제품에 최적화된 AI 영상 생성 플랫폼
            </p>
          </div>

          <div className="mt-16 grid gap-8 sm:grid-cols-2 lg:grid-cols-4">
            <FeatureCard
              icon={<Zap className="h-8 w-8" />}
              title="5분 완성"
              description="제품 선택부터 영상 완성까지 단 5분. 기다림 없이 바로 결과물을 확인하세요."
            />
            <FeatureCard
              icon={<Sparkles className="h-8 w-8" />}
              title="AI 스크립트"
              description="제품 특성에 맞는 광고 카피를 AI가 자동으로 생성합니다."
            />
            <FeatureCard
              icon={<Palette className="h-8 w-8" />}
              title="프로 템플릿"
              description="삼성 브랜드에 맞는 고품질 템플릿 12종을 무료로 제공합니다."
            />
            <FeatureCard
              icon={<Download className="h-8 w-8" />}
              title="다양한 포맷"
              description="유튜브, 인스타, 틱톡, 쿠팡까지 플랫폼별 최적화 영상 제공."
            />
          </div>
        </div>
      </section>

      {/* Product Categories */}
      <section className="py-24">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h2 className="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
              지원 제품 카테고리
            </h2>
            <p className="mt-4 text-lg text-gray-600">
              삼성전자 주요 제품군을 모두 지원합니다
            </p>
          </div>

          <div className="mt-16 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
            <CategoryCard
              emoji="📱"
              title="스마트폰"
              description="Galaxy S, Z Fold, Z Flip 시리즈"
              count={15}
            />
            <CategoryCard
              emoji="📺"
              title="TV"
              description="Neo QLED, OLED, The Frame"
              count={12}
            />
            <CategoryCard
              emoji="🏠"
              title="가전"
              description="비스포크 냉장고, 세탁기, 에어컨"
              count={18}
            />
            <CategoryCard
              emoji="⌚"
              title="웨어러블"
              description="Galaxy Watch, Buds, Ring"
              count={5}
            />
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section className="py-24 bg-gray-50">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h2 className="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
              심플한 요금제
            </h2>
            <p className="mt-4 text-lg text-gray-600">
              필요한 만큼만 사용하세요
            </p>
          </div>

          <div className="mt-16 grid gap-8 lg:grid-cols-3">
            <PricingCard
              name="Free"
              price="₩0"
              period="영원히 무료"
              features={[
                "월 3개 영상",
                "워터마크 포함",
                "720p 해상도",
                "기본 템플릿",
              ]}
            />
            <PricingCard
              name="Basic"
              price="₩19,900"
              period="/월"
              features={[
                "월 30개 영상",
                "워터마크 없음",
                "1080p 해상도",
                "모든 템플릿",
                "AI 나레이션",
              ]}
              highlighted
            />
            <PricingCard
              name="Pro"
              price="₩49,900"
              period="/월"
              features={[
                "월 100개 영상",
                "워터마크 없음",
                "4K 해상도",
                "모든 템플릿",
                "AI 나레이션",
                "A/B 테스트",
                "우선 지원",
              ]}
            />
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 bg-samsung-blue">
        <div className="mx-auto max-w-4xl px-4 text-center sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold tracking-tight text-white sm:text-4xl">
            지금 바로 시작하세요
          </h2>
          <p className="mt-4 text-lg text-blue-100">
            무료로 3개의 영상을 만들어보세요. 신용카드 필요 없습니다.
          </p>
          <Link
            href="/create"
            className="mt-8 inline-flex items-center gap-2 rounded-full bg-white px-8 py-4 text-lg font-semibold text-samsung-blue transition-all hover:bg-gray-100 hover:scale-105"
          >
            무료로 시작하기
            <ArrowRight className="h-5 w-5" />
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 py-12">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col items-center justify-between gap-4 sm:flex-row">
            <p className="text-gray-400">
              © 2025 SaiAd. All rights reserved.
            </p>
            <div className="flex gap-6">
              <Link href="/terms" className="text-gray-400 hover:text-white">
                이용약관
              </Link>
              <Link href="/privacy" className="text-gray-400 hover:text-white">
                개인정보처리방침
              </Link>
              <Link href="/contact" className="text-gray-400 hover:text-white">
                문의하기
              </Link>
            </div>
          </div>
        </div>
      </footer>
    </main>
  );
}

function FeatureCard({
  icon,
  title,
  description,
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
}) {
  return (
    <div className="rounded-2xl bg-white p-8 shadow-sm border border-gray-100 transition-all hover:shadow-md">
      <div className="inline-flex items-center justify-center rounded-xl bg-samsung-blue/10 p-3 text-samsung-blue">
        {icon}
      </div>
      <h3 className="mt-4 text-xl font-semibold text-gray-900">{title}</h3>
      <p className="mt-2 text-gray-600">{description}</p>
    </div>
  );
}

function CategoryCard({
  emoji,
  title,
  description,
  count,
}: {
  emoji: string;
  title: string;
  description: string;
  count: number;
}) {
  return (
    <Link
      href={`/create?category=${title.toLowerCase()}`}
      className="group rounded-2xl bg-white p-6 shadow-sm border border-gray-100 transition-all hover:shadow-md hover:border-samsung-blue/30"
    >
      <div className="text-4xl">{emoji}</div>
      <h3 className="mt-4 text-xl font-semibold text-gray-900 group-hover:text-samsung-blue">
        {title}
      </h3>
      <p className="mt-1 text-sm text-gray-600">{description}</p>
      <p className="mt-2 text-sm font-medium text-samsung-blue">
        {count}개 제품
      </p>
    </Link>
  );
}

function PricingCard({
  name,
  price,
  period,
  features,
  highlighted = false,
}: {
  name: string;
  price: string;
  period: string;
  features: string[];
  highlighted?: boolean;
}) {
  return (
    <div
      className={`rounded-2xl p-8 ${
        highlighted
          ? "bg-samsung-blue text-white ring-4 ring-samsung-blue/20 scale-105"
          : "bg-white border border-gray-200"
      }`}
    >
      <h3
        className={`text-lg font-semibold ${
          highlighted ? "text-blue-100" : "text-gray-600"
        }`}
      >
        {name}
      </h3>
      <div className="mt-4 flex items-baseline">
        <span className="text-4xl font-bold">{price}</span>
        <span
          className={`ml-1 ${highlighted ? "text-blue-100" : "text-gray-500"}`}
        >
          {period}
        </span>
      </div>
      <ul className="mt-8 space-y-4">
        {features.map((feature) => (
          <li key={feature} className="flex items-center gap-3">
            <svg
              className={`h-5 w-5 ${
                highlighted ? "text-blue-200" : "text-samsung-blue"
              }`}
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M5 13l4 4L19 7"
              />
            </svg>
            <span>{feature}</span>
          </li>
        ))}
      </ul>
      <button
        className={`mt-8 w-full rounded-full py-3 font-semibold transition-all ${
          highlighted
            ? "bg-white text-samsung-blue hover:bg-gray-100"
            : "bg-samsung-blue text-white hover:bg-samsung-blue/90"
        }`}
      >
        시작하기
      </button>
    </div>
  );
}
