"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { useProjectStore } from "@/stores/projectStore";
import {
  ArrowLeft,
  Download,
  Share2,
  RefreshCw,
  Play,
  Pause,
  Check,
  Loader2,
  Youtube,
  Instagram,
  Video,
  ShoppingBag,
  Copy,
  ExternalLink,
} from "lucide-react";

type GenerationStep = {
  id: string;
  name: string;
  status: "pending" | "in_progress" | "completed";
};

const initialSteps: GenerationStep[] = [
  { id: "script", name: "스크립트 처리", status: "pending" },
  { id: "image", name: "이미지 처리", status: "pending" },
  { id: "video", name: "영상 생성", status: "pending" },
  { id: "composite", name: "영상 합성", status: "pending" },
  { id: "audio", name: "오디오 믹싱", status: "pending" },
];

const downloadFormats = [
  { id: "youtube", name: "유튜브", icon: Youtube, ratio: "16:9", resolution: "1080p" },
  { id: "instagram", name: "인스타 릴스", icon: Instagram, ratio: "9:16", resolution: "1080p" },
  { id: "tiktok", name: "틱톡", icon: Video, ratio: "9:16", resolution: "1080p" },
  { id: "coupang", name: "쿠팡 상세", icon: ShoppingBag, ratio: "1:1", resolution: "720p" },
];

