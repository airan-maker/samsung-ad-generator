"use client";

import { Suspense, useState, useEffect } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { ArrowLeft, Save, Eye, Download, Share2 } from "lucide-react";
import { TemplateCustomizer, TemplateConfig } from "@/components/templates/TemplateCustomizer";
import { LoadingPage } from "@/components/common/Loading";

interface Template {
  id: string;
  name: string;
  description: string;
  thumbnail: string;
  category: string;
  duration: number;
  aspectRatio: string;
}

// Mock template data
const mockTemplates: Record<string, Template> = {
  "1": {
    id: "1",
    name: "Galaxy S 시리즈 프리미엄",
    description: "Galaxy S 시리즈를 위한 프리미엄 광고 템플릿",
    thumbnail: "/templates/galaxy-s.jpg",
    category: "smartphone",
    duration: 30,
    aspectRatio: "16:9",
  },
  "2": {
    id: "2",
    name: "가전제품 라이프스타일",
    description: "삼성 가전제품을 위한 라이프스타일 템플릿",
    thumbnail: "/templates/appliance.jpg",
    category: "appliance",
    duration: 15,
    aspectRatio: "9:16",
  },
  "3": {
    id: "3",
    name: "B2B 기업 솔루션",
    description: "기업용 솔루션 홍보를 위한 전문적인 템플릿",
    thumbnail: "/templates/b2b.jpg",
    category: "b2b",
    duration: 60,
    aspectRatio: "16:9",
  },
};

function TemplateCustomizeContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const templateId = searchParams.get("id") || "1";

  const [template, setTemplate] = useState<Template | null>(null);
  const [config, setConfig] = useState<TemplateConfig | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [showPreview, setShowPreview] = useState(false);

  useEffect(() => {
    // Load template data
    const templateData = mockTemplates[templateId];
    if (templateData) {
      setTemplate(templateData);
    }
  }, [templateId]);

  const handleConfigChange = (newConfig: TemplateConfig) => {
    setConfig(newConfig);
  };

  const handleSave = async () => {
    if (!config) return;

    setIsSaving(true);
    try {
      // API call to save template configuration
      const response = await fetch(`/api/v1/templates/${templateId}/customize`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(config),
      });

      if (response.ok) {
        // Show success notification
        alert("템플릿 설정이 저장되었습니다.");
      }
    } catch (error) {
      console.error("Failed to save template config:", error);
      alert("저장 중 오류가 발생했습니다.");
    } finally {
      setIsSaving(false);
    }
  };

  const handleExport = () => {
    if (!config) return;

    const dataStr = JSON.stringify(config, null, 2);
    const dataBlob = new Blob([dataStr], { type: "application/json" });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `template-config-${templateId}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const handleShare = async () => {
    if (!config) return;

    try {
      // Create shareable link
      const response = await fetch(`/api/v1/templates/${templateId}/share`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(config),
      });

      if (response.ok) {
        const data = await response.json();
        await navigator.clipboard.writeText(data.shareUrl);
        alert("공유 링크가 클립보드에 복사되었습니다.");
      }
    } catch (error) {
      console.error("Failed to create share link:", error);
    }
  };

  if (!template) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-samsung-blue border-t-transparent"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="sticky top-0 z-40 border-b bg-white">
        <div className="flex h-16 items-center justify-between px-6">
          <div className="flex items-center gap-4">
            <button
              onClick={() => router.back()}
              className="flex items-center gap-2 text-gray-600 hover:text-gray-900"
            >
              <ArrowLeft className="h-5 w-5" />
              <span className="hidden sm:inline">돌아가기</span>
            </button>
            <div className="h-6 w-px bg-gray-200" />
            <div>
              <h1 className="font-semibold text-gray-900">{template.name}</h1>
              <p className="text-sm text-gray-500">템플릿 커스터마이징</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => setShowPreview(!showPreview)}
              className={`flex items-center gap-2 rounded-lg border px-4 py-2 text-sm font-medium transition-colors ${
                showPreview
                  ? "border-samsung-blue bg-samsung-blue text-white"
                  : "border-gray-200 bg-white text-gray-700 hover:bg-gray-50"
              }`}
            >
              <Eye className="h-4 w-4" />
              미리보기
            </button>

            <button
              onClick={handleExport}
              className="flex items-center gap-2 rounded-lg border border-gray-200 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              <Download className="h-4 w-4" />
              내보내기
            </button>

            <button
              onClick={handleShare}
              className="flex items-center gap-2 rounded-lg border border-gray-200 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              <Share2 className="h-4 w-4" />
              공유
            </button>

            <button
              onClick={handleSave}
              disabled={isSaving}
              className="flex items-center gap-2 rounded-lg bg-samsung-blue px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
            >
              <Save className="h-4 w-4" />
              {isSaving ? "저장 중..." : "저장"}
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex">
        {/* Customizer Panel */}
        <div className={`transition-all duration-300 ${showPreview ? "w-1/2" : "w-full"}`}>
          <TemplateCustomizer
            templateId={templateId}
            initialConfig={config || undefined}
            onConfigChange={handleConfigChange}
            onSave={handleSave}
          />
        </div>

        {/* Preview Panel */}
        {showPreview && (
          <div className="w-1/2 border-l bg-gray-900 p-6">
            <div className="sticky top-24">
              <h3 className="mb-4 text-lg font-semibold text-white">실시간 미리보기</h3>
              <div
                className="relative mx-auto overflow-hidden rounded-lg bg-black"
                style={{
                  aspectRatio: template.aspectRatio === "9:16" ? "9/16" : "16/9",
                  maxHeight: "70vh",
                }}
              >
                {/* Preview Canvas */}
                <div
                  className="absolute inset-0 flex items-center justify-center"
                  style={{
                    backgroundColor: config?.colors?.background || "#000000",
                  }}
                >
                  {/* Sample preview content */}
                  <div className="p-8 text-center">
                    <h2
                      className="mb-4 text-3xl font-bold"
                      style={{
                        color: config?.colors?.primary || "#1428A0",
                        fontFamily: config?.typography?.headlineFont || "Samsung Sharp Sans",
                      }}
                    >
                      Galaxy S25 Ultra
                    </h2>
                    <p
                      className="text-lg"
                      style={{
                        color: config?.colors?.text || "#FFFFFF",
                        fontFamily: config?.typography?.bodyFont || "Samsung One",
                      }}
                    >
                      혁신의 새로운 기준
                    </p>

                    {config?.branding?.showLogo && (
                      <div className="mt-8">
                        {/* eslint-disable-next-line @next/next/no-img-element */}
                        <img
                          src="/samsung-logo-white.png"
                          alt="Samsung"
                          className="mx-auto h-8"
                          style={{ opacity: 1 }}
                        />
                      </div>
                    )}
                  </div>

                  {/* Animation preview overlay */}
                  {config?.effects?.animation && (
                    <div className="pointer-events-none absolute inset-0 bg-gradient-to-t from-transparent via-transparent to-white/5" />
                  )}
                </div>

                {/* Duration indicator */}
                <div className="absolute bottom-4 left-4 rounded bg-black/50 px-2 py-1 text-xs text-white">
                  {template.duration}초
                </div>
              </div>

              {/* Preview controls */}
              <div className="mt-4 flex justify-center gap-4">
                <button className="rounded-lg bg-white/10 px-4 py-2 text-sm text-white hover:bg-white/20">
                  처음부터 재생
                </button>
                <button className="rounded-lg bg-white/10 px-4 py-2 text-sm text-white hover:bg-white/20">
                  전체 화면
                </button>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default function TemplateCustomizePage() {
  return (
    <Suspense fallback={<LoadingPage />}>
      <TemplateCustomizeContent />
    </Suspense>
  );
}
