"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useProjectStore } from "@/stores/projectStore";
import { ArrowLeft, ArrowRight, Play, Clock } from "lucide-react";
import type { Template } from "@/types";

// Mock templates
const mockTemplates: Template[] = [
  {
    id: "tpl_1",
    name: "언박싱 시퀀스",
    description: "제품 개봉의 설렘을 담은 프리미엄 언박싱 영상",
    category: "smartphone",
    style: "unboxing",
    durations: [15, 30, 60],
    thumbnail: "/templates/unboxing.jpg",
    preview_url: "/templates/unboxing-preview.mp4",
    is_premium: false,
  },
  {
    id: "tpl_2",
    name: "카메라 하이라이트",
    description: "카메라 성능을 극대화하는 시네마틱 영상",
    category: "smartphone",
    style: "feature",
    durations: [15, 30, 60],
    thumbnail: "/templates/camera.jpg",
    preview_url: "/templates/camera-preview.mp4",
    is_premium: false,
  },
  {
    id: "tpl_3",
    name: "일상 라이프스타일",
    description: "제품과 함께하는 일상을 자연스럽게 담은 영상",
    category: "smartphone",
    style: "lifestyle",
    durations: [15, 30, 60],
    thumbnail: "/templates/lifestyle.jpg",
    preview_url: "/templates/lifestyle-preview.mp4",
    is_premium: false,
  },
  {
    id: "tpl_4",
    name: "스펙 비교",
    description: "경쟁 제품과의 비교를 통한 강점 부각",
    category: "smartphone",
    style: "comparison",
    durations: [30, 60],
    thumbnail: "/templates/comparison.jpg",
    preview_url: "/templates/comparison-preview.mp4",
    is_premium: true,
  },
  {
    id: "tpl_5",
    name: "거실 시네마틱",
    description: "TV가 있는 거실의 프리미엄 분위기를 연출",
    category: "tv",
    style: "lifestyle",
    durations: [15, 30, 60],
    thumbnail: "/templates/living-room.jpg",
    preview_url: "/templates/living-preview.mp4",
    is_premium: false,
  },
  {
    id: "tpl_6",
    name: "게이밍 모드",
    description: "게이밍 TV의 성능을 극대화한 역동적인 영상",
    category: "tv",
    style: "gaming",
    durations: [15, 30],
    thumbnail: "/templates/gaming.jpg",
    preview_url: "/templates/gaming-preview.mp4",
    is_premium: false,
  },
  {
    id: "tpl_7",
    name: "비스포크 인테리어",
    description: "주방과 어우러지는 비스포크 가전의 아름다움",
    category: "appliance",
    style: "interior",
    durations: [15, 30, 60],
    thumbnail: "/templates/bespoke.jpg",
    preview_url: "/templates/bespoke-preview.mp4",
    is_premium: false,
  },
  {
    id: "tpl_8",
    name: "기능 시연",
    description: "제품의 핵심 기능을 명확하게 보여주는 영상",
    category: "appliance",
    style: "feature",
    durations: [30, 60],
    thumbnail: "/templates/demo.jpg",
    preview_url: "/templates/demo-preview.mp4",
    is_premium: false,
  },
  {
    id: "tpl_9",
    name: "헬스 트래킹",
    description: "건강 관리 기능을 중심으로 한 역동적인 영상",
    category: "wearable",
    style: "health",
    durations: [15, 30],
    thumbnail: "/templates/health.jpg",
    preview_url: "/templates/health-preview.mp4",
    is_premium: false,
  },
] as Template[];

const durationOptions = [
  { value: 15, label: "15초" },
  { value: 30, label: "30초" },
  { value: 60, label: "60초" },
];