export default function ResultPage() {
  const router = useRouter();
  const { selectedProduct, customProductName, selectedTemplate, config, script, reset } =
    useProjectStore();

  const [isGenerating, setIsGenerating] = useState(true);
  const [progress, setProgress] = useState(0);
  const [steps, setSteps] = useState<GenerationStep[]>(initialSteps);
  const [isPlaying, setIsPlaying] = useState(false);
  const [generatedVideoUrl, setGeneratedVideoUrl] = useState<string | null>(null);

  const productName = selectedProduct?.name || customProductName || "제품";

  // Simulate video generation
  useEffect(() => {
    if (!isGenerating) return;

    const stepDurations = [1000, 1500, 3000, 2000, 1500]; // ms for each step
    const totalDuration = stepDurations.reduce((a, b) => a + b, 0);

    const updateProgress = () => {
      let elapsed = 0;
      stepDurations.forEach((duration, index) => {
        setTimeout(() => {
          setSteps((prev) =>
            prev.map((step, i) => ({
              ...step,
              status: i < index ? "completed" : i === index ? "in_progress" : "pending",
            }))
          );
        }, elapsed);
        elapsed += duration;
      });

      // Final completion
      setTimeout(() => {
        setSteps((prev) => prev.map((step) => ({ ...step, status: "completed" })));
        setIsGenerating(false);
        setGeneratedVideoUrl("/demo-video.mp4"); // Mock URL
      }, totalDuration);
    };

    // Progress bar animation
    const progressInterval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 100) {
          clearInterval(progressInterval);
          return 100;
        }
        return prev + 1;
      });
    }, totalDuration / 100);

    updateProgress();

    return () => {
      clearInterval(progressInterval);
    };
  }, [isGenerating]);

  const handleDownload = (format: string) => {
    // In production, this would call the API to get a signed download URL
    console.log(`Downloading ${format} format`);
    alert(`${format} 형식으로 다운로드를 시작합니다.`);
  };

  const handleShare = () => {
    if (navigator.share) {
      navigator.share({
        title: `${productName} 광고 영상`,
        text: `SaiAd로 만든 ${productName} 광고 영상을 확인해보세요!`,
        url: window.location.href,
      });
    } else {
      navigator.clipboard.writeText(window.location.href);
      alert("링크가 복사되었습니다.");
    }
  };

  const handleCreateAnother = () => {
    reset();
    router.push("/create/product");
  };

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900">
          {isGenerating ? "영상 생성 중..." : "영상 완성!"}
        </h1>
        <p className="mt-2 text-gray-600">
          {isGenerating
            ? "잠시만 기다려주세요. AI가 영상을 만들고 있습니다."
            : `${productName} 광고 영상이 준비되었습니다.`}
        </p>
      </div>

      <div className="grid gap-8 lg:grid-cols-3">
        {/* Video Preview */}
        <div className="lg:col-span-2">
          <Card>
            <CardContent className="p-0">
              <div className="relative aspect-video overflow-hidden rounded-t-xl bg-gradient-to-br from-gray-800 to-gray-900">
                {isGenerating ? (
                  // Generation Progress View
                  <div className="absolute inset-0 flex flex-col items-center justify-center p-8">
                    <Loader2 className="h-12 w-12 animate-spin text-samsung-blue" />
                    <p className="mt-4 text-lg font-medium text-white">영상 생성 중...</p>
                    <div className="mt-4 w-full max-w-xs">
                      <Progress value={progress} showLabel />
                    </div>
                  </div>
                ) : (
                  // Completed Video View
                  <div className="absolute inset-0 flex flex-col items-center justify-center p-8 text-center text-white">
                    <h2 className="text-2xl font-bold">{script?.headline || productName}</h2>
                    <p className="mt-2 text-lg text-gray-300">{script?.subline}</p>
                    <button
                      onClick={() => setIsPlaying(!isPlaying)}
                      className="mt-6 rounded-full bg-white/20 p-4 transition-all hover:bg-white/30"
                    >
                      {isPlaying ? (
                        <Pause className="h-8 w-8 text-white" />
                      ) : (
                        <Play className="h-8 w-8 text-white" fill="white" />
                      )}
                    </button>
                  </div>
                )}
              </div>

              {/* Video Info Bar */}
              <div className="flex items-center justify-between border-t bg-gray-50 p-4">
                <div className="flex items-center gap-4">
                  <Badge>{config.duration}초</Badge>
                  <span className="text-sm text-gray-500">
                    {selectedTemplate?.name || "템플릿"}
                  </span>
                </div>
                {!isGenerating && (
                  <div className="flex items-center gap-2">
                    <Button variant="outline" size="sm" onClick={handleShare}>
                      <Share2 className="mr-2 h-4 w-4" />
                      공유
                    </Button>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Generation Status */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">생성 상태</CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-3">
                {steps.map((step) => (
                  <li key={step.id} className="flex items-center gap-3">
                    <div
                      className={cn(
                        "flex h-6 w-6 items-center justify-center rounded-full",
                        step.status === "completed"
                          ? "bg-green-500 text-white"
                          : step.status === "in_progress"
                          ? "bg-samsung-blue text-white"
                          : "bg-gray-200 text-gray-400"
                      )}
                    >
                      {step.status === "completed" ? (
                        <Check className="h-4 w-4" />
                      ) : step.status === "in_progress" ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        <span className="text-xs">○</span>
                      )}
                    </div>
                    <span
                      className={cn(
                        "text-sm",
                        step.status === "completed"
                          ? "text-gray-900"
                          : step.status === "in_progress"
                          ? "font-medium text-samsung-blue"
                          : "text-gray-400"
                      )}
                    >
                      {step.name}
                    </span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>

          {/* Download Options */}
          {!isGenerating && (
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">다운로드</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                {downloadFormats.map((format) => (
                  <button
                    key={format.id}
                    onClick={() => handleDownload(format.id)}
                    className="flex w-full items-center justify-between rounded-lg border p-3 transition-all hover:border-samsung-blue hover:bg-samsung-blue/5"
                  >
                    <div className="flex items-center gap-3">
                      <format.icon className="h-5 w-5 text-gray-600" />
                      <div className="text-left">
                        <p className="font-medium">{format.name}</p>
                        <p className="text-xs text-gray-500">
                          {format.ratio} · {format.resolution}
                        </p>
                      </div>
                    </div>
                    <Download className="h-4 w-4 text-gray-400" />
                  </button>
                ))}
              </CardContent>
            </Card>
          )}

          {/* Project Summary */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">프로젝트 정보</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-500">제품</span>
                <span className="font-medium">{productName}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">템플릿</span>
                <span className="font-medium">{selectedTemplate?.name || "-"}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">톤앤매너</span>
                <span className="font-medium">
                  {config.tone === "premium"
                    ? "프리미엄"
                    : config.tone === "practical"
                    ? "실용적"
                    : "MZ"}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">영상 길이</span>
                <span className="font-medium">{config.duration}초</span>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Bottom Actions */}
      <div className="flex flex-col gap-4 border-t pt-6 sm:flex-row sm:justify-between">
        <Button variant="outline" size="lg" onClick={() => router.push("/create/customize")}>
          <ArrowLeft className="mr-2 h-5 w-5" />
          수정하기
        </Button>
        <div className="flex gap-4">
          <Button variant="outline" size="lg" onClick={handleCreateAnother}>
            <RefreshCw className="mr-2 h-5 w-5" />
            새 영상 만들기
          </Button>
          <Link href="/projects">
            <Button variant="samsung" size="lg">
              내 프로젝트로 이동
              <ExternalLink className="ml-2 h-5 w-5" />
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
}