export default function TemplateSelectionPage() {
  const router = useRouter();
  const { selectedProduct, customProductName, selectedTemplate, setTemplate, config, setConfig } =
    useProjectStore();

  const [selectedDuration, setSelectedDuration] = useState<number>(config.duration || 30);
  const [hoveredTemplate, setHoveredTemplate] = useState<string | null>(null);

  // Filter templates based on selected product category
  const productCategory = selectedProduct?.category || "smartphone";
  const relevantTemplates = mockTemplates.filter(
    (t) => t.category === productCategory || t.category === "smartphone" // fallback
  );

  const handleTemplateSelect = (template: Template) => {
    setTemplate(template);
    // Adjust duration if not available in selected template
    if (!template.durations.includes(selectedDuration)) {
      setSelectedDuration(template.durations[0]);
      setConfig({ duration: template.durations[0] as 15 | 30 | 60 });
    }
  };

  const handleDurationChange = (duration: number) => {
    setSelectedDuration(duration);
    setConfig({ duration: duration as 15 | 30 | 60 });
  };

  const handleNext = () => {
    router.push("/create/customize");
  };

  const handleBack = () => {
    router.push("/create/product");
  };

  const productName = selectedProduct?.name || customProductName || "제품";

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900">템플릿 선택</h1>
        <p className="mt-2 text-gray-600">
          <span className="font-medium text-samsung-blue">{productName}</span>에 어울리는 템플릿을
          선택하세요
        </p>
      </div>

      {/* Duration Selection */}
      <div className="flex items-center justify-center gap-2">
        <Clock className="h-5 w-5 text-gray-400" />
        <span className="text-sm text-gray-600">영상 길이:</span>
        <div className="flex gap-2">
          {durationOptions.map((option) => (
            <button
              key={option.value}
              onClick={() => handleDurationChange(option.value)}
              disabled={
                selectedTemplate && !selectedTemplate.durations.includes(option.value)
              }
              className={cn(
                "rounded-full px-4 py-1.5 text-sm font-medium transition-colors",
                selectedDuration === option.value
                  ? "bg-samsung-blue text-white"
                  : "bg-gray-100 text-gray-600 hover:bg-gray-200",
                selectedTemplate &&
                  !selectedTemplate.durations.includes(option.value) &&
                  "cursor-not-allowed opacity-50"
              )}
            >
              {option.label}
            </button>
          ))}
        </div>
      </div>

      {/* Template Grid */}
      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {relevantTemplates.map((template) => (
          <Card
            key={template.id}
            className={cn(
              "cursor-pointer overflow-hidden transition-all hover:shadow-lg",
              selectedTemplate?.id === template.id && "ring-2 ring-samsung-blue"
            )}
            onClick={() => handleTemplateSelect(template)}
            onMouseEnter={() => setHoveredTemplate(template.id)}
            onMouseLeave={() => setHoveredTemplate(null)}
          >
            {/* Preview Area */}
            <div className="relative aspect-video bg-gradient-to-br from-gray-800 to-gray-900">
              {/* Template style icon as placeholder */}
              <div className="absolute inset-0 flex items-center justify-center text-white/20">
                <span className="text-6xl">
                  {template.style === "unboxing" && "📦"}
                  {template.style === "feature" && "✨"}
                  {template.style === "lifestyle" && "🌟"}
                  {template.style === "comparison" && "⚖️"}
                  {template.style === "gaming" && "🎮"}
                  {template.style === "interior" && "🏠"}
                  {template.style === "health" && "💪"}
                </span>
              </div>

              {/* Play overlay on hover */}
              {hoveredTemplate === template.id && (
                <div className="absolute inset-0 flex items-center justify-center bg-black/40">
                  <div className="rounded-full bg-white/90 p-3">
                    <Play className="h-6 w-6 text-samsung-blue" fill="currentColor" />
                  </div>
                </div>
              )}

              {/* Badges */}
              <div className="absolute left-2 top-2 flex gap-2">
                {selectedTemplate?.id === template.id && (
                  <Badge variant="default">선택됨</Badge>
                )}
                {template.is_premium && (
                  <Badge variant="warning">Premium</Badge>
                )}
              </div>

              {/* Duration badges */}
              <div className="absolute bottom-2 right-2 flex gap-1">
                {template.durations.map((d) => (
                  <span
                    key={d}
                    className="rounded bg-black/60 px-1.5 py-0.5 text-xs text-white"
                  >
                    {d}초
                  </span>
                ))}
              </div>
            </div>

            {/* Info */}
            <div className="p-4">
              <h3 className="font-semibold text-gray-900">{template.name}</h3>
              <p className="mt-1 text-sm text-gray-500">{template.description}</p>
            </div>
          </Card>
        ))}
      </div>

      {/* Bottom Actions */}
      <div className="flex justify-between border-t pt-6">
        <Button variant="outline" size="lg" onClick={handleBack}>
          <ArrowLeft className="mr-2 h-5 w-5" />
          이전 단계
        </Button>
        <Button
          variant="samsung"
          size="lg"
          disabled={!selectedTemplate}
          onClick={handleNext}
        >
          다음 단계
          <ArrowRight className="ml-2 h-5 w-5" />
        </Button>
      </div>
    </div>
  );
}
